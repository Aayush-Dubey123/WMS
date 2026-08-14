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
} from "lucide-react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
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

const actionTileClass =
  "rounded-lg border border-border bg-card hover:bg-surface-hover p-4 transition-colors";

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

  const isLoading = summaryLoading || arrivalsLoading || ordersLoading;

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

  const summaryData = summary as Summary | undefined;
  const ordersList = ((orders as OrdersList | undefined)?.orders) ?? [];
  const arrivalsList = ((arrivals as ArrivedFeed | undefined)?.records) ?? [];

  const pendingOrders = ordersList.filter((o) => o.status === "PENDING").length;
  const reservedOrders = ordersList.filter((o) => o.status === "RESERVED").length;
  const packedOrders = ordersList.filter((o) => o.status === "PACKED").length;
  const shippedOrders = ordersList.filter((o) => o.status === "SHIPPED").length;

  const metrics = [
    { icon: PackageSearch, title: "Today's Arrivals", value: summaryData?.todays_tickets || 0, sub: "parcels received" },
    { icon: AlertCircle, title: "Pending Orders", value: pendingOrders, sub: "awaiting fulfillment" },
    { icon: CheckCircle2, title: "Items Sold Today", value: summaryData?.todays_sold || 0, sub: "units sold" },
    { icon: AlertCircle, title: "Unannounced Arrivals", value: summaryData?.arrived_missed || 0, sub: "no ticket on file" },
  ];

  const orderStatusChart = [
    { name: "Pending", value: pendingOrders, color: "var(--color-warning)" },
    { name: "Reserved", value: reservedOrders, color: "var(--color-info)" },
    { name: "Packed", value: packedOrders, color: "var(--color-primary)" },
    { name: "Shipped", value: shippedOrders, color: "var(--color-chart-4)" },
  ].filter((x) => x.value > 0);

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Executive Overview"
      actions={<Btn onClick={() => navigate({ to: "/orders" })}><Plus className="size-4" /> Create Order</Btn>}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MetricCard key={i} icon={m.icon} title={m.title} value={String(m.value)} sub={m.sub} />
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { icon: BarChart3, label: "View Reports", action: () => navigate({ to: "/reports" }) },
          { icon: Users, label: "Manage Users", action: () => navigate({ to: "/users" }) },
          { icon: Box, label: "Warehouses", action: () => navigate({ to: "/warehouses" }) },
          { icon: Zap, label: "Voice Pipeline", action: () => navigate({ to: "/voice" }) },
        ].map((btn, i) => (
          <button key={i} onClick={btn.action} className={actionTileClass}>
            <btn.icon className="size-6 text-primary mb-2" />
            <p className="text-sm font-semibold">{btn.label}</p>
          </button>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2 xl:grid-cols-3">
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

        <Panel className="lg:col-span-1">
          <h3 className="font-semibold">Today's Metrics</h3>
          <p className="text-xs text-muted-foreground mb-4">Quick overview</p>
          <div className="space-y-2">
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Arrivals</span><span className="font-bold text-base">{summaryData?.todays_tickets || 0}</span></div>
            <div className="h-px bg-border" />
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Sold</span><span className="font-bold text-base">{summaryData?.todays_sold || 0}</span></div>
            <div className="h-px bg-border" />
            <div className="flex justify-between items-center py-1.5"><span className="text-xs text-muted-foreground">Unannounced</span><span className="font-bold text-base">{summaryData?.arrived_missed || 0}</span></div>
          </div>
        </Panel>

        <Panel className="lg:col-span-1">
          <h3 className="font-semibold">Your Profile</h3>
          <p className="text-xs text-muted-foreground mb-4">Account info</p>
          <div className="space-y-3">
            <div className="bg-secondary rounded-lg p-3">
              <span className="text-xs text-muted-foreground">Name</span>
              <div className="font-bold text-sm mt-1">{user?.full_name}</div>
            </div>
            <div className="bg-secondary rounded-lg p-3">
              <span className="text-xs text-muted-foreground">Role</span>
              <div className="mt-2 inline-block rounded-md bg-info/15 px-2.5 py-1 text-xs font-bold text-info">
                {user?.role}
              </div>
            </div>
            {user?.email && (
              <div className="bg-secondary rounded-lg p-3">
                <span className="text-xs text-muted-foreground">Email</span>
                <div className="text-xs mt-1 truncate text-secondary-foreground">{user.email}</div>
              </div>
            )}
          </div>
        </Panel>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section>
          <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Today's Arrivals</h3><Link to="/tickets" className="text-[12px] font-semibold text-primary">View all</Link></>}>
            <thead><tr><Th>Ticket</Th><Th>Warehouse</Th><Th>Status</Th></tr></thead>
            <tbody>
              {arrivalsList.length > 0 ? (
                arrivalsList.slice(0, 5).map((a) => (
                  <Tr key={a.ticket_id}><Td className="font-mono text-xs">{a.ticket_id}</Td><Td className="text-xs text-muted-foreground">{a.warehouse_id}</Td><Td><StatusBadge status={a.status} /></Td></Tr>
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
              {ordersList.length > 0 ? (
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

  const today = new Date().toISOString().split("T")[0];
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
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  const ordersList = ((orders as OrdersList | undefined)?.orders) ?? [];
  const arrivalsList = ((arrivals as ArrivedFeed | undefined)?.records) ?? [];
  const approvalsList = ((approvals as ApprovalQueue | undefined)?.pending_tickets) ?? [];

  const pendingOrders = ordersList.filter((o) => o.status === "PENDING").length;
  const reservedOrders = ordersList.filter((o) => o.status === "RESERVED").length;
  const packedOrders = ordersList.filter((o) => o.status === "PACKED").length;

  const metrics = [
    { icon: AlertCircle, title: "Pending Approvals", value: approvalsList.length, sub: "tickets awaiting review" },
    { icon: PackageSearch, title: "Pending Orders", value: pendingOrders, sub: "waiting fulfillment" },
    { icon: Truck, title: "Reserved Stock", value: reservedOrders, sub: "orders picked" },
    { icon: CheckCircle2, title: "Ready to Ship", value: packedOrders, sub: "prepared items" },
  ];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Operations Manager"
      actions={<Btn onClick={() => navigate({ to: "/tickets" })}><Plus className="size-4" /> Log Arrival</Btn>}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MetricCard key={i} icon={m.icon} title={m.title} value={String(m.value)} sub={m.sub} />
        ))}
      </div>

      {approvalsList.length > 0 && (
        <Alert className="mt-6 border-destructive/40 bg-destructive/10 text-destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <strong className="text-lg">{approvalsList.length}</strong> tickets pending your approval — action required.
            <Link to="/tickets" className="ml-4 font-bold hover:underline">Review Now →</Link>
          </AlertDescription>
        </Alert>
      )}

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { icon: CheckCircle2, label: "Pending Approvals", count: approvalsList.length, action: () => navigate({ to: "/tickets" }) },
          { icon: PackageSearch, label: "Receiving Queue", count: arrivalsList.length, action: () => navigate({ to: "/tickets" }) },
          { icon: Users, label: "Team Management", count: "—", action: () => navigate({ to: "/users" }) },
        ].map((btn, i) => (
          <button key={i} onClick={btn.action} className={actionTileClass}>
            <div className="flex items-center justify-between">
              <div><btn.icon className="size-6 text-primary mb-2" /><p className="text-sm font-semibold">{btn.label}</p></div>
              <div className="text-2xl font-bold text-primary">{btn.count}</div>
            </div>
          </button>
        ))}
      </div>

      {approvalsList.length > 0 && (
        <section className="mt-6">
          <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Tickets Awaiting Approval</h3><span className="text-[12px] font-bold text-destructive">{approvalsList.length} action item(s)</span></>}>
            <thead>
              <tr>
                <Th>Ticket ID</Th>
                <Th>Warehouse</Th>
                <Th>Arrived</Th>
                <Th>Action</Th>
              </tr>
            </thead>
            <tbody>
              {approvalsList.map((ticket: any) => (
                <Tr key={ticket.id}>
                  <Td className="font-mono text-xs font-bold">{ticket.ticket_id}</Td>
                  <Td className="text-xs text-muted-foreground">{ticket.warehouse_id}</Td>
                  <Td className="text-xs text-muted-foreground">{ticket.created_at}</Td>
                  <Td>
                    <Link to="/tickets" className="px-3 py-1 rounded bg-primary text-primary-foreground text-xs font-bold hover:opacity-90">Review</Link>
                  </Td>
                </Tr>
              ))}
            </tbody>
          </TableShell>
        </section>
      )}

      <section className="mt-6">
        <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Recent Arrivals</h3><Link to="/tickets" className="text-[12px] font-semibold text-primary">View all</Link></>}>
          <thead><tr><Th>Ticket</Th><Th>Warehouse</Th><Th>Status</Th></tr></thead>
          <tbody>
            {arrivalsList.length > 0 ? (
              arrivalsList.slice(0, 5).map((a) => (
                <Tr key={a.ticket_id}><Td className="font-mono text-xs">{a.ticket_id}</Td><Td className="text-xs text-muted-foreground">{a.warehouse_id}</Td><Td><StatusBadge status={a.status} /></Td></Tr>
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

  const ordersList = ((orders as OrdersList | undefined)?.orders) ?? [];
  const ticketsList = ((tickets as TicketsList | undefined)?.tickets) ?? [];

  const pendingOrders = ordersList.filter((o) => o.status === "PENDING").length;
  const reservedOrders = ordersList.filter((o) => o.status === "RESERVED").length;
  const packedOrders = ordersList.filter((o) => o.status === "PACKED").length;
  const pendingApprovalTickets = ticketsList.filter((t) => t.status === "PENDING_APPROVAL").length;

  const metrics = [
    { icon: PackageSearch, title: "My Pending Tasks", value: pendingOrders, sub: "orders to fulfill" },
    { icon: Box, title: "Picking Queue", value: reservedOrders, sub: "items to pick" },
    { icon: Truck, title: "Ready to Pack", value: packedOrders, sub: "orders prepared" },
    { icon: Clock, title: "Tickets Awaiting Approval", value: pendingApprovalTickets, sub: "parcels received" },
  ];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Warehouse Operations"
      actions={<Btn onClick={() => navigate({ to: "/tickets" })}><Plus className="size-4" /> Log Arrival</Btn>}
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MetricCard key={i} icon={m.icon} title={m.title} value={String(m.value)} sub={m.sub} />
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          { icon: PackageSearch, label: "Fulfill Orders", count: pendingOrders, action: () => navigate({ to: "/orders" }) },
          { icon: Box, label: "Pick Items", count: reservedOrders, action: () => navigate({ to: "/orders" }) },
          { icon: Truck, label: "Pack & Ship", count: packedOrders, action: () => navigate({ to: "/orders" }) },
        ].map((btn, i) => (
          <button key={i} onClick={btn.action} className={actionTileClass}>
            <div className="flex items-center justify-between">
              <div><btn.icon className="size-6 text-primary mb-2" /><p className="text-sm font-semibold">{btn.label}</p></div>
              <div className="text-3xl font-bold text-primary">{btn.count}</div>
            </div>
          </button>
        ))}
      </div>

      <section className="mt-6">
        <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Your Tasks — Orders to Fulfill</h3><Link to="/orders" className="text-[12px] font-semibold text-primary">View all</Link></>}>
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
                    <Link to={`/orders/${order.id}`} className="px-3 py-1 rounded bg-info text-white text-xs font-bold hover:opacity-90">Fulfill</Link>
                  </Td>
                </Tr>
              ))
            ) : (
              <Tr><Td colSpan={4} className="py-4 text-center text-sm text-muted-foreground">No pending tasks</Td></Tr>
            )}
          </tbody>
        </TableShell>
      </section>

      <section className="mt-6">
        <TableShell toolbar={<><h3 className="mr-auto text-base font-semibold">Recent Tickets</h3><Link to="/tickets" className="text-[12px] font-semibold text-primary">View all</Link></>}>
          <thead><tr><Th>Ticket</Th><Th>Warehouse</Th><Th>Status</Th></tr></thead>
          <tbody>
            {ticketsList.length > 0 ? (
              ticketsList.slice(0, 5).map((t) => (
                <Tr key={t.id}><Td className="font-mono text-xs">{t.ticket_id}</Td><Td className="text-xs text-muted-foreground">{t.warehouse_id}</Td><Td><StatusBadge status={t.status} /></Td></Tr>
              ))
            ) : (
              <Tr><Td colSpan={3} className="py-4 text-center text-sm text-muted-foreground">No recent tickets</Td></Tr>
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
