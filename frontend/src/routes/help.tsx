import { createFileRoute } from "@tanstack/react-router";
import { BookOpen, Mail, MessageCircle, Zap } from "lucide-react";

import { AppShell } from "@/components/wms/app-shell";
import { Panel } from "@/components/wms/ui-bits";
import { ProtectedRoute } from "@/lib/protected-route";

export const Route = createFileRoute("/help")({
  head: () => ({
    meta: [{ title: "Help & Support — Whitfield WMS" }],
  }),
  component: HelpPageWrapper,
});

const FAQ = [
  {
    q: "How do I process an inbound shipment?",
    a: "Go to Tickets & Arrivals → click 'New Arrival', enter the tracking number and warehouse. The system matches it to an accepted inbox announcement and generates a ticket.",
  },
  {
    q: "How do I approve a ticket?",
    a: "Once staff submit a ticket for inspection (status PENDING_INSPECTION), it appears in the Approvals queue. Open the ticket and click 'Approve' to transition items to SHIPMENT_ARRIVED.",
  },
  {
    q: "How does order reservation work?",
    a: "Create an order, then click 'Reserve'. The system atomically reserves matching STORED items. Concurrent reservation conflicts return HTTP 409 — retry or adjust the order.",
  },
  {
    q: "What is Voice Assistance?",
    a: "Staff can upload an audio clip describing a parcel. The system transcribes it, extracts item details via LLM, and creates a draft for confirmation — hands-free scanning.",
  },
  {
    q: "How do I export reports?",
    a: "Go to Reports and use the Export button to download the current view as CSV or XLSX. Note: the backend export endpoint is not yet implemented in this deployment.",
  },
];

function HelpContent() {
  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Help & Support" }]}
      title="Help & Support"
    >
      <div className="max-w-2xl space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            { icon: BookOpen, label: "Documentation", sub: "Full API & user guide" },
            { icon: MessageCircle, label: "Chat Support", sub: "Ask the AI Assistant" },
            { icon: Mail, label: "Email Support", sub: "ops@whitfield.io" },
          ].map(({ icon: Icon, label, sub }) => (
            <Panel key={label} className="flex items-center gap-3">
              <Icon className="size-5 text-primary" />
              <div>
                <p className="text-sm font-semibold">{label}</p>
                <p className="text-[12px] text-muted-foreground">{sub}</p>
              </div>
            </Panel>
          ))}
        </div>

        <Panel>
          <div className="flex items-center gap-2 mb-4">
            <Zap className="size-4 text-primary" />
            <h3 className="font-semibold">Frequently Asked Questions</h3>
          </div>
          <dl className="space-y-5">
            {FAQ.map(({ q, a }) => (
              <div key={q}>
                <dt className="text-sm font-semibold">{q}</dt>
                <dd className="mt-1 text-sm text-muted-foreground">{a}</dd>
              </div>
            ))}
          </dl>
        </Panel>
      </div>
    </AppShell>
  );
}

function HelpPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER", "STAFF"]}>
      <HelpContent />
    </ProtectedRoute>
  );
}
