import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import {
  Clock,
  PackageSearch,
  Plus,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Zap,
  Box,
  Truck,
  Users,
  BarChart3,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import { Btn, Panel, TableShell, Td, Th, Tr } from "@/components/wms/ui-bits";
import { reportsAPI, approvalsAPI, ordersAPI, ticketsAPI, warehousesAPI } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ProtectedRoute } from "@/lib/protected-route";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — Whitfield WMS" },
      {
        name: "description",
        content:
          "Live warehouse operations dashboard: orders, arrivals, fulfillment and operations.",
      },
    ],
  }),
  component: Dashboard,
});

type Summary = {
  todays_tickets?: number;
  todays_sold?: number;
  arrived_missed?: number;
  per_warehouse?: any[];
};
type ArrivedFeed = { records?: any[] };
type ApprovalQueue = { pending_tickets?: any[]; total?: number };
type OrdersList = { orders?: any[] };
type TicketsList = { tickets?: any[] };

/* ─── Shared UI Components ─── */

function KPICard({
  title,
  value,
  sub,
  icon: Icon,
}: {
  title: string;
  value: string | number;
  sub: string;
  icon: any;
}) {
  return (
    <div
      style={{
        background: "#fff",
        border: "1px solid var(--wf-border)",
        borderRadius: 16,
        padding: "24px",
        boxShadow: "var(--wf-shadow-sm)",
      }}
      className="flex flex-col justify-between"
    >
      <div>
        <div
          style={{
            background: "var(--wf-orange-pale)",
            color: "var(--wf-orange)",
          }}
          className="p-2.5 rounded-lg inline-block shrink-0"
        >
          <Icon className="size-5" />
        </div>
        <p className="text-[10px] text-muted-foreground font-extrabold uppercase mt-4 tracking-wider">
          {title}
        </p>
        <p className="text-3xl font-extrabold text-[var(--wf-dark)] font-outfit mt-1 leading-tight">
          {value}
        </p>
      </div>
      <p className="text-[11px] text-[#7A7A6E] mt-3 font-semibold">{sub}</p>
    </div>
  );
}

function QuickActionTile({
  label,
  sub,
  onClick,
  icon: Icon,
}: {
  label: string;
  sub: string;
  onClick: () => void;
  icon: any;
}) {
  return (
    <button
      onClick={onClick}
      style={{ border: "1px solid var(--wf-border)", boxShadow: "var(--wf-shadow-sm)" }}
      className="flex items-center justify-between p-4 rounded-xl bg-white hover:bg-[#FAF6F0] transition-colors duration-150 text-left w-full"
    >
      <div className="flex items-center gap-3">
        <div
          style={{ background: "var(--wf-orange-pale)", color: "var(--wf-orange)" }}
          className="p-2.5 rounded-lg shrink-0"
        >
          <Icon className="size-5" />
        </div>
        <div>
          <p className="text-sm font-bold text-[var(--wf-dark)] leading-tight">{label}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>
        </div>
      </div>
      <ChevronRight className="size-4 text-muted-foreground shrink-0" />
    </button>
  );
}

function WarehouseHealthGrid({ navigate, selectedWH }: { navigate: any; selectedWH: string }) {
  // Query actual warehouse records dynamically
  const { data: whResponse } = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehousesAPI.getAll(0, 100),
    staleTime: 30000,
  });
  const whList = (whResponse as any)?.warehouses || [];

  return (
    <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "24px" }} className="flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center justify-between mb-4 border-b border-[var(--wf-border)] pb-3">
          <div>
            <h3 className="font-extrabold text-base text-[var(--wf-dark)] font-outfit">Warehouse Health</h3>
            <p className="text-xs text-muted-foreground">Operational status</p>
          </div>
          <button
            onClick={() => navigate({ to: "/warehouses" })}
            className="text-xs font-bold text-[var(--wf-orange)] hover:underline"
          >
            View all warehouses
          </button>
        </div>

        <div className="space-y-3">
          {whList.map((wh: any) => {
            const isTargetSelected = wh.id === selectedWH;
            return (
              <div
                key={wh.id}
                onClick={() => navigate({ to: "/warehouses" })}
                style={{
                  borderColor: isTargetSelected ? "var(--wf-orange)" : "var(--wf-border)",
                  background: isTargetSelected ? "var(--wf-orange-pale)" : "transparent",
                }}
                className="flex items-center justify-between p-3 rounded-lg border hover:bg-[#FAF6F0] cursor-pointer transition-all duration-100"
              >
                <div className="flex items-center gap-3">
                  <div style={{ background: "var(--wf-orange-pale)", color: "var(--wf-orange)" }} className="p-2 rounded-lg">
                    <Box size={16} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-[var(--wf-dark)] leading-tight">{wh.name}</p>
                    <p className="text-[10px] text-muted-foreground mt-0.5">{wh.address || "Location Yard"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={cn(
                    "text-[10px] font-bold px-2 py-0.5 rounded-full",
                    wh.active ? "bg-green-50 text-green-700 border border-green-200" : "bg-amber-50 text-amber-700 border border-amber-200"
                  )}>
                    {wh.active ? "Healthy" : "Inactive"}
                  </span>
                  <span className="text-xs font-extrabold text-[var(--wf-dark)]">{wh.utilization || 0}% Utilized</span>
                </div>
              </div>
            );
          })}
          {whList.length === 0 && (
            <div className="py-4 text-center text-xs text-muted-foreground">No warehouses registered.</div>
          )}
        </div>
      </div>
    </Panel>
  );
}

