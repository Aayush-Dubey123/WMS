import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Send, Loader2, MessageCircle, X } from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
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

// API client for chatbot
const chatbotAPI = {
  async sendMessage(conversationId: string, userInput: string, token: string) {
    const response = await fetch("http://127.0.0.1:8000/chat/message", {
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
      `http://127.0.0.1:8000/chat/history/${conversationId}`,
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
      <div className="mx-auto max-w-2xl">
        {/* Chat Container */}
        <div className="flex h-[600px] flex-col rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm shadow-xl overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto space-y-4 p-6">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-xs rounded-lg px-4 py-2.5 ${
                    msg.type === "user"
                      ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white"
                      : "bg-slate-700/50 text-slate-100 border border-slate-600/50"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {msg.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-700/50 text-slate-100 rounded-lg px-4 py-2.5 border border-slate-600/50">
                  <Loader2 className="size-5 animate-spin text-cyan-400" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-slate-700/50 bg-slate-900/50 p-4">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <Input
                type="text"
                placeholder="Ask about orders, inventory, approvals..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
                className="flex-1 bg-slate-700/30 border-slate-600/30 text-white placeholder:text-slate-500 focus:border-cyan-500/50 focus:ring-cyan-500/20"
              />
              <Button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white disabled:opacity-50"
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

        {/* Info Box */}
        <div className="mt-6 rounded-lg border border-blue-500/20 bg-blue-500/5 p-4">
          <div className="flex gap-3">
            <MessageCircle className="size-5 text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-slate-300">
              <p className="font-semibold text-blue-300 mb-1">✨ Assistant Capabilities:</p>
              <ul className="space-y-1 text-xs">
                <li>• <span className="text-slate-400">Search orders by ID, customer, or status</span></li>
                <li>• <span className="text-slate-400">Check inventory by barcode or location</span></li>
                <li>• <span className="text-slate-400">View pending approvals (Manager/Owner)</span></li>
                <li>• <span className="text-slate-400">Search audit logs (Owner only)</span></li>
                <li>• <span className="text-slate-400">Get SOP guidance for receiving, packing, shipping</span></li>
              </ul>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="mt-6 text-xs text-slate-400">
          <p>Role: <span className="text-slate-300 font-semibold capitalize">{user?.role}</span></p>
          <p>Scope: <span className="text-slate-300">{user?.warehouse_id ? `Warehouse ${user.warehouse_id}` : 'Global'}</span></p>
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
