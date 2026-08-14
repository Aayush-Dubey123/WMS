"""
chatbot_controller.py — WMS-adapted Chatbot Controller (SDK-migrated final).

Integrates Google Gemini LLM with WMS domain knowledge.
- System prompt covers Whitfield WMS SOPs and operations
- Tool declarations wire to existing WMS controllers/CRUDs
- Auth: reuses commons/auth.py; respects role + facility scope
- Audit questions routed through existing audit_log collection

READ-ONLY operations only—all writes go through validated endpoints.
Unknown answers → say so, never invent stock numbers.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException, status

from core import logger
from core.cruds.wms_crud import CRUDChat

logging = logger(__name__)

# Load .env from backend root.
# This file lives at: backend/core/controllers/chatbot_controller.py
# .env lives at:      backend/.env  → three parents up, not two.
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=str(_env_path), override=False)

# Tightened chain: Gemini-specific names only (no generic API_KEY pickup).
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENAI_API_KEY")
if API_KEY:
    API_KEY = API_KEY.strip().strip('"').strip("'")

# Model configurable via env; migrate models with an .env edit, not a code hunt.
# Defensive strip: dotenv keeps stray quotes/whitespace on unquoted values
# verbatim (e.g. `KEY=value"` -> value has a trailing `"`), which the Gemini
# API rejects with "unexpected model name format" rather than a clear error.
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip().strip('"').strip("'")

# Try to import Gemini client (optional; chatbot gracefully degrades if absent).
try:
    from google import genai
    from google.genai import types as genai_types

    _gemini_client = genai.Client(api_key=API_KEY) if API_KEY else None
    CHATBOT_ENABLED = _gemini_client is not None
except ImportError:
    logging.warning(
        "google-genai not installed. Install with: pip install google-genai"
    )
    _gemini_client = None
    genai_types = None
    CHATBOT_ENABLED = False

if not API_KEY:
    logging.warning(
        "GEMINI_API_KEY / GOOGLE_GENAI_API_KEY not set. Chatbot will provide fallback responses."
    )
    CHATBOT_ENABLED = False

# Per-conversation in-memory store (cache layer)
# Persisted to MongoDB for durability and analytics
conversations: dict[str, list] = {}

# Default temperature for response creativity (0.0=deterministic, 1.0=creative)
DEFAULT_TEMPERATURE = 0.7

# Token estimation helper (rough approximation: 1 token ≈ 4 chars)
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

SYSTEM_INSTRUCTION = """\
You are Whitfield WMS Assistant, a helpful and accurate warehouse operations helper.

## Your Purpose
Help Whitfield Fulfillment staff, managers, and owners with:
- **Staff FAQ**: SOP questions, receiving procedures, packing guidelines
- **Stock Lookups**: Check inventory, find items by barcode/location
- **Order Tracking**: View order status, fulfillment progress
- **Arrival Logging**: Confirm incoming shipment details (partner with voice logging)
- **Manager Queries**: Approvals needed, team metrics, warehouse utilization
- **Audit Access**: Who changed what, when (OWNER only)

## Rules
- **ALWAYS use tools** for live data. Never invent order IDs, quantities, locations, or dates.
- **Role-based access**: Respect user role (STAFF, MANAGER, OWNER) and warehouse scope.
  - STAFF: See only their assigned warehouse, no owner-level reports
  - MANAGER: Their warehouse + team data, no other facilities
  - OWNER: Full system view + audit access
