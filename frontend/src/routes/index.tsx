import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import {
  Clock,
  PackageSearch,
  Plus,
  ShieldAlert,
  Loader2,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Zap,
  Box,
  Truck,
  Users,
  BarChart3,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  LineChart,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import { Btn, MetricCard, Panel, TableShell, Td, Th, Tr } from "@/components/wms/ui-bits";
import { reportsAPI, approvalsAPI, ordersAPI, ticketsAPI } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ProtectedRoute } from "@/lib/protected-route";
import { Alert, AlertDescription } from "@/components/ui/alert";

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

const tooltipStyle = {
  background: "var(--color-card)",
  border: "1px solid var(--color-border)",
  borderRadius: 8,
  fontSize: 12,
};

// OWNER DASHBOARD - Executive view with full analytics
function OwnerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const today = new Date().toISOString().split("T")[0];

  const { data: summary, isLoading: summaryLoading, error: summaryError } = useQuery({
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

  const { data: tickets, isLoading: ticketsLoading } = useQuery({
    queryKey: ["tickets"],
    queryFn: () => ticketsAPI.getAll(0, 50),
    staleTime: 30000,
  });

  const isLoading = summaryLoading || arrivalsLoading || ordersLoading || ticketsLoading;

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  if (summaryError) {
    return (
      <AppShell>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>Failed to load dashboard data.</AlertDescription>
        </Alert>
      </AppShell>
    );
  }

  const ordersList = Array.isArray(orders) ? orders : orders?.orders || [];
  const arrivalsList = Array.isArray(arrivals) ? arrivals : arrivals?.arrivals || [];

  const pendingOrders = ordersList.filter((o) => o.status === "PENDING").length;
  const packedOrders = ordersList.filter((o) => o.status === "PACKED").length;
  const shippedOrders = ordersList.filter((o) => o.status === "SHIPPED").length;

  const metrics = [
    { icon: PackageSearch, title: "Today's Arrivals", value: summary?.todays_tickets || 0, trend: 2, sub: "parcels received" },
    { icon: AlertCircle, title: "Pending Orders", value: pendingOrders, trend: 1, sub: "awaiting fulfillment" },
    { icon: TrendingUp, title: "Items Stored", value: summary?.todays_stored || 0, trend: -1, sub: "in inventory" },
    { icon: CheckCircle2, title: "Shipped Today", value: summary?.todays_sold || 0, trend: 3, sub: "orders completed" },
  ];

  const orderStatusChart = [
    { name: "Pending", value: pendingOrders, color: "#fbbf24" },
    { name: "Reserved", value: ordersList.filter((o) => o.status === "RESERVED").length, color: "#60a5fa" },
    { name: "Packed", value: packedOrders, color: "#10b981" },
    { name: "Shipped", value: shippedOrders, color: "#8b5cf6" },
  ].filter((x) => x.value > 0);

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Executive Overview"
      actions={<Btn onClick={() => navigate({ to: "/orders" })}><Plus className="size-4" /> Create Order</Btn>}
    >
      {/* Owner Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MetricCard key={i} icon={m.icon} title={m.title} value={String(m.value)} trend={m.trend} sub={m.sub} data={[]} />
        ))}
      </div>

      {/* Owner-specific controls */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { icon: BarChart3, label: "View Reports", action: () => navigate({ to: "/reports" }) },
          { icon: Users, label: "Manage Users", action: () => navigate({ to: "/users" }) },
          { icon: Box, label: "Warehouses", action: () => navigate({ to: "/warehouses" }) },
          { icon: Zap, label: "Voice Pipeline", action: () => navigate({ to: "/voice" }) },
        ].map((btn, i) => (
          <button
            key={i}
            onClick={btn.action}
            className="rounded-lg border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/50 hover:from-slate-700/50 hover:to-slate-800/50 p-4 transition-all"
          >
            <btn.icon className="size-6 text-primary mb-2" />
            <p className="text-sm font-semibold">{btn.label}</p>
          </button>
        ))}
      </div>

      {/* Charts Grid - Balanced Layout */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {/* Chart - Full width on mobile, 2 cols on desktop */}
        {orderStatusChart.length > 0 && (
          <Panel className="lg:col-span-1">
            <h3 className="font-semibold">Order Status</h3>
            <p className="text-xs text-muted-foreground mb-4">Distribution</p>
            <div className="mt-2 h-[180px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie isAnimationActive={false} data={orderStatusChart} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={50}>
                    {orderStatusChart.map((d, idx) => (
                      <Cell key={idx} fill={d.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 space-y-1.5">
              {orderStatusChart.map((item) => (
                <div key={item.name} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="size-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-muted-foreground">{item.name}</span>
                  </div>
                  <span className="font-semibold">{item.value}</span>
                </div>
              ))}
            </div>
          </Panel>
        )}

        {/* Summary Card */}
        <Panel className="lg:col-span-1">
          <h3 className="font-semibold">Today's Metrics</h3>
          <p className="text-xs text-muted-foreground mb-4">Quick overview</p>
          <div className="space-y-2">
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Arrivals</span><span className="font-bold text-base">{summary?.todays_tickets || 0}</span></div>
            <div className="h-px bg-border/50" />
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Pending</span><span className="font-bold text-base">{summary?.pending_approvals || 0}</span></div>
            <div className="h-px bg-border/50" />
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Stored</span><span className="font-bold text-base">{summary?.todays_stored || 0}</span></div>
            <div className="h-px bg-border/50" />
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Shipped</span><span className="font-bold text-base">{summary?.todays_sold || 0}</span></div>
          </div>
        </Panel>

        {/* Account Card - Improved styling */}
        <Panel className="lg:col-span-1">
          <h3 className="font-semibold">Your Profile</h3>
          <p className="text-xs text-muted-foreground mb-4">Account info</p>
          <div className="space-y-3">
            <div className="bg-slate-700/20 rounded-lg p-3">
              <span className="text-xs text-muted-foreground">Name</span>
              <div className="font-bold text-sm mt-1">{user?.full_name}</div>
            </div>
            <div className="bg-slate-700/20 rounded-lg p-3">
              <span className="text-xs text-muted-foreground">Role</span>
              <div className="mt-2 inline-block rounded-md bg-blue-500/20 px-2.5 py-1 text-xs font-bold text-blue-300">
                {user?.role}
              </div>
            </div>
            {user?.email && (
              <div className="bg-slate-700/20 rounded-lg p-3">
                <span className="text-xs text-muted-foreground">Email</span>
                <div className="text-xs mt-1 truncate text-slate-300">{user.email}</div>
              </div>
            )}
          </div>
        </Panel>
      </div>

      {/* Recent tables */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section>
          <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Today's Arrivals</h3><Link to="/tickets" className="text-[12px] font-semibold text-primary">View all</Link></>}>
            <thead><tr><Th>Ticket</Th><Th>Items</Th><Th>Status</Th></tr></thead>
            <tbody>
              {arrivalsList?.length > 0 ? (
                arrivalsList.slice(0, 5).map((a) => (
                  <Tr key={a.id}><Td className="font-mono text-xs">{a.ticket_id}</Td><Td>{a.item_count || 0}</Td><Td><StatusBadge status={a.status} /></Td></Tr>
                ))
              ) : (
                <Tr><Td colSpan={3} className="py-4 text-center text-sm text-muted-foreground">No arrivals</Td></Tr>
              )}
            </tbody>
          </TableShell>
        </section>

        <section>
          <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Recent Orders</h3><Link to="/orders" className="text-[12px] font-semibold text-primary">View all</Link></>}>
            <thead><tr><Th>Order ID</Th><Th>Customer</Th><Th>Status</Th></tr></thead>
            <tbody>
              {ordersList?.length > 0 ? (
                ordersList.slice(0, 5).map((order) => (
                  <Tr key={order.id}><Td className="font-mono text-xs">{order.order_id}</Td><Td>{order.customer_name}</Td><Td><StatusBadge status={order.status} /></Td></Tr>
                ))
              ) : (
                <Tr><Td colSpan={3} className="py-4 text-center text-sm text-muted-foreground">No orders</Td></Tr>
              )}
            </tbody>
          </TableShell>
        </section>
      </div>
    </AppShell>
  );
}

// MANAGER DASHBOARD - Operational view with approval focus
function ManagerDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const today = new Date().toISOString().split("T")[0];

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["reports", "summary", today],
    queryFn: () => reportsAPI.getSummary(today),
    staleTime: 30000,
  });

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

  const { data: arrivals, isLoading: arrivalsLoading } = useQuery({
    queryKey: ["reports", "arrived-today", today],
    queryFn: () => reportsAPI.getArrivedToday(0, 5),
    staleTime: 30000,
  });

  const isLoading = summaryLoading || approvalsLoading || ordersLoading || arrivalsLoading;

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  const ordersList = Array.isArray(orders) ? orders : orders?.orders || [];
  const arrivalsList = Array.isArray(arrivals) ? arrivals : arrivals?.arrivals || [];
  const approvalsData = Array.isArray(approvals) ? approvals : [];

  const pendingOrders = ordersList.filter((o) => o.status === "PENDING").length;
  const reservedOrders = ordersList.filter((o) => o.status === "RESERVED").length;
  const packedOrders = ordersList.filter((o) => o.status === "PACKED").length;

  const metrics = [
    { icon: AlertCircle, title: "Pending Approvals", value: approvalsData.length, trend: approvalsData.length > 3 ? -1 : 1, sub: "tickets awaiting review" },
    { icon: PackageSearch, title: "Pending Orders", value: pendingOrders, trend: 1, sub: "waiting fulfillment" },
    { icon: Truck, title: "Reserved Stock", value: reservedOrders, trend: 2, sub: "orders picked" },
    { icon: CheckCircle2, title: "Ready to Ship", value: packedOrders, trend: 3, sub: "prepared items" },
  ];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Operations Manager"
      actions={<Btn onClick={() => navigate({ to: "/tickets" })}><Plus className="size-4" /> Log Arrival</Btn>}
    >
      {/* Manager Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MetricCard key={i} icon={m.icon} title={m.title} value={String(m.value)} trend={m.trend} sub={m.sub} data={[]} />
        ))}
      </div>

      {/* CRITICAL: Pending Approvals Alert */}
      {approvalsData.length > 0 && (
        <Alert className="mt-6 border-red-600 bg-red-50 text-red-900">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong className="text-lg">{approvalsData.length}</strong> tickets pending your approval - Action required!
            <Link to="/tickets" className="ml-4 font-bold text-red-700 hover:underline">Review Now →</Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Manager controls */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { icon: CheckCircle2, label: "Pending Approvals", count: approvalsData.length, action: () => navigate({ to: "/tickets" }) },
          { icon: PackageSearch, label: "Receiving Queue", count: arrivalsList.length, action: () => navigate({ to: "/tickets" }) },
          { icon: Users, label: "Team Management", count: "∞", action: () => navigate({ to: "/users" }) },
        ].map((btn, i) => (
          <button
            key={i}
            onClick={btn.action}
            className="rounded-lg border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/50 hover:from-slate-700/50 hover:to-slate-800/50 p-4 transition-all"
          >
            <div className="flex items-center justify-between">
              <div><btn.icon className="size-6 text-primary mb-2" /><p className="text-sm font-semibold">{btn.label}</p></div>
              <div className="text-2xl font-bold text-primary">{btn.count}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Pending Approvals Table - Most Important for Manager */}
      {approvalsData.length > 0 && (
        <section className="mt-6">
          <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Tickets Awaiting Approval</h3><span className="text-[12px] font-bold text-red-600">{approvalsData.length} action item(s)</span></>}>
            <thead>
              <tr>
                <Th>Ticket ID</Th>
                <Th>Items</Th>
                <Th>Arrived</Th>
                <Th>Priority</Th>
                <Th>Action</Th>
              </tr>
            </thead>
            <tbody>
              {approvalsData.map((ticket) => (
                <Tr key={ticket.id}>
                  <Td className="font-mono text-xs font-bold">{ticket.ticket_id}</Td>
                  <Td className="text-sm">{ticket.item_count || 0}</Td>
                  <Td className="text-xs text-muted-foreground">{ticket.created_at}</Td>
                  <Td><span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-bold">URGENT</span></Td>
                  <Td>
                    <Link to={`/tickets`} className="px-3 py-1 rounded bg-primary text-white text-xs font-bold hover:opacity-80">Review</Link>
                  </Td>
                </Tr>
              ))}
            </tbody>
          </TableShell>
        </section>
      )}

      {/* Recent arrivals */}
      <section className="mt-6">
        <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Recent Arrivals</h3><Link to="/tickets" className="text-[12px] font-semibold text-primary">View all</Link></>}>
          <thead><tr><Th>Ticket</Th><Th>Items</Th><Th>Status</Th></tr></thead>
          <tbody>
            {arrivalsList?.length > 0 ? (
              arrivalsList.slice(0, 5).map((a) => (
                <Tr key={a.id}><Td className="font-mono text-xs">{a.ticket_id}</Td><Td>{a.item_count || 0}</Td><Td><StatusBadge status={a.status} /></Td></Tr>
              ))
            ) : (
              <Tr><Td colSpan={3} className="py-4 text-center text-sm text-muted-foreground">No recent arrivals</Td></Tr>
            )}
          </tbody>
        </TableShell>
      </section>
    </AppShell>
  );
}

