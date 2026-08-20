import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Send, Loader2, MessageCircle, X, ChevronRight } from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { Panel } from "@/components/wms/ui-bits";
import { ProtectedRoute } from "@/lib/protected-route";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth-context";

export const Route = createFileRoute("/chatbot")({
  head: () => ({
    meta: [
      { title: "AI Assistant — Whitfield WMS" },
      { name: "description", content: "Natural language assistant for warehouse operations" },
    ],
  }),
  component: ChatbotPageWrapper,
});

interface Message {
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const API_BASE = import.meta.env['VITE_API_BASE_URL'] || "http://127.0.0.1:8000";

// API client for chatbot
const chatbotAPI = {
  async sendMessage(conversationId: string, userInput: string, token: string) {
    const response = await fetch(`${API_BASE}/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        user_input: userInput,
      }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return response.json();
  },

  async getHistory(conversationId: string, token: string) {
    const response = await fetch(
      `${API_BASE}/chat/history/${conversationId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return response.json();
  },
};

function ChatbotContent() {
  const { user } = useAuth();
  const [conversationId] = useState(
    `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );
  const [messages, setMessages] = useState<Message[]>([
    {
      type: "assistant",
      content:
        "Hi! I'm your Whitfield WMS Assistant. I can help you with order tracking, inventory lookups, pending approvals, SOP questions, and audit logs. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [token, setToken] = useState<string>("");

  // Get token from localStorage
  useEffect(() => {
    const accessToken = localStorage.getItem("access_token");
    if (accessToken) {
      setToken(accessToken);
    }
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || !token) {
      toast.error("Please enter a message");
      return;
    }

    // Add user message
    const userMessage: Message = {
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await chatbotAPI.sendMessage(
        conversationId,
        inputValue,
        token
      );

      const assistantMessage: Message = {
        type: "assistant",
        content: response.response || "No response generated",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to send message";
      toast.error(errorMessage);
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell crumbs={[{ label: "Dashboard", to: "/" }, { label: "AI Assistant" }]} title="Warehouse AI Assistant">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column: Chat Container */}
        <div className="lg:col-span-2 flex flex-col h-fit bg-white border border-[var(--wf-border)] rounded-xl shadow-sm overflow-hidden">
          {/* Messages Area */}
          <div className="overflow-y-auto space-y-4 p-6 bg-[#FAF6F0]/30 max-h-[480px]">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  style={{
                    backgroundColor: msg.type === "user" ? "var(--wf-orange)" : "#fff",
                    color: msg.type === "user" ? "#fff" : "var(--wf-dark)",
                    borderColor: msg.type === "user" ? "transparent" : "var(--wf-border)",
                  }}
                  className={`max-w-[80%] rounded-xl px-4 py-3 border shadow-sm ${
                    msg.type === "user" ? "rounded-tr-none" : "rounded-tl-none"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p className="text-[10px] mt-1.5 opacity-70 font-semibold text-right">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-xl px-4 py-3 border border-[var(--wf-border)] shadow-sm rounded-tl-none">
                  <Loader2 className="size-4 animate-spin text-[var(--wf-orange)]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-[var(--wf-border)] bg-[#FAF6F0] p-4">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <Input
                type="text"
                placeholder="Ask about orders, inventory, approvals..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
                style={{
                  border: "1px solid var(--wf-border)",
                }}
                className="flex-1 bg-white text-[var(--wf-dark)] placeholder:text-[#7A7A6E] focus:border-[var(--wf-orange)] focus:ring-0 outline-none h-11 rounded-lg text-sm"
              />
              <Button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                style={{
                  backgroundColor: "var(--wf-orange)",
                  color: "#fff",
                }}
                className="hover:brightness-110 text-white disabled:opacity-50 h-11 px-5 rounded-lg font-bold flex items-center justify-center border-0 cursor-pointer"
              >
                {isLoading ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <Send className="size-4" />
                )}
              </Button>
            </form>
          </div>
        </div>

        {/* Right Column: Capabilities & Context Panels */}
        <div className="space-y-4 lg:col-span-1">
          {/* Assistant Capabilities */}
          <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "16px 20px" }} className="shadow-sm rounded-xl">
            <div className="flex items-center gap-2.5 mb-4 border-b border-[var(--wf-border)] pb-3">
              <div style={{ background: "var(--wf-orange-pale)", color: "var(--wf-orange)" }} className="p-2 rounded-lg">
                <MessageCircle className="size-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base text-[var(--wf-dark)] font-outfit">AI Capabilities</h3>
                <p className="text-[10px] text-muted-foreground">What you can ask the assistant</p>
              </div>
            </div>

            <ul className="space-y-3">
              {[
                { title: "Search orders by ID", desc: "Instantly check logs or fulfillment statuses." },
                { title: "Check inventory", desc: "Lookup counts by item barcode or bay location." },
                { title: "View approvals", desc: "Access review items queue (Owner/Manager)." },
                { title: "Search audit logs", desc: "Track system access transactions (Owner only)." },
                { title: "SOP guidance", desc: "Get detailed instructions for receiving or shipping." },
              ].map((cap, i) => (
                <li key={i} className="flex gap-2 items-start">
                  <span className="size-1.5 rounded-full bg-[var(--wf-orange)] mt-1.5 shrink-0" />
                  <div>
                    <p className="text-xs font-bold text-[var(--wf-dark)] leading-tight">{cap.title}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{cap.desc}</p>
                  </div>
                </li>
              ))}
            </ul>
          </Panel>

          {/* Quick Suggestions Starter */}
          <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "16px 20px" }} className="shadow-sm rounded-xl">
            <h4 className="text-xs font-extrabold text-[var(--wf-dark)] font-outfit uppercase tracking-wider mb-3">
              Quick Suggestions
            </h4>
            <div className="flex flex-wrap gap-2">
              {[
                "Fulfillment SOP receiving",
                "Identify pending approvals",
                "Check Reno warehouse capacity",
                "Search audit log recent",
              ].map((promptText) => (
                <button
                  key={promptText}
                  onClick={() => setInputValue(promptText)}
                  style={{ border: "1px solid var(--wf-border)" }}
                  className="px-3 py-2 rounded-lg bg-[#FAF6F0] hover:bg-[var(--wf-orange-pale)] text-xs text-[var(--wf-dark-secondary)] hover:text-[var(--wf-orange)] font-semibold transition-all duration-150 text-left w-full flex items-center justify-between cursor-pointer"
                >
                  <span>"{promptText}"</span>
                  <ChevronRight size={12} className="opacity-60" />
                </button>
              ))}
            </div>
          </Panel>