// Generate real activity items from actual orders and arrivals datasets
function renderRealActivityFeed(orders: any[], arrivals: any[]) {
  const feed: { label: string; ref: string; detail: string; time: string }[] = [];

  if (orders.length > 0) {
    orders.slice(0, 2).forEach((o) => {
      feed.push({
        label: "Order Logged",
        ref: o.order_id || o.id,
        detail: o.customer_name || "Customer Record",
        time: "Fulfillment Log"
      });
    });
  }

  if (arrivals.length > 0) {
    arrivals.slice(0, 2).forEach((a) => {
      feed.push({
        label: "Arrival Scanned",
        ref: a.ticket_id || a.id,
        detail: `Facility: ${a.warehouse_id}`,
        time: "Inbound Log"
      });
    });
  }

  return (
    <div className="space-y-4">
      {feed.map((row, i) => (
        <div key={i} className="flex items-center justify-between py-2 border-b border-[var(--wf-border)] last:border-b-0 last:pb-0">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[var(--wf-orange-pale)] text-[var(--wf-orange)] shrink-0">
              <Zap size={16} />
            </div>
            <div>
              <p className="text-xs font-bold text-[var(--wf-dark)] leading-tight">{row.label}</p>
              <p className="text-[10px] text-muted-foreground font-mono mt-0.5">{row.ref}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs font-bold text-[#4A4A4A]">{row.detail}</p>
            <p className="text-[10px] text-muted-foreground mt-0.5">{row.time}</p>
          </div>
        </div>
      ))}
      {feed.length === 0 && (
        <div className="py-6 text-center text-xs text-muted-foreground">No recent database operations.</div>
      )}
    </div>
  );
}

/* ─── OWNER DASHBOARD ─── */
function OwnerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const today = new Date().toISOString().split("T")[0]!;

  // Hook for reacting to warehouse selector changes in header
  const [selectedWH, setSelectedWH] = useState(() => {
    return localStorage.getItem("selected_warehouse_id") || "ALL";
  });

  useEffect(() => {
    const handleWHChange = () => {
      setSelectedWH(localStorage.getItem("selected_warehouse_id") || "ALL");
    };
    window.addEventListener("warehouseChanged", handleWHChange);
    return () => window.removeEventListener("warehouseChanged", handleWHChange);
  }, []);

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["reports", "summary", today],
    queryFn: () => reportsAPI.getSummary(today),
    staleTime: 30000,
  });

  const { data: arrivals, isLoading: arrivalsLoading } = useQuery({
    queryKey: ["reports", "arrived-today", today],
    queryFn: () => reportsAPI.getArrivedToday(0, 5),
    staleTime: 30000,
  });

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => ordersAPI.getAll(0, 50),
    staleTime: 30000,
  });

  const isLoading = summaryLoading || arrivalsLoading || ordersLoading;

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-[var(--wf-orange)]" />
        </div>
      </AppShell>
    );
  }

  const summaryData = summary as Summary | undefined;
  const ordersList = ((orders as OrdersList | undefined)?.orders) ?? [];
  const arrivalsList = ((arrivals as ArrivedFeed | undefined)?.records) ?? [];

  // Filter lists by selected warehouse
  const filteredOrders = selectedWH === "ALL"
    ? ordersList
    : ordersList.filter((o) => o.warehouse_id === selectedWH || o.warehouse === selectedWH);

  const filteredArrivals = selectedWH === "ALL"
    ? arrivalsList
    : arrivalsList.filter((a) => a.warehouse_id === selectedWH);

  // Compute scoped summary KPIs from summary breakdown if filtered
  let arrivalsValue = summaryData?.todays_tickets ?? 0;
  let soldValue = summaryData?.todays_sold ?? 0;
  let unannouncedValue = summaryData?.arrived_missed ?? 0;

  if (selectedWH !== "ALL" && summaryData?.per_warehouse) {
    const whBreakdown = summaryData.per_warehouse.find((w) => w.warehouse_id === selectedWH);
    if (whBreakdown) {
      arrivalsValue = whBreakdown.todays_tickets ?? 0;
      soldValue = whBreakdown.todays_sold ?? 0;
      unannouncedValue = whBreakdown.arrived_missed ?? 0;
    } else {
      arrivalsValue = 0;
      soldValue = 0;
      unannouncedValue = 0;
    }
  }

  const pendingOrders = filteredOrders.filter((o) => o.status === "PENDING").length;
  const reservedOrders = filteredOrders.filter((o) => o.status === "RESERVED").length;
  const packedOrders = filteredOrders.filter((o) => o.status === "PACKED").length;
  const shippedOrders = filteredOrders.filter((o) => o.status === "SHIPPED").length;

  const orderStatusChart = [
    { name: "Pending", value: pendingOrders, color: "#F5A623" },
    { name: "Reserved", value: reservedOrders, color: "#3B82F6" },
    { name: "Packed", value: packedOrders, color: "#D4740B" },
    { name: "Shipped", value: shippedOrders, color: "#2E7D32" },
  ].filter((x) => x.value > 0);

  const chartTotal = orderStatusChart.reduce((sum, item) => sum + item.value, 0);

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Executive Overview"
      actions={
        <Btn onClick={() => navigate({ to: "/orders" })} className="bg-[var(--wf-orange)] hover:bg-[var(--wf-orange-hover)] text-white">
          <Plus className="size-4" /> Create Order
        </Btn>
      }
    >
      {/* KPIs Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Today's Arrivals"
          value={arrivalsValue}
          sub="parcels received"
          icon={PackageSearch}
        />
        <KPICard
          title="Pending Orders"
          value={pendingOrders}
          sub="awaiting fulfillment"
          icon={Clock}
        />
        <KPICard
          title="Items Sold Today"
          value={soldValue}
          sub="units sold"
          icon={CheckCircle2}
        />
        <KPICard
          title="Unannounced Arrivals"
          value={unannouncedValue}
          sub="no ticket on file"
          icon={AlertCircle}
        />
      </div>

      {/* Quick Actions Row */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <QuickActionTile
          label="View Reports"
          sub="Explore analytics"
          onClick={() => navigate({ to: "/reports" })}
          icon={BarChart3}
        />
        <QuickActionTile
          label="Manage Users"
          sub="Add or edit users"
          onClick={() => navigate({ to: "/users" })}
          icon={Users}
        />
        <QuickActionTile
          label="Warehouses"
          sub="Manage locations"
          onClick={() => navigate({ to: "/warehouses" })}
          icon={Box}
        />
        <QuickActionTile
          label="Voice Assistance"
          sub="Live voice operations"
          onClick={() => navigate({ to: "/voice" })}
          icon={Zap}
        />
      </div>

      {/* Mid Sections */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Order Status Donut Chart */}
        <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "24px" }} className="flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-base text-[var(--wf-dark)] font-outfit">Order Status</h3>
            <p className="text-xs text-muted-foreground mb-4">Distribution overview</p>
            {chartTotal > 0 ? (
              <div style={{ position: "relative", height: 180 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      isAnimationActive={false}
                      data={orderStatusChart}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={48}
                      outerRadius={68}
                      paddingAngle={3}
                    >
                      {orderStatusChart.map((d, idx) => (
                        <Cell key={idx} fill={d.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    textAlign: "center",
                    pointerEvents: "none",
                  }}
                >
                  <p style={{ fontSize: 24, fontWeight: 800, margin: 0, fontFamily: "'Outfit', sans-serif" }} className="text-[var(--wf-dark)]">
                    {chartTotal}
                  </p>
                  <p style={{ fontSize: 9, color: "var(--wf-muted)", margin: 0, fontWeight: 700, textTransform: "uppercase" }}>
                    Total Orders
                  </p>
                </div>
              </div>
            ) : (
              <div className="h-[180px] flex items-center justify-center text-xs text-muted-foreground">
                No orders logged.
              </div>
            )}

            <div className="mt-4 space-y-2">
              {orderStatusChart.map((item) => (
                <div key={item.name} className="flex items-center justify-between text-xs border-b border-[#FAF6F0] pb-1.5 last:border-0 last:pb-0">
                  <div className="flex items-center gap-2">
                    <div className="size-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-[#4A4A4A] font-semibold">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold text-[var(--wf-dark)]">{item.value}</span>
                    <span className="text-[10px] text-muted-foreground">
                      ({chartTotal > 0 ? ((item.value / chartTotal) * 100).toFixed(0) : 0}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <Link
            to="/reports"
            style={{ color: "var(--wf-orange)" }}
            className="text-xs font-bold mt-4 hover:underline inline-flex items-center gap-1"
          >
            View full report <ChevronRight size={14} />
          </Link>
        </Panel>

        {/* Today's Metrics */}
        <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "24px" }} className="flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-base text-[var(--wf-dark)] font-outfit">Today's Metrics</h3>
            <p className="text-xs text-muted-foreground mb-4">Quick overview</p>
            <div className="space-y-4">
              {[
                { label: "Arrivals", val: arrivalsValue },
                { label: "Sold Today", val: soldValue },
                { label: "Unannounced", val: unannouncedValue },
              ].map((m) => (
                <div key={m.label} className="flex justify-between items-center py-2 border-b border-[#FAF6F0] last:border-0 last:pb-0">
                  <span className="text-xs font-bold text-[#4A4A4A]">{m.label}</span>
                  <span className="font-bold text-sm text-[var(--wf-dark)]">{m.val}</span>
                </div>
              ))}
            </div>
          </div>
          <Link
            to="/reports"
            style={{ color: "var(--wf-orange)" }}
            className="text-xs font-bold mt-4 hover:underline inline-flex items-center gap-1"
          >
            View all metrics <ChevronRight size={14} />
          </Link>
        </Panel>

        {/* Your Profile */}
        <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "24px" }} className="flex flex-col justify-between relative">
          <div>
            <h3 className="font-extrabold text-base text-[var(--wf-dark)] font-outfit">Your Profile</h3>
            <p className="text-xs text-muted-foreground mb-4">Account information</p>

            <div className="space-y-3">
              <div className="bg-[#FAF6F0] border border-[var(--wf-border)] rounded-xl p-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#7A7A6E]">Name</span>
                <div className="font-bold text-sm text-[var(--wf-dark)] mt-0.5">{user?.full_name || "Guest User"}</div>
              </div>
              <div className="bg-[#FAF6F0] border border-[var(--wf-border)] rounded-xl p-3 flex justify-between items-center">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#7A7A6E]">Role</span>
                  <div className="mt-1">
                    <span className="rounded-md bg-[var(--wf-orange-pale)] px-2.5 py-0.5 text-xs font-bold text-[var(--wf-orange)] border border-[var(--wf-orange)]/25">
                      {user?.role || "OWNER"}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#7A7A6E] block">Status</span>
                  <span className="text-xs font-bold text-green-700 capitalize mt-1 block">
                    {user?.status || "active"}
                  </span>
                </div>
              </div>
              {user?.email && (
                <div className="bg-[#FAF6F0] border border-[var(--wf-border)] rounded-xl p-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#7A7A6E]">Email</span>
                  <div className="text-xs mt-0.5 truncate text-[var(--wf-dark-secondary)] font-medium">{user.email}</div>
                </div>
              )}
              {user?.experience_tier && (
                <div className="bg-[#FAF6F0] border border-[var(--wf-border)] rounded-xl p-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#7A7A6E]">Experience Tier</span>
                  <div className="text-xs mt-0.5 text-[var(--wf-dark-secondary)] font-bold">{user.experience_tier}</div>
                </div>
              )}
            </div>
          </div>
          <Link
            to="/settings"
            style={{ color: "var(--wf-orange)" }}
            className="text-xs font-bold mt-4 hover:underline inline-flex items-center gap-1"
          >
            View profile <ChevronRight size={14} />
          </Link>
        </Panel>
      </div>

      {/* Bottom Section */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity Feed */}
        <Panel style={{ background: "#fff", border: "1px solid var(--wf-border)", padding: "24px" }} className="flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-[var(--wf-border)] pb-3">
              <div>
                <h3 className="font-extrabold text-base text-[var(--wf-dark)] font-outfit">Recent Activity</h3>
                <p className="text-xs text-muted-foreground">Latest operations across the system</p>
              </div>
            </div>
            {renderRealActivityFeed(filteredOrders, filteredArrivals)}
          </div>
          <Link
            to="/reports"
            style={{ color: "var(--wf-orange)" }}
            className="text-xs font-bold mt-6 hover:underline inline-flex items-center gap-1"
          >
            View all activity <ChevronRight size={14} />
          </Link>
        </Panel>

        {/* Warehouse Health */}
        <WarehouseHealthGrid navigate={navigate} selectedWH={selectedWH} />
      </div>
    </AppShell>
  );
}

/* ─── MANAGER DASHBOARD ─── */
function ManagerDashboard() {
  const navigate = useNavigate();

  // Hook for reacting to warehouse selector changes in header
  const [selectedWH, setSelectedWH] = useState(() => {
    return localStorage.getItem("selected_warehouse_id") || "ALL";
  });

  useEffect(() => {
    const handleWHChange = () => {
      setSelectedWH(localStorage.getItem("selected_warehouse_id") || "ALL");
    };
    window.addEventListener("warehouseChanged", handleWHChange);
    return () => window.removeEventListener("warehouseChanged", handleWHChange);
  }, []);

  const { data: approvals, isLoading: approvalsLoading } = useQuery({
    queryKey: ["approvals"],
    queryFn: () => approvalsAPI.listPending(0, 10),
    staleTime: 30000,
  });

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => ordersAPI.getAll(0, 50),
    staleTime: 30000,
  });

  const today = new Date().toISOString().split("T")[0]!;
  const { data: arrivals, isLoading: arrivalsLoading } = useQuery({
    queryKey: ["reports", "arrived-today", today],
    queryFn: () => reportsAPI.getArrivedToday(0, 5),
    staleTime: 30000,
  });

  const isLoading = approvalsLoading || ordersLoading || arrivalsLoading;

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-[var(--wf-orange)]" />
        </div>
      </AppShell>
    );
  }

  const ordersList = ((orders as OrdersList | undefined)?.orders) ?? [];
  const arrivalsList = ((arrivals as ArrivedFeed | undefined)?.records) ?? [];
  const approvalsList = ((approvals as ApprovalQueue | undefined)?.pending_tickets) ?? [];

  // Filter lists by selected warehouse
  const filteredOrders = selectedWH === "ALL"
    ? ordersList
    : ordersList.filter((o) => o.warehouse_id === selectedWH || o.warehouse === selectedWH);

  const filteredApprovals = selectedWH === "ALL"
    ? approvalsList
    : approvalsList.filter((a) => a.warehouse_id === selectedWH);

  const pendingOrders = filteredOrders.filter((o) => o.status === "PENDING").length;
  const reservedOrders = filteredOrders.filter((o) => o.status === "RESERVED").length;
  const packedOrders = filteredOrders.filter((o) => o.status === "PACKED").length;

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Operations Manager Overview"
      actions={
        <Btn onClick={() => navigate({ to: "/tickets" })} className="bg-[var(--wf-orange)] hover:bg-[var(--wf-orange-hover)] text-white">
          <Plus className="size-4" /> Log Arrival
        </Btn>
      }
    >
      {/* KPIs Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Pending Approvals"
          value={filteredApprovals.length}
          sub="tickets awaiting review"
          icon={ShieldAlert}
        />
        <KPICard
          title="Pending Orders"
          value={pendingOrders}
          sub="waiting fulfillment"
          icon={Clock}
        />
        <KPICard
          title="Reserved Stock"
          value={reservedOrders}
          sub="orders picked"
          icon={Box}
        />
        <KPICard
          title="Ready to Ship"
          value={packedOrders}
          sub="prepared items"
          icon={Truck}
        />
      </div>

      {/* Warning alert if pending approvals */}
      {filteredApprovals.length > 0 && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 text-red-800 rounded-xl flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <AlertCircle className="size-5 shrink-0 text-red-600" />
            <p className="text-sm font-semibold">
              <strong className="text-base">{filteredApprovals.length}</strong> tickets require immediate approval to update storage counts.
            </p>
          </div>
          <Link to="/tickets" className="text-xs font-bold text-red-700 hover:underline">
            Review Now &rarr;
          </Link>
        </div>
      )}

      {/* Quick Actions Row */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <QuickActionTile
          label="Pending Approvals"
          sub="Review arrival inspection tickets"
          onClick={() => navigate({ to: "/tickets" })}
          icon={ShieldAlert}
        />
        <QuickActionTile
          label="Receiving Queue"
          sub="Manage active inbound trucks"
          onClick={() => navigate({ to: "/tickets" })}
          icon={PackageSearch}
        />
        <QuickActionTile
          label="Team Management"
          sub="Configure staff accounts"
          onClick={() => navigate({ to: "/users" })}
          icon={Users}
        />
      </div>

      {/* Grid: Approvals Queue + Warehouse Health */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Approvals table */}
        {filteredApprovals.length > 0 ? (
          <section>
            <TableShell
              toolbar={
                <>
                  <h3 className="mr-auto text-base font-extrabold text-[var(--wf-dark)] font-outfit">Tickets Awaiting Approval</h3>
                  <span className="text-[11px] font-bold text-red-600 px-2 py-0.5 rounded-full bg-red-100 border border-red-200">
                    {filteredApprovals.length} action item(s)
                  </span>
                </>
              }
            >
              <thead>
                <tr>
                  <Th>Ticket ID</Th>
                  <Th>Warehouse</Th>
                  <Th>Arrived</Th>
                  <Th>Action</Th>
                </tr>
              </thead>
              <tbody>
                {filteredApprovals.map((ticket: any) => (
                  <Tr key={ticket.id}>
                    <Td className="font-mono text-xs font-bold text-[var(--wf-dark)]">{ticket.ticket_id}</Td>
                    <Td className="text-xs text-muted-foreground">{ticket.warehouse_id}</Td>
                    <Td className="text-xs text-muted-foreground">{ticket.created_at}</Td>
                    <Td>
                      <Link
                        to="/tickets"
                        className="px-3 py-1 rounded bg-[var(--wf-orange)] text-white text-xs font-bold hover:bg-[var(--wf-orange-hover)]"
                      >
                        Review
                      </Link>
                    </Td>
                  </Tr>
                ))}
              </tbody>
            </TableShell>
          </section>
        ) : (
          <div className="bg-white border border-[var(--wf-border)] p-6 rounded-xl flex items-center justify-center text-xs text-muted-foreground h-full">
            No approval tickets pending for selector.
          </div>
        )}

        {/* Health */}
        <WarehouseHealthGrid navigate={navigate} selectedWH={selectedWH} />
      </div>
    </AppShell>
  );
}

