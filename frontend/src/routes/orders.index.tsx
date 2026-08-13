import { createFileRoute, Link } from "@tanstack/react-router";
import { Download, Filter, MoreHorizontal, Plus } from "lucide-react";
import { useMemo, useState } from "react";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import {
  Btn,
  Field,
  Pager,
  SearchField,
  Select,
  TableShell,
  Td,
  Th,
  Tr,
} from "@/components/wms/ui-bits";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { orders } from "@/lib/wms-data";

export const Route = createFileRoute("/orders/")({
  head: () => ({
    meta: [
      { title: "Orders & Fulfillment — Whitfield WMS" },
      {
        name: "description",
        content:
          "Search, filter and fulfill customer orders: reserve stock, pack, generate labels and ship from any warehouse.",
      },
      { property: "og:title", content: "Orders & Fulfillment — Whitfield WMS" },
      {
        property: "og:description",
        content: "Reserve, pack, label and ship customer orders across warehouses.",
      },
    ],
  }),
  component: OrdersPage,
});

function OrdersPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("ALL");
  const [selected, setSelected] = useState<string[]>([]);

  const rows = useMemo(
    () =>
      orders.filter(
        (o) =>
          (status === "ALL" || o.status === status) &&
          (o.id.toLowerCase().includes(query.toLowerCase()) ||
            o.customer.toLowerCase().includes(query.toLowerCase())),
      ),
    [query, status],
  );

  const toggle = (id: string) =>
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Orders" }]}
      title="Orders"
      actions={
        <>
          <Btn variant="secondary">
            <Filter className="size-4" /> Filter
          </Btn>
          <Btn variant="secondary">
            <Download className="size-4" /> Export
          </Btn>
          <Btn>
            <Plus className="size-4" /> Create Order
          </Btn>
        </>
      }
    >
      <div className="sticky top-16 z-20 mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-border bg-card p-4 shadow-e1">
        <SearchField
          className="w-full sm:w-[280px]"
          placeholder="Search order ID or customer..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="ALL">All statuses</option>
          {["PENDING", "RESERVED", "PACKED", "SHIPPED", "ERROR"].map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </Select>
        <Select defaultValue="ALL">
          <option value="ALL">All warehouses</option>
          <option>WHT-01 · Whitfield North</option>
          <option>WHT-02 · Dalton Yard</option>
          <option>WHT-03 · Redmoor</option>
        </Select>
        <Field type="date" className="w-[160px]" />
        <Field type="date" className="w-[160px]" />
        <button
          onClick={() => {
            setQuery("");
            setStatus("ALL");
          }}
          className="text-[12px] font-semibold text-primary hover:underline"
        >
          Clear all
        </button>
        {selected.length > 0 && (
          <Btn variant="danger" className="ml-auto">
            Delete {selected.length} selected
          </Btn>
        )}
      </div>

      <div className="rounded-xl">
        <TableShell>
          <thead>
            <tr>
              <Th className="w-10" />
              <Th>Order ID</Th>
              <Th>Customer</Th>
              <Th>Warehouse</Th>
              <Th className="text-right">Items</Th>
              <Th>Status</Th>
              <Th>Created</Th>
              <Th className="w-[60px]" />
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <Tr key={o.id} className={selected.includes(o.id) ? "border-l-primary bg-surface-hover" : ""}>
                <Td>
                  <Checkbox
                    checked={selected.includes(o.id)}
                    onCheckedChange={() => toggle(o.id)}
                    aria-label={`Select ${o.id}`}
                  />
                </Td>
                <Td>
                  <Link
                    to="/orders/$orderId"
                    params={{ orderId: o.id }}
                    className="font-mono text-[13px] text-primary hover:underline"
                  >
                    {o.id}
                  </Link>
                </Td>
                <Td className="font-medium">{o.customer}</Td>
                <Td className="text-[12px] text-muted-foreground">{o.warehouse}</Td>
                <Td className="text-right text-[12px] text-muted-foreground">{o.items.length}</Td>
                <Td>
                  <StatusBadge status={o.status} />
                </Td>
                <Td className="text-[12px] text-muted-foreground">{o.created}</Td>
                <Td>
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      aria-label="Row actions"
                      className="grid size-8 place-items-center rounded-md hover:bg-border"
                    >
                      <MoreHorizontal className="size-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="shadow-e3">
                      <DropdownMenuItem asChild>
                        <Link to="/orders/$orderId" params={{ orderId: o.id }}>
                          View
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem>Edit</DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive focus:text-destructive">
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </Td>
              </Tr>
            ))}
          </tbody>
        </TableShell>
        <div className="rounded-b-xl border-x border-b border-border bg-card">
          <Pager total={rows.length} />
        </div>
      </div>
    </AppShell>
  );
}
