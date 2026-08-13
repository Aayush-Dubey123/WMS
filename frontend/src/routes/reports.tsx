import { createFileRoute } from "@tanstack/react-router";
import { AlertOctagon, Clock, Download, PackageCheck, Ticket } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
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
  Field,
  MetricCard,
  Panel,
  TableShell,
  Td,
  Th,
  Tr,
} from "@/components/wms/ui-bits";
import {
  activity,
  spark,
  statusDonut,
  stockRows,
  trendData,
  warehouseBars,
  warehouseList,
} from "@/lib/wms-data";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Analytics & Reports — Whitfield WMS" },
      {
        name: "description",
        content:
          "Executive warehouse analytics: throughput trends, inventory summary, unannounced arrivals and processing times.",
      },
      { property: "og:title", content: "Analytics & Reports — Whitfield WMS" },
      {
        property: "og:description",
        content: "Warehouse throughput trends, inventory summary and processing analytics.",
      },
    ],
  }),
  component: ReportsPage,
});

const tooltipStyle = {
  background: "var(--color-card)",
  border: "1px solid var(--color-border)",
  borderRadius: 8,
  fontSize: 12,
};

function ReportsPage() {
  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Reports" }]}
      title="Analytics & Reports"
      actions={
        <>
          <Field type="date" className="w-[150px]" />
          <Field type="date" className="w-[150px]" />
          <Btn variant="secondary">
            <Download className="size-4" /> Export CSV
          </Btn>
        </>
      }
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Ticket} title="Tickets Created Today" value="38" trend={9} data={spark(2)} />
        <MetricCard icon={PackageCheck} title="Items Sold Today" value="612" trend={14} data={spark(4)} />
        <MetricCard icon={AlertOctagon} title="Unannounced Arrivals" value="5" trend={-11} data={spark(6)} />
        <MetricCard icon={Clock} title="Avg Processing Time" value="42m" trend={-6} data={spark(8)} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel>
          <h3>Order Status Breakdown</h3>
          <div className="mt-4 h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie isAnimationActive={false} data={statusDonut} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={3} stroke="none">
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
          <div className="mt-4 h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={warehouseBars}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#9CA3AF" }} axisLine={false} />
                <YAxis tick={{ fontSize: 12, fill: "#9CA3AF" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
                <Bar isAnimationActive={false} dataKey="orders" fill="var(--color-info)" radius={[6, 6, 0, 0]} barSize={48} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel>
          <h3>Trend Over Time</h3>
          <div className="mt-4 h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 12, fill: "#9CA3AF" }} axisLine={false} />
                <YAxis tick={{ fontSize: 12, fill: "#9CA3AF" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line isAnimationActive={false} type="monotone" dataKey="orders" stroke="var(--color-primary)" strokeWidth={2} dot={false} />
                <Line isAnimationActive={false} type="monotone" dataKey="arrivals" stroke="var(--color-warning)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel>
          <h3>Inventory Heatmap</h3>
          <p className="mt-1 text-[12px] text-muted-foreground">Bin utilization per warehouse zone</p>
          <div className="mt-5 space-y-4">
            {warehouseList.map((w) => (
              <div key={w.code}>
                <div className="mb-2 flex items-center justify-between text-[12px]">
                  <span className="font-semibold">{w.code} · {w.name}</span>
                  <span className="text-muted-foreground">{w.utilization}%</span>
                </div>
                <div className="grid grid-cols-12 gap-1">
                  {Array.from({ length: 24 }, (_, i) => {
                    const intensity = Math.min(1, (w.utilization / 100) * (0.5 + ((i * 7) % 10) / 10));
                    return (
                      <span
                        key={i}
                        className="h-5 rounded-sm"
                        style={{ background: `rgba(16,185,129,${(0.12 + intensity * 0.75).toFixed(2)})` }}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <section className="mt-6">
        <TableShell toolbar={<h3 className="text-base font-semibold">Inventory Summary</h3>}>
          <thead>
            <tr>
              <Th>SKU</Th>
              <Th>Product</Th>
              <Th>Warehouse</Th>
              <Th className="text-right">On Hand</Th>
              <Th className="text-right">Available</Th>
              <Th className="text-right">Reserved</Th>
              <Th className="text-right">Damaged</Th>
              <Th>Last Modified</Th>
            </tr>
          </thead>
          <tbody>
            {stockRows.map((r) => (
              <Tr key={r.sku}>
                <Td className="font-mono text-[12px] text-muted-foreground">{r.sku}</Td>
                <Td className="font-medium">{r.product}</Td>
                <Td className="text-[12px] text-muted-foreground">{r.warehouse}</Td>
                <Td className="text-right">{r.onHand}</Td>
                <Td className="text-right font-semibold text-primary">{r.available}</Td>
                <Td className="text-right text-warning">{r.reserved}</Td>
                <Td className="text-right text-destructive">{r.damaged}</Td>
                <Td className="text-[12px] text-muted-foreground">{r.modified}</Td>
              </Tr>
            ))}
          </tbody>
        </TableShell>
      </section>

      <section className="mt-6">
        <Panel>
          <h3>Recent Activity</h3>
          <ol className="mt-4 space-y-4 border-l border-border pl-5">
            {activity.slice(0, 6).map((a, i) => (
              <li key={i} className="relative">
                <span className="absolute top-1.5 -left-[26px] size-2.5 rounded-full bg-primary" />
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm">
                    <span className="font-semibold">{a.actor}</span>{" "}
                    <span className="text-muted-foreground">{a.type.replace(/_/g, " ").toLowerCase()}</span>{" "}
                    <span className="font-mono text-[12px]">{a.ref}</span>
                  </p>
                  <div className="flex items-center gap-3">
                    <StatusBadge status={a.status} />
                    <span className="text-[12px] text-muted-foreground">Aug 13 · {a.time}</span>
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </Panel>
      </section>
    </AppShell>
  );
}