          {/* Session Scope Details */}
          <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "16px 20px" }} className="shadow-sm rounded-xl">
            <h4 className="text-xs font-extrabold text-[var(--wf-dark)] font-outfit uppercase tracking-wider mb-3">
              Operator Scope
            </h4>
            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1 border-b border-[#FAF6F0]">
                <span className="text-muted-foreground">Active Role</span>
                <span className="font-bold text-[var(--wf-orange)] bg-[var(--wf-orange-pale)] px-2 py-0.5 rounded text-[10px]">
                  {user?.role || "OWNER"}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#FAF6F0]">
                <span className="text-muted-foreground">Facility Limit</span>
                <span className="font-bold text-[var(--wf-dark)]">
                  {user?.warehouse_id ? `Warehouse ${user.warehouse_id}` : "Global (All Warehouses)"}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#FAF6F0]">
                <span className="text-muted-foreground">Experience Tier</span>
                <span className="font-bold text-[var(--wf-dark)]">
                  {user?.experience_tier || "EXPERIENCED"}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-muted-foreground">Account Status</span>
                <span className="font-bold text-green-700">
                  {user?.status || "active"}
                </span>
              </div>
            </div>
          </Panel>
        </div>
      </div>
    </AppShell>
  );
}

function ChatbotPageWrapper() {
  return (
    <ProtectedRoute>
      <ChatbotContent />
    </ProtectedRoute>
  );
}