// STAFF DASHBOARD - Task-focused operational view
function StaffDashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();

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
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  const ordersList = Array.isArray(orders) ? orders : orders?.orders || [];
  const ticketsList = Array.isArray(tickets) ? tickets : tickets?.tickets || [];

  const pendingOrders = ordersList.filter((o) => o.status === "PENDING").length;
  const reservedOrders = ordersList.filter((o) => o.status === "RESERVED").length;
  const packedOrders = ordersList.filter((o) => o.status === "PACKED").length;
  const receivedTickets = ticketsList.filter((t) => t.status === "RECEIVED").length;

  const metrics = [
    { icon: PackageSearch, title: "My Pending Tasks", value: pendingOrders, trend: 1, sub: "orders to fulfill" },
    { icon: Box, title: "Picking Queue", value: reservedOrders, trend: 2, sub: "items to pick" },
    { icon: Truck, title: "Ready to Pack", value: packedOrders, trend: 2, sub: "orders prepared" },
    { icon: Clock, title: "Arrivals to Log", value: receivedTickets, trend: 1, sub: "parcels received" },
  ];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Warehouse Operations"
      actions={<Btn onClick={() => navigate({ to: "/tickets" })}><Plus className="size-4" /> Log Arrival</Btn>}
    >
      {/* Staff Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MetricCard key={i} icon={m.icon} title={m.title} value={String(m.value)} trend={m.trend} sub={m.sub} data={[]} />
        ))}
      </div>

      {/* Staff Quick Actions */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { icon: PackageSearch, label: "Fulfill Orders", count: pendingOrders, action: () => navigate({ to: "/orders" }), color: "blue" },
          { icon: Box, label: "Pick Items", count: reservedOrders, action: () => navigate({ to: "/orders" }), color: "purple" },
          { icon: Truck, label: "Pack & Ship", count: packedOrders, action: () => navigate({ to: "/orders" }), color: "green" },
        ].map((btn, i) => (
          <button
            key={i}
            onClick={btn.action}
            className={`rounded-lg border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/50 hover:from-slate-700/50 hover:to-slate-800/50 p-4 transition-all`}
          >
            <div className="flex items-center justify-between">
              <div><btn.icon className={`size-6 mb-2`} style={{ color: btn.color === "blue" ? "#06b6d4" : btn.color === "purple" ? "#a78bfa" : "#10b981" }} /><p className="text-sm font-semibold">{btn.label}</p></div>
              <div className="text-3xl font-bold text-primary">{btn.count}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Orders to Fulfill */}
      <section className="mt-6">
        <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Your Tasks - Orders to Fulfill</h3><Link to="/orders" className="text-[12px] font-semibold text-primary">View all</Link></>}>
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
              ordersList.filter((o) => o.status === "PENDING").slice(0, 5).map((order) => (
                <Tr key={order.id}>
                  <Td className="font-mono text-xs font-bold">{order.order_id}</Td>
                  <Td className="text-sm">{order.customer_name}</Td>
                  <Td><StatusBadge status={order.status} /></Td>
                  <Td>
                    <button className="px-3 py-1 rounded bg-blue-500 text-white text-xs font-bold hover:opacity-80">Fulfill</button>
                  </Td>
                </Tr>
              ))
            ) : (
              <Tr><Td colSpan={4} className="py-4 text-center text-sm text-muted-foreground">No pending tasks</Td></Tr>
            )}
          </tbody>
        </TableShell>
      </section>

      {/* Arrival Log */}
      <section className="mt-6">
        <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Recent Arrivals</h3><Link to="/tickets" className="text-[12px] font-semibold text-primary">View all</Link></>}>
          <thead><tr><Th>Ticket</Th><Th>Items</Th><Th>Status</Th></tr></thead>
          <tbody>
            {ticketsList?.length > 0 ? (
              ticketsList.slice(0, 5).map((t) => (
                <Tr key={t.id}><Td className="font-mono text-xs">{t.ticket_id}</Td><Td>{t.item_count || 0}</Td><Td><StatusBadge status={t.status} /></Td></Tr>
              ))
            ) : (
              <Tr><Td colSpan={3} className="py-4 text-center text-sm text-muted-foreground">No recent arrivals logged</Td></Tr>
            )}
          </tbody>
        </TableShell>
      </section>
    </AppShell>
  );
}

// Router to correct dashboard based on role
function DashboardContent() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  if (!user) {
    return <AppShell><Alert variant="destructive"><AlertCircle /><AlertDescription>Not authenticated</AlertDescription></Alert></AppShell>;
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
