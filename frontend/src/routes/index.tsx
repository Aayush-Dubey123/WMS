import { createFileRoute, Link } from "@tanstack/react-router";
import { Clock, DollarSign, Download, PackageSearch, Plus, ShieldAlert } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import {
  Btn,
  MetricCard,
  Panel,
  TableShell,
  Td,
  Th,
  Tr,
} from "@/components/wms/ui-bits";
import { activity, spark, statusDonut, warehouseBars } from "@/lib/wms-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — Whitfield WMS" },
      {
        name: "description",
        content:
          "Live warehouse operations dashboard: orders, revenue, fulfillment time and approval queue across all facilities.",
      },
      { property: "og:title", content: "Dashboard — Whitfield WMS" },
      {
        property: "og:description",
        content: "Live warehouse operations dashboard for orders, arrivals and fulfillment.",
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

function Dashboard() {
  return (
    <AppShell
      crumbs={[{ label: "Dashboard" }]}
      title="Operations Overview"
      actions={
        <>
          <Btn variant="secondary">
            <Download className="size-4" /> Export
          </Btn>
          <Btn>
            <Plus className="size-4" /> Create Order
          </Btn>
        </>
      }
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={PackageSearch}
          title="Total Orders"
          value="1,284"
          trend={12}
          sub="vs. previous 30 days"
          data={spark(1)}
        />
        <MetricCard
          icon={DollarSign}
          title="Total Revenue"
          value="$482,940"
          trend={8}
          sub="net of returns"
          data={spark(3)}
        />
        <MetricCard
          icon={Clock}
          title="Avg Fulfillment"
          value="6h 12m"
          trend={-4}
          sub="pick to ship"
          data={spark(5)}
        />
        <MetricCard
          icon={ShieldAlert}
          title="Pending Approvals"
          value="17"
          trend={3}
          sub="manager review queue"
          data={spark(7)}
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel>
          <h3>Order Status Breakdown</h3>
          <p className="mt-1 text-[12px] text-muted-foreground">Across all warehouses, last 30 days</p>
          <div className="mt-4 h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  isAnimationActive={false}
                  data={statusDonut}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={65}
                  outerRadius={100}
                  paddingAngle={3}
                  stroke="none"
                >
                  {statusDonut.map((d) => (
                    <Cell key={d.name} fill={d.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel>
          <h3>Warehouse Comparison</h3>
          <p className="mt-1 text-[12px] text-muted-foreground">Orders processed per facility</p>
          <div className="mt-4 h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={warehouseBars}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#9CA3AF" }} axisLine={false} />
                <YAxis tick={{ fontSize: 12, fill: "#9CA3AF" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar isAnimationActive={false} dataKey="orders" fill="var(--color-primary)" radius={[6, 6, 0, 0]} barSize={48} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <section className="mt-6">
        <TableShell
          toolbar={
            <>
              <h3 className="mr-auto text-base font-semibold">Recent Activity</h3>
              <Link to="/reports" className="text-[12px] font-semibold text-primary hover:underline">
                View all
              </Link>
            </>
          }
        >
          <thead>
            <tr>
              <Th>Timestamp</Th>
              <Th>Event Type</Th>
              <Th>Actor</Th>
              <Th>Reference</Th>
              <Th>Status</Th>
            </tr>
          </thead>
          <tbody>
            {activity.map((a, i) => (
              <Tr key={i}>
                <Td className="font-mono text-[12px] text-muted-foreground">Aug 13 · {a.time}</Td>
                <Td className="font-medium">{a.type.replace(/_/g, " ")}</Td>
                <Td className="text-secondary-foreground">{a.actor}</Td>
                <Td className="font-mono text-[12px] text-muted-foreground">{a.ref}</Td>
                <Td>
                  <StatusBadge status={a.status} />
                </Td>
              </Tr>
            ))}
          </tbody>
        </TableShell>
      </section>
    </AppShell>
  );
}
