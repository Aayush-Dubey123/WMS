"""
export_postman_collection.py — Export Postman Collection script.

Converts FastAPI OpenAPI schema into a Postman v2.1 collection JSON file with
pre-configured authentication environment variables (Owner, Manager, Rookie).
Run with: python -m scripts.export_postman_collection
"""

import json
import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.apis.api import custom_openapi
from core.config.settings import settings


def generate_postman_collection() -> dict:
    """
    Generate Postman v2.1 collection dictionary from FastAPI app OpenAPI schema.

    Returns:
        dict: Postman v2.1 collection JSON dictionary.
    """
    openapi = custom_openapi()

    items = []
    for path, methods in openapi.get("paths", {}).items():
        for method, spec in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            summary = spec.get("summary", f"{method.upper()} {path}")
            description = spec.get("description", "")
            tags = spec.get("tags", ["Default"])

            postman_item = {
                "name": f"[{tags[0]}] {summary}",
                "request": {
                    "method": method.upper(),
                    "header": [
                        {"key": "Content-Type", "value": "application/json", "type": "text"},
                        {"key": "Authorization", "value": "Bearer {{jwt_token}}", "type": "text"},
                    ],
                    "url": {
                        "raw": "{{base_url}}" + path,
                        "host": ["{{base_url}}"],
                        "path": [p for p in path.split("/") if p],
                    },
                    "description": description,
                },
                "response": [],
            }
            items.append(postman_item)

    collection = {
        "info": {
            "name": f"{settings.APP_NAME} API Collection",
            "description": "Postman Collection for Whitfield Fulfillment WMS Backend API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000", "type": "string"},
            {"key": "jwt_token", "value": "PASTE_TOKEN_HERE", "type": "string"},
        ],
    }

    return collection


def main():
    """Script entrypoint writing postman_collection.json file."""
    output_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "postman_collection.json")
    )
    collection = generate_postman_collection()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)

    print(f"Successfully exported Postman Collection to: {output_path}")


if __name__ == "__main__":
    main()