/* ─── STAFF DASHBOARD ─── */
function StaffDashboard() {
  const navigate = useNavigate();

  // Hook for reacting to warehouse selector changes in header
  const [selectedWH, setSelectedWH] = useState(() => {
    return localStorage.getItem("selected_warehouse_id") || "ALL";
  });

  useEffect(() => {
    const handleWHChange = () => {
      setSelectedWH(localStorage.getItem("selected_warehouse_id") || "ALL");
    };
    window.addEventListener("warehouseChanged", handleWHChange);
    return () => window.removeEventListener("warehouseChanged", handleWHChange);
  }, []);

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => ordersAPI.getAll(0, 50),
    staleTime: 30000,
  });

  const { data: tickets, isLoading: ticketsLoading } = useQuery({
    queryKey: ["tickets"],
    queryFn: () => ticketsAPI.getAll(0, 20),
    staleTime: 30000,
  });

  const isLoading = ordersLoading || ticketsLoading;

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-[var(--wf-orange)]" />
        </div>
      </AppShell>
    );
  }

  const ordersList = ((orders as OrdersList | undefined)?.orders) ?? [];
  const ticketsList = ((tickets as TicketsList | undefined)?.tickets) ?? [];

  // Filter lists by selected warehouse
  const filteredOrders = selectedWH === "ALL"
    ? ordersList
    : ordersList.filter((o) => o.warehouse_id === selectedWH || o.warehouse === selectedWH);

  const filteredTickets = selectedWH === "ALL"
    ? ticketsList
    : ticketsList.filter((t) => t.warehouse_id === selectedWH);

  const pendingOrders = filteredOrders.filter((o) => o.status === "PENDING").length;
  const reservedOrders = filteredOrders.filter((o) => o.status === "RESERVED").length;
  const packedOrders = filteredOrders.filter((o) => o.status === "PACKED").length;
  const pendingApprovalTickets = filteredTickets.filter((t) => t.status === "PENDING_APPROVAL").length;

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Warehouse Operations"
      actions={
        <Btn onClick={() => navigate({ to: "/tickets" })} className="bg-[var(--wf-orange)] hover:bg-[var(--wf-orange-hover)] text-white">
          <Plus className="size-4" /> Log Arrival
        </Btn>
      }
    >
      {/* Metrics Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="My Pending Tasks"
          value={pendingOrders}
          sub="orders to fulfill"
          icon={Clock}
        />
        <KPICard
          title="Picking Queue"
          value={reservedOrders}
          sub="items to pick"
          icon={Box}
        />
        <KPICard
          title="Ready to Pack"
          value={packedOrders}
          sub="orders prepared"
          icon={Truck}
        />
        <KPICard
          title="Tickets Awaiting Approval"
          value={pendingApprovalTickets}
          sub="parcels received"
          icon={PackageSearch}
        />
      </div>

      {/* Quick Action Tiles */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <QuickActionTile
          label="Fulfill Orders"
          sub="Fulfillment lists"
          onClick={() => navigate({ to: "/orders" })}
          icon={PackageSearch}
        />
        <QuickActionTile
          label="Pick Items"
          sub="Items in reserve queue"
          onClick={() => navigate({ to: "/orders" })}
          icon={Box}
        />
        <QuickActionTile
          label="Pack & Ship"
          sub="Pack items in boxes"
          onClick={() => navigate({ to: "/orders" })}
          icon={Truck}
        />
      </div>

      {/* Tasks Table */}
      <div className="mt-8 grid grid-cols-1 gap-6">
        <section>
          <TableShell
            toolbar={
              <>
                <h3 className="mr-auto text-base font-extrabold text-[var(--wf-dark)] font-outfit">Your Tasks — Orders to Fulfill</h3>
                <Link to="/orders" className="text-xs font-bold text-[var(--wf-orange)] hover:underline">
                  View all
                </Link>
              </>
            }
          >
            <thead>
              <tr>
                <Th>Order ID</Th>
                <Th>Customer</Th>
                <Th>Status</Th>
                <Th>Action</Th>
              </tr>
            </thead>
            <tbody>
              {pendingOrders > 0 ? (
                filteredOrders
                  .filter((o) => o.status === "PENDING")
                  .slice(0, 5)
                  .map((order) => (
                    <Tr key={order.id}>
                      <Td className="font-mono text-xs font-bold text-[var(--wf-dark)]">{order.order_id}</Td>
                      <Td className="text-xs text-[var(--wf-dark-secondary)] font-medium">{order.customer_name}</Td>
                      <Td>
                        <StatusBadge status={order.status} />
                      </Td>
                      <Td>
                        <Link
                          to="/orders/$orderId"
                          params={{ orderId: order.id }}
                          className="px-3 py-1 rounded bg-[#3B82F6] text-white text-xs font-bold hover:opacity-90"
                        >
                          Fulfill
                        </Link>
                      </Td>
                    </Tr>
                  ))
              ) : (
                <Tr>
                  <Td colSpan={4} className="py-4 text-center text-sm text-muted-foreground">
                    No pending tasks
                  </Td>
                </Tr>
              )}
            </tbody>
          </TableShell>
        </section>
      </div>
    </AppShell>
  );
}

/* ─── Router DashboardContent ─── */
function DashboardContent() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-[var(--wf-orange)]" />
        </div>
      </AppShell>
    );
  }

  if (!user) {
    return (
      <AppShell>
        <div className="p-4 bg-red-50 border border-red-200 text-red-800 rounded-xl flex items-center gap-2">
          <AlertCircle />
          <p className="text-sm font-semibold">Not authenticated</p>
        </div>
      </AppShell>
    );
  }

  switch (user.role) {
    case "OWNER":
      return <OwnerDashboard />;
    case "MANAGER":
      return <ManagerDashboard />;
    case "STAFF":
      return <StaffDashboard />;
    default:
      return <StaffDashboard />;
  }
}

function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

// Custom cn utility inside route component to guarantee standalone resolving
function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
