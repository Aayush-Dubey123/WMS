import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { AlertOctagon, Loader2, PackageCheck, ShieldAlert, Ticket } from "lucide-react";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import { MetricCard, Panel, TableShell, Td, Th, Tr } from "@/components/wms/ui-bits";
import { ProtectedRoute } from "@/lib/protected-route";
import { useAuth } from "@/lib/auth-context";
import { reportsAPI, auditAPI } from "@/lib/api";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Analytics & Reports — Whitfield WMS" },
      {
        name: "description",
        content: "Executive warehouse analytics: today's tickets, sold items and unannounced arrivals.",
      },
    ],
  }),
  component: ReportsPageWrapper,
});

function ReportsContent() {
  const { user } = useAuth();
  const today = new Date().toISOString().slice(0, 10);

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["reports-summary", today],
    queryFn: () => reportsAPI.getSummary(today),
    staleTime: 30000,
  });

  const { data: arrivedData, isLoading: arrivedLoading } = useQuery({
    queryKey: ["reports-arrived-today"],
    queryFn: () => reportsAPI.getArrivedToday(0, 25),
    staleTime: 30000,
  });

  const { data: soldData, isLoading: soldLoading } = useQuery({
    queryKey: ["reports-sold-today"],
    queryFn: () => reportsAPI.getSoldToday(0, 25),
    staleTime: 30000,
  });

  const { data: auditData, isLoading: auditLoading } = useQuery({
    queryKey: ["reports-audit"],
    queryFn: () => auditAPI.list(0, 10),
    staleTime: 30000,
    enabled: user?.role === "OWNER",
  });

  const summaryData = summary as
    | { todays_tickets?: number; todays_sold?: number; arrived_missed?: number; per_warehouse?: any[] }
    | undefined;
  const arrivals = (arrivedData as { records?: any[] } | undefined)?.records ?? [];
  const sold = (soldData as { records?: any[] } | undefined)?.records ?? [];
  const auditLogs = (auditData as { logs?: any[] } | undefined)?.logs ?? [];
  const perWarehouse = summaryData?.per_warehouse ?? [];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Reports" }]}
      title="Analytics & Reports"
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard
          icon={Ticket}
          title="Tickets Created Today"
          value={summaryLoading ? "—" : String(summaryData?.todays_tickets ?? 0)}
        />
        <MetricCard
          icon={PackageCheck}
          title="Items Sold Today"
          value={summaryLoading ? "—" : String(summaryData?.todays_sold ?? 0)}
        />
        <MetricCard
          icon={AlertOctagon}
          title="Unannounced Arrivals"
          value={summaryLoading ? "—" : String(summaryData?.arrived_missed ?? 0)}
        />
      </div>

      {perWarehouse.length > 0 && (
        <section className="mt-6">
          <Panel>
            <h3>Per-Warehouse Breakdown</h3>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {perWarehouse.map((w: any) => (
                <div key={w.warehouse_id} className="rounded-md border border-border p-3">
                  <p className="font-mono text-[12px] text-muted-foreground">{w.warehouse_id}</p>
                  <div className="mt-2 flex justify-between text-sm">
                    <span className="text-muted-foreground">Tickets</span>
                    <span className="font-semibold">{w.todays_tickets}</span>
                  </div>
                  <div className="mt-1 flex justify-between text-sm">
                    <span className="text-muted-foreground">Sold</span>
                    <span className="font-semibold">{w.todays_sold}</span>
                  </div>
                  <div className="mt-1 flex justify-between text-sm">
                    <span className="text-muted-foreground">Unannounced</span>
                    <span className="font-semibold text-warning">{w.arrived_missed}</span>
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </section>
      )}

      <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <TableShell toolbar={<h3 className="text-base font-semibold">Arrived Today</h3>}>
          <thead>
            <tr>
              <Th>Ticket</Th>
              <Th>Warehouse</Th>
              <Th>Status</Th>
              <Th>Tracking</Th>
            </tr>
          </thead>
          <tbody>
            {arrivedLoading ? (
              <tr>
                <Td colSpan={4} className="py-8 text-center">
                  <Loader2 className="mx-auto size-5 animate-spin text-primary" />
                </Td>
              </tr>
            ) : arrivals.length === 0 ? (
              <tr>
                <Td colSpan={4} className="py-8 text-center text-muted-foreground">
                  No arrivals today
                </Td>
              </tr>
            ) : (
              arrivals.map((r: any) => (
                <Tr key={r.ticket_id}>
                  <Td className="font-mono text-[12px] text-primary">{r.ticket_id}</Td>
                  <Td className="text-[12px] text-muted-foreground">{r.warehouse_id}</Td>
                  <Td>
                    <StatusBadge status={r.status} />
                  </Td>
                  <Td className="font-mono text-[12px] text-muted-foreground">
                    {r.tracking_number || "—"}
                  </Td>
                </Tr>
              ))
            )}
          </tbody>
        </TableShell>

        <TableShell toolbar={<h3 className="text-base font-semibold">Sold Today</h3>}>
          <thead>
            <tr>
              <Th>Barcode</Th>
              <Th>Product</Th>
              <Th>Warehouse</Th>
              <Th>Order</Th>
            </tr>
          </thead>
          <tbody>
            {soldLoading ? (
              <tr>
                <Td colSpan={4} className="py-8 text-center">
                  <Loader2 className="mx-auto size-5 animate-spin text-primary" />
                </Td>
              </tr>
            ) : sold.length === 0 ? (
              <tr>
                <Td colSpan={4} className="py-8 text-center text-muted-foreground">
                  No items sold today
                </Td>
              </tr>
            ) : (
              sold.map((r: any) => (
                <Tr key={r.item_id}>
                  <Td className="font-mono text-[12px] text-muted-foreground">{r.barcode}</Td>
                  <Td className="font-medium">{r.product_name}</Td>
                  <Td className="text-[12px] text-muted-foreground">{r.warehouse_id}</Td>
                  <Td className="font-mono text-[12px] text-primary">{r.order_id || "—"}</Td>
                </Tr>
              ))
            )}
          </tbody>
        </TableShell>
      </section>

      {user?.role === "OWNER" && (
        <section className="mt-6">
          <Panel>
            <div className="flex items-center gap-2">
              <ShieldAlert className="size-4 text-muted-foreground" />
              <h3>Recent Audit Activity</h3>
            </div>
            <ol className="mt-4 space-y-3 border-l border-border pl-5">
              {auditLoading ? (
                <li className="py-4">
                  <Loader2 className="size-5 animate-spin text-primary" />
                </li>
              ) : auditLogs.length === 0 ? (
                <li className="text-sm text-muted-foreground">No recent audit records</li>
              ) : (
                auditLogs.map((a: any) => (
                  <li key={a.id} className="relative">
                    <span className="absolute top-1.5 -left-[26px] size-2.5 rounded-full bg-primary" />
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <p className="text-sm">
                        <span className="font-semibold">{a.actor_email || a.actor_id}</span>{" "}
                        <span className="text-muted-foreground">{a.action}</span>{" "}
                        <span className="font-mono text-[12px]">
                          {a.collection}/{a.doc_id}
                        </span>
                      </p>
                      <span className="text-[12px] text-muted-foreground">{a.timestamp}</span>
                    </div>
                  </li>
                ))
              )}
            </ol>
          </Panel>
        </section>
      )}
    </AppShell>
  );
}

function ReportsPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER"]}>
      <ReportsContent />
    </ProtectedRoute>
  );
}