- **For unknown questions**: Say "I don't have information about that. Please contact your manager."
- **Never diagnose or assume**: If data is missing, say so.
- **For confirmation dialogs**: Partner with voice logging endpoint — confirm details before logging.
- **Keep responses short**: One sentence is better than a paragraph.
"""

# Tool declarations only defined if genai_types is available
if genai_types:
    TOOL_DECLARATIONS = genai_types.Tool(
        function_declarations=[
            genai_types.FunctionDeclaration(
                name="search_orders",
                description="Search for orders by ID, customer, or status. Returns matching orders with fulfillment progress.",
                parameters=genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "query": genai_types.Schema(
                            type=genai_types.Type.STRING,
                            description="Order ID, customer name, or status (PENDING/RESERVED/PACKED/SHIPPED)",
                        ),
                        "limit": genai_types.Schema(
                            type=genai_types.Type.INTEGER,
                            description="Max results (default 10, max 100)",
                        ),
                    },
                    required=["query"],
                ),
            ),
            genai_types.FunctionDeclaration(
                name="check_inventory",
                description="Check stock levels and locations. Search by item barcode, SKU, or location code.",
                parameters=genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "search": genai_types.Schema(
                            type=genai_types.Type.STRING,
                            description="Barcode, SKU, or storage location (e.g., 'A-12-05' or 'SKU-12345')",
                        ),
                    },
                    required=["search"],
                ),
            ),
            genai_types.FunctionDeclaration(
                name="get_pending_approvals",
                description="Get tickets pending manager approval. Managers see their warehouse; OWNER sees all.",
                parameters=genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={},
                    required=[],
                ),
            ),
            genai_types.FunctionDeclaration(
                name="audit_log_search",
                description="Search audit logs for changes (OWNER only). Find who changed what and when.",
                parameters=genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "query": genai_types.Schema(
                            type=genai_types.Type.STRING,
                            description="Search term: entity type (e.g., 'orders'), user email, action, date range",
                        ),
                        "days_back": genai_types.Schema(
                            type=genai_types.Type.INTEGER,
                            description="Search last N days (default 30)",
                        ),
                    },
                    required=["query"],
                ),
            ),
            genai_types.FunctionDeclaration(
                name="get_sop_info",
                description="Return SOP guidance for common staff questions: receiving, packing, shipping, safety.",
                parameters=genai_types.Schema(
                    type=genai_types.Type.OBJECT,
                    properties={
                        "topic": genai_types.Schema(
                            type=genai_types.Type.STRING,
                            description="Topic: 'receiving', 'packing', 'shipping', 'safety', 'quality'",
                        ),
                    },
                    required=["topic"],
                ),
            ),
        ]
    )
else:
    TOOL_DECLARATIONS = None


# ---------------------------------------------------------------------------
# History helpers — the SDK requires uniform Content objects (role: user/model),
# never dicts with a "content" key. These helpers keep every append consistent.
# ---------------------------------------------------------------------------

def _user_text(text: str):
    return genai_types.Content(
        role="user", parts=[genai_types.Part.from_text(text=text)]
    )


def _model_text(text: str):
    return genai_types.Content(
        role="model", parts=[genai_types.Part.from_text(text=text)]
    )


def _tool_result_content(tool_name: str, result: str):
    return genai_types.Content(
        role="user",
        parts=[
            genai_types.Part.from_function_response(
                name=tool_name, response={"result": result}
            )
        ],
    )


async def resolve_tool_call(
    tool_name: str,
    tool_args: dict,
    current_user: dict,
) -> str:
    """
    Execute a tool call and return result as string.

    Args:
        tool_name: Name of the tool to invoke
        tool_args: Arguments for the tool
        current_user: Authenticated user (contains role, warehouse_id, email)

    Returns:
        Result as string (safe for Gemini)
    """
    # Import here to avoid circular deps
    from core.cruds.wms_crud import CRUDOrder, CRUDStorageLocation, CRUDTicket
    from core.database.database import MongoDatabase

    user_role = current_user.get("role", "STAFF")
    user_warehouse_id = current_user.get("warehouse_id")

    if tool_name == "search_orders":
        try:
            query = tool_args.get("query", "")
            limit = min(tool_args.get("limit", 10), 100)

            crud = CRUDOrder()
            filter_doc = {}

            if query.upper() in ["PENDING", "RESERVED", "PACKED", "SHIPPED"]:
                filter_doc["status"] = query.upper()
            else:
                filter_doc = {
                    "$or": [
                        {"order_id": {"$regex": query, "$options": "i"}},
                        {"customer_name": {"$regex": query, "$options": "i"}},
                    ]
                }

            orders, total = await crud.list_orders(filter_doc, skip=0, limit=limit)

            # Scope: STAFF and MANAGER see only their warehouse; OWNER sees all.
            if user_role in ("STAFF", "MANAGER") and user_warehouse_id:
                orders = [o for o in orders if o.get("warehouse_id") == user_warehouse_id]

            if not orders:
                return f"No orders found matching '{query}'."

            summary = "\n".join(
                [
                    f"- {o.get('order_id')}: {o.get('customer_name')} ({o.get('status')}, {len(o.get('items', []))} items)"
                    for o in orders[:limit]
                ]
            )
            return f"Found {len(orders)} orders:\n{summary}"

        except Exception as exc:
            logging.error(f"Error in search_orders: {exc}")
            return f"Error searching orders: {str(exc)}"

    elif tool_name == "check_inventory":
        try:
            search = tool_args.get("search", "")
            db = MongoDatabase()
            filter_doc = {
                "$or": [
                    {"location_code": {"$regex": search, "$options": "i"}},
                    {"barcode": {"$regex": search, "$options": "i"}},
                ]
            }
            locations = await db.storage_locations.find(filter_doc).limit(50).to_list(length=50)

            if not locations:
                return f"No inventory found for '{search}'."

            # Scope: STAFF and MANAGER limited to their warehouse.
            if user_role in ("STAFF", "MANAGER") and user_warehouse_id:
                locations = [l for l in locations if l.get("warehouse_id") == user_warehouse_id]

            if not locations:
                return f"No inventory found for '{search}' in your warehouse."

            summary = "\n".join(
                [
                    f"- Location {l.get('location_code')}: {l.get('quantity', 0)} units (barcode: {l.get('barcode')})"
                    for l in locations[:10]
                ]
            )
            return f"Found {len(locations)} storage locations:\n{summary}"

        except Exception as exc:
            logging.error(f"Error in check_inventory: {exc}")
            return f"Error checking inventory: {str(exc)}"

    elif tool_name == "get_pending_approvals":
        try:
            if user_role not in ["MANAGER", "OWNER"]:
                return "Only managers and owners can view pending approvals."

            db = MongoDatabase()
            filter_doc = {"status": "PENDING_APPROVAL"}

            if user_role == "MANAGER" and user_warehouse_id:
                filter_doc["warehouse_id"] = user_warehouse_id

            approvals = await db.approvals.find(filter_doc).sort("created_at", -1).limit(100).to_list(length=100)

            if not approvals:
                return "No pending approvals."

            summary = "\n".join(
                [
                    f"- Ticket {a.get('ticket_id')}: {a.get('item_count', 0)} items (arrived {a.get('created_at')})"
                    for a in approvals[:10]
                ]
            )
            return f"You have {len(approvals)} pending approvals:\n{summary}"

        except Exception as exc:
            logging.error(f"Error in get_pending_approvals: {exc}")
            return f"Error retrieving approvals: {str(exc)}"

    elif tool_name == "audit_log_search":
        try:
            if user_role != "OWNER":
                return "Audit logs are accessible to OWNER only."

            query = tool_args.get("query", "")
            days_back = int(tool_args.get("days_back", 30) or 30)

            db = MongoDatabase()
            # days_back now actually used (was hardcoded to month start before).
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

            # Regex search instead of $text: works without a text index.
            results = await db.audit_log.find(
                {
                    "$or": [
                        {"entity_type": {"$regex": query, "$options": "i"}},
                        {"user_email": {"$regex": query, "$options": "i"}},
                        {"action": {"$regex": query, "$options": "i"}},
                    ],
                    "created_at": {"$gte": cutoff.isoformat()},
                }
            ).sort("created_at", -1).limit(10).to_list(length=10)

            if not results:
                return f"No audit records found for '{query}' in the last {days_back} days."

            summary = "\n".join(
                [
                    f"- {r.get('action')} on {r.get('entity_type')} by {r.get('user_email')} ({r.get('created_at')})"
                    for r in results[:10]
                ]
            )
            return f"Found {len(results)} audit records:\n{summary}"

        except Exception as exc:
            logging.error(f"Error in audit_log_search: {exc}")
            return f"Error searching audit logs: {str(exc)}"

    elif tool_name == "get_sop_info":
        topic = tool_args.get("topic", "").lower()

        sops = {
            "receiving": (
                "**Receiving SOP**: "
                "1. Check shipment barcode against PO. "
                "2. Log parcels in system (voice or manual). "
                "3. Manager approves; items moved to storage. "
                "4. Update location codes and QC flags."
            ),
            "packing": (
                "**Packing SOP**: "
                "1. Pick items from storage per order list. "
                "2. Inspect for damage/quality. "
                "3. Box and label (use barcode printer). "
                "4. Update order status to PACKED. "
                "5. Ready for handoff to shipping."
            ),
            "shipping": (
                "**Shipping SOP**: "
                "1. Collect PACKED orders. "
                "2. Generate shipping labels (carrier integration). "
                "3. Update tracking in system. "
                "4. Mark order SHIPPED. "
                "5. Hand off to carrier."
            ),
            "safety": (
                "**Warehouse Safety**: "
                "- Hard hats required in receiving area. "
                "- Report hazmat immediately. "
                "- Keep aisles clear. "
                "- Use mechanical lifts for heavy items."
            ),
            "quality": (
                "**Quality Checks**: "
                "- Inspect arrivals for shipping damage. "
                "- Check expiry dates for time-sensitive items. "
                "- Report discrepancies to QA. "
                "- Flag items for rework/return."
            ),
        }

        return sops.get(topic, f"Unknown SOP topic: {topic}. Try: receiving, packing, shipping, safety, quality.")

    else:
        return f"Tool '{tool_name}' not recognized."


class ChatbotController:
    """WMS Chatbot controller using Google Gemini."""

    def __init__(self):
        # Lenient constructor: a missing key/SDK no longer raises here.
        # run_turn's documented fallback path handles it (was unreachable before).
        self.client = _gemini_client

    async def run_turn(
        self,
        conversation_id: str,
        user_input: str,
        current_user: dict,
    ) -> str:
        """
        Process a chat turn: send message to Gemini, resolve tool calls, return reply.

        If Gemini is not configured, returns a fallback response instead of erroring.
        Saves conversation to MongoDB for persistence and analytics.
        """
        if conversation_id not in conversations:
            conversations[conversation_id] = []
            # Initialize conversation in MongoDB
            crud_chat = CRUDChat()
            from core.models.chat_model import ChatConversation
            initial_conv = ChatConversation(
                conversation_id=conversation_id,
                user_id=current_user.get("id", "unknown"),
                user_role=current_user.get("role", "STAFF"),
                warehouse_id=current_user.get("warehouse_id"),
            )
            await crud_chat.append_messages(
                conversation_id=conversation_id,
                messages=[],
                tokens_delta=0,
            )

        # If Gemini not configured/installed, fallback — checked BEFORE any
        # SDK-typed history is written, and stored as plain dicts safely.
        if not CHATBOT_ENABLED or not self.client or genai_types is None:
            fallback = (
                "I'm the Whitfield WMS Assistant. To enable AI features, set "
                "GEMINI_API_KEY in .env and install google-genai. For now, I can "
                "help you find: orders, inventory, approvals, and SOPs. "
                "What would you like to know?"
            )
            conversations[conversation_id].append({"role": "user", "text": user_input})
            conversations[conversation_id].append({"role": "model", "text": fallback})
            return fallback

        # Add user message to history (uniform Content object — never a dict).
        conversations[conversation_id].append(_user_text(user_input))

        try:
            # First Gemini call (with tools) — new SDK: everything in config=.
            response = await self.client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=conversations[conversation_id],
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[TOOL_DECLARATIONS] if TOOL_DECLARATIONS else None,
                ),
            )

            if response.function_calls:
                # Single-tool turn (matches original design; parallel calls = BACKLOG).
                fc = response.function_calls[0]
                tool_name = fc.name
                tool_args = dict(fc.args) if fc.args else {}

                logging.info(
                    f"Tool call: {tool_name} by {current_user.get('email')}"
                )

                # Record the model's tool request verbatim off the response.
                conversations[conversation_id].append(response.candidates[0].content)

                try:
                    tool_result = await resolve_tool_call(
                        tool_name, tool_args, current_user
                    )
                except ValueError as auth_err:
                    tool_result = f"Permission denied: {str(auth_err)}"

                # Feed the tool result back as a function_response part.
                conversations[conversation_id].append(
                    _tool_result_content(tool_name, tool_result)
                )

                # Second Gemini call (no tools) for the final natural reply.
                final_response = await self.client.aio.models.generate_content(
                    model=MODEL_NAME,
                    contents=conversations[conversation_id],
                    config=genai_types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                    ),
                )
                reply_text = final_response.text or ""
            else:
                # Model answered directly, no tool needed.
                reply_text = response.text or ""

            reply_text = reply_text or "I couldn't process that request. Please try again."

            # Save assistant reply to history (both paths).
            conversations[conversation_id].append(_model_text(reply_text))

            # Persist to MongoDB: extract token counts from response metadata if available
            turn_start = time.time()
            tokens_in = getattr(response, "usage_metadata", None)
            if tokens_in:
                tokens_in_count = getattr(tokens_in, "prompt_token_count", 0)
                tokens_out_count = getattr(tokens_in, "candidates_token_count", 0)
            else:
                tokens_in_count = estimate_tokens(user_input)
                tokens_out_count = estimate_tokens(reply_text)
            tokens_total = tokens_in_count + tokens_out_count

            # Save user and model messages
            crud_chat = CRUDChat()
            await crud_chat.append_messages(
                conversation_id=conversation_id,
                messages=[
                    {
                        "role": "user",
                        "text": user_input,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "tokens_used": tokens_in_count,
                    },
                    {
                        "role": "model",
                        "text": reply_text,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "tokens_used": tokens_out_count,
                    },
                ],
                tokens_delta=tokens_total,
            )

            # Log response metrics (for analytics)
            response_time_ms = (time.time() - turn_start) * 1000
            logging.info(
                f"Chat metrics | conv={conversation_id} | tokens={tokens_total} "
                f"(in={tokens_in_count} out={tokens_out_count}) | time={response_time_ms:.0f}ms"
            )

            return reply_text

        except HTTPException:
            raise
        except Exception as exc:
            logging.error(f"Error in run_turn: {exc}")
            # Upstream/model failure ≠ our server bug: surface as 502 with a
            # clean envelope, never a raw 500 with internals.
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Assistant temporarily unavailable. Please try again.",
            )

    async def get_history(
        self,
        conversation_id: str,
        current_user: dict,
    ) -> list:
        """
        Retrieve chat history from MongoDB with RBAC.

        OWNER can access any conversation; users can only access their own.
        Returns JSON-safe dicts: [{role, text, timestamp}, ...]
        """
        try:
            crud_chat = CRUDChat()
            conversation = await crud_chat.get_conversation(conversation_id)

            if not conversation:
                return []

            # RBAC: user can only view their own conversation (unless OWNER)
            if (
                current_user.get("role") != "OWNER"
                and conversation.get("user_id") != current_user.get("id")
            ):
                raise ValueError("Access denied: conversation does not belong to user")

            # Extract messages: {role, text, timestamp}
            messages = conversation.get("messages", [])
            return [
                {"role": msg.get("role", ""), "text": msg.get("text", "")}
                for msg in messages
            ]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
        except Exception as error:
            logging.error(f"Error in get_history: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving history",
            )