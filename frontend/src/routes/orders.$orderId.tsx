import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { Check, Printer, Ship, Tag } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import { Btn, Field, Panel, TableShell, Td, Th, Tr } from "@/components/wms/ui-bits";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { orders, orderTotal } from "@/lib/wms-data";

export const Route = createFileRoute("/orders/$orderId")({
  loader: ({ params }) => {
    const order = orders.find((o) => o.id === params.orderId);
    if (!order) throw notFound();
    return { order };
  },
  head: ({ loaderData }) => {
    if (!loaderData) {
      return {
        meta: [{ title: "Order unavailable — Whitfield WMS" }, { name: "robots", content: "noindex" }],
      };
    }
    const title = `Order ${loaderData.order.id} — Whitfield WMS`;
    const description = `Fulfillment detail for ${loaderData.order.id} from ${loaderData.order.customer}: items, stock reservation and shipping timeline.`;
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
      ],
    };
  },
  component: OrderDetail,
});

const steps = ["Created", "Reserved", "Packed", "Shipped"] as const;

function OrderDetail() {
  const { order } = Route.useLoaderData();
  const [packOpen, setPackOpen] = useState(false);
  const currentStep = { PENDING: 0, RESERVED: 1, PACKED: 2, SHIPPED: 3, ERROR: 0 }[order.status];

  return (
    <AppShell
      crumbs={[
        { label: "Dashboard", to: "/" },
        { label: "Orders", to: "/orders" },
        { label: order.id },
      ]}
      title={`Order ${order.id}`}
      actions={<StatusBadge status={order.status} />}
    >
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[3fr_2fr]">
        <div className="space-y-4">
          <Panel>
            <h3>Customer</h3>
            <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
              {[
                ["Name", order.customer],
                ["Email", order.email],
                ["Phone", order.phone],
              ].map(([k, v]) => (
                <div key={k}>
                  <dt className="label-xs text-muted-foreground uppercase">{k}</dt>
                  <dd className="mt-1 text-sm">{v}</dd>
                </div>
              ))}
            </dl>
          </Panel>

          <TableShell toolbar={<h3 className="text-base font-semibold">Items</h3>}>
            <thead>
              <tr>
                <Th>SKU</Th>
                <Th>Product</Th>
                <Th className="text-right">Qty</Th>
                <Th className="text-right">Price</Th>
                <Th className="text-right">Subtotal</Th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((it) => (
                <Tr key={it.sku}>
                  <Td className="font-mono text-[12px] text-muted-foreground">{it.sku}</Td>
                  <Td className="font-medium">{it.product}</Td>
                  <Td className="text-right">{it.qty}</Td>
                  <Td className="text-right">${it.price.toFixed(2)}</Td>
                  <Td className="text-right font-semibold">${(it.qty * it.price).toFixed(2)}</Td>
                </Tr>
              ))}
              <tr>
                <Td colSpan={4} className="text-right font-semibold">
                  Order total
                </Td>
                <Td className="text-right text-lg font-bold text-primary">
                  ${orderTotal(order).toFixed(2)}
                </Td>
              </tr>
            </tbody>
          </TableShell>

          <p className="text-[12px] text-muted-foreground">
            Created by John Mercer on {order.created}
          </p>
        </div>

        <div className="space-y-4">
          <Panel>
            <h3>Status Timeline</h3>
            <ol className="mt-4 space-y-1">
              {steps.map((s, i) => (
                <li key={s} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <span
                      className={
                        "grid size-6 place-items-center rounded-full border " +
                        (i <= currentStep
                          ? "border-primary bg-primary/20 text-primary"
                          : "border-border text-muted-foreground")
                      }
                    >
                      {i < currentStep ? <Check className="size-3.5" /> : <span className="size-1.5 rounded-full bg-current" />}
                    </span>
                    {i < steps.length - 1 && (
                      <span className={"h-8 w-px " + (i < currentStep ? "bg-primary" : "bg-border")} />
                    )}
                  </div>
                  <span
                    className={
                      "pt-0.5 text-sm " +
                      (i === currentStep ? "font-semibold text-primary" : "text-secondary-foreground")
                    }
                  >
                    {s}
                  </span>
                </li>
              ))}
            </ol>
          </Panel>

          <Panel>
            <h3>Stock Reservation</h3>
            {order.status === "ERROR" ? (
              <div className="mt-3 rounded-md border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
                Insufficient stock for 2 line items. Rebalance inventory to continue.
              </div>
            ) : (
              <p className="mt-2 text-sm text-muted-foreground">
                {order.items.reduce((s, i) => s + i.qty, 0)} units reserved across{" "}
                {order.items.length} SKUs.
              </p>
            )}
            <div className="mt-4 flex flex-wrap gap-3">
              <Btn onClick={() => toast.success(`Stock reserved for ${order.id}`)}>Reserve Stock</Btn>
              <Btn variant="secondary" onClick={() => setPackOpen(true)}>
                Pack Order
              </Btn>
              <Btn variant="ghost" onClick={() => toast("Label generated · 1Z9884213US")}>
                <Tag className="size-4" /> Generate Label
              </Btn>
              <Btn variant="secondary" onClick={() => toast.success("Order marked as shipped")}>
                <Ship className="size-4" /> Ship
              </Btn>
            </div>
          </Panel>

          <Panel>
            <div className="flex items-center justify-between">
              <h3>Picklist</h3>
              <button aria-label="Print picklist" className="grid size-10 place-items-center rounded-md hover:bg-surface-hover">
                <Printer className="size-4" />
              </button>
            </div>
            <ul className="mt-3 space-y-2">
              {order.items.map((it, i) => (
                <li
                  key={it.sku}
                  className="flex items-center justify-between rounded-md border border-border bg-input px-3 py-2 text-sm"
                >
                  <span className="truncate">{it.product}</span>
                  <span className="ml-3 rounded-[20px] bg-primary/20 px-2.5 py-1 font-mono text-[11px] text-primary">
                    A-0{i + 1}-{12 + i}
                  </span>
                </li>
              ))}
            </ul>
            <Link
              to="/tickets"
              className="mt-4 inline-block text-[12px] font-semibold text-primary hover:underline"
            >
              View inbound arrivals
            </Link>
          </Panel>
        </div>
      </div>

      <Dialog open={packOpen} onOpenChange={setPackOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[520px]">
          <DialogHeader>
            <DialogTitle>Pack {order.id}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4">
            {["Packed Weight (lbs)", "Width (in)", "Height (in)", "Length (in)"].map((l) => (
              <div key={l}>
                <label className="label-xs text-secondary-foreground">{l}</label>
                <Field type="number" className="mt-1" placeholder="0" />
              </div>
            ))}
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setPackOpen(false)}>
              Cancel
            </Btn>
            <Btn
              onClick={() => {
                setPackOpen(false);
                toast.success(`${order.id} packed and ready for label`);
              }}
            >
              Pack Order
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
