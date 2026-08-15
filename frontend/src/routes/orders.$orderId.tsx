import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Loader2, Ship, Tag, XCircle } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
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
import { ordersAPI } from "@/lib/api";
import { ProtectedRoute } from "@/lib/protected-route";

export const Route = createFileRoute("/orders/$orderId")({
  head: () => ({
    meta: [
      { title: "Order Detail — Whitfield WMS" },
      {
        name: "description",
        content: "Fulfillment detail: items, stock reservation and shipping timeline.",
      },
    ],
  }),
  component: OrderDetailWrapper,
});

const steps = ["PENDING", "RESERVED", "PACKED", "SHIPPED"] as const;

type OrderItem = { barcode: string; product_name: string; quantity: number };

type UnitItem = { barcode: string; storage_location: string | null; status: string };

type OrderData = {
  id: string;
  order_id: string;
  customer_name: string;
  warehouse_id: string;
  items: OrderItem[];
  status: "PENDING" | "RESERVED" | "PACKED" | "SHIPPED" | "CANCELLED";
  packed_weight: number | null;
  packed_dims: { width: number; height: number; length: number } | null;
  tracking_number: string | null;
  label_url: string | null;
  created_at: string;
};

type PackFormState = { packed_weight: string; width: string; height: string; length: string };

const emptyPackForm: PackFormState = { packed_weight: "", width: "", height: "", length: "" };

function OrderDetailContent() {
  const { orderId } = Route.useParams();
  const [packOpen, setPackOpen] = useState(false);
  const [packForm, setPackForm] = useState<PackFormState>(emptyPackForm);
  const [isPacking, setIsPacking] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const {
    data: order,
    isLoading,
    isError,
    refetch,
  } = useQuery<OrderData>({
    queryKey: ["order", orderId],
    queryFn: () => ordersAPI.getById(orderId) as Promise<OrderData>,
    retry: false,
  });

  const {
    data: unitsData,
    isFetching: unitsLoading,
    refetch: refetchUnits,
  } = useQuery<{ items: UnitItem[]; total: number }>({
    queryKey: ["order-items", order?.id],
    queryFn: () => ordersAPI.getItems(order!.id) as Promise<{ items: UnitItem[]; total: number }>,
    enabled: !!order?.id,
    refetchInterval: 15000,
  });

  const locationsByBarcode = (unitsData?.items ?? []).reduce<Record<string, string[]>>((acc, unit) => {
    if (!unit.storage_location) return acc;
    const list = acc[unit.barcode] ?? (acc[unit.barcode] = []);
    if (!list.includes(unit.storage_location)) list.push(unit.storage_location);
    return acc;
  }, {});

  const currentStepIndex = order ? steps.indexOf(order.status as (typeof steps)[number]) : -1;

  const runAction = async (action: string, fn: () => Promise<unknown>, successMsg?: string) => {
    setActionLoading(action);
    try {
      await fn();
      if (successMsg) toast.success(successMsg);
      await refetch();
      await refetchUnits();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : `Failed to ${action} order`);
    } finally {
      setActionLoading(null);
    }
  };

  const handlePackSubmit = async () => {
    if (!order) return;
    const weight = parseFloat(packForm.packed_weight);
    const width = parseFloat(packForm.width);
    const height = parseFloat(packForm.height);
    const length = parseFloat(packForm.length);
    if ([weight, width, height, length].some((v) => !Number.isFinite(v) || v <= 0)) {
      toast.error("All packing values must be positive numbers");
      return;
    }
    setIsPacking(true);
    try {
      await ordersAPI.pack(order.id, { packed_weight: weight, width, height, length });
      toast.success(`${order.order_id} packed and ready for label`);
      setPackOpen(false);
      setPackForm(emptyPackForm);
      await refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to pack order");
    } finally {
      setIsPacking(false);
    }
  };

  if (isLoading) {
    return (
      <AppShell
        crumbs={[{ label: "Dashboard", to: "/" }, { label: "Orders", to: "/orders" }]}
        title="Loading order..."
      >
        <div className="py-16 text-center">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">Loading order...</p>
        </div>
      </AppShell>
    );
  }

  if (isError || !order) {
    return (
      <AppShell
        crumbs={[{ label: "Dashboard", to: "/" }, { label: "Orders", to: "/orders" }]}
        title="Order not found"
      >
        <Panel className="py-12 text-center">
          <p className="text-sm text-muted-foreground">
            We couldn&apos;t find this order. It may have been removed or the ID is incorrect.
          </p>
          <Link to="/orders" className="mt-4 inline-block text-sm font-semibold text-primary hover:underline">
            Back to Orders
          </Link>
        </Panel>
      </AppShell>
    );
  }

  const canReserve = order.status === "PENDING";
  const canPack = order.status === "RESERVED";
  const canGenerateLabel = order.status === "PACKED";
  const canShip = order.status === "PACKED" && !!order.label_url;
  const canCancel = order.status !== "SHIPPED" && order.status !== "CANCELLED";
  const totalUnits = order.items.reduce((sum, it) => sum + it.quantity, 0);

  return (
    <AppShell
      crumbs={[
        { label: "Dashboard", to: "/" },
        { label: "Orders", to: "/orders" },
        { label: order.order_id },
      ]}
      title={`Order ${order.order_id}`}
      actions={<StatusBadge status={order.status} />}
    >
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[3fr_2fr]">
        <div className="space-y-4">
          <Panel>
            <h3>Customer</h3>
            <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <dt className="label-xs text-muted-foreground uppercase">Name</dt>
                <dd className="mt-1 text-sm">{order.customer_name}</dd>
              </div>
              <div>
                <dt className="label-xs text-muted-foreground uppercase">Warehouse</dt>
                <dd className="mt-1 text-sm">{order.warehouse_id}</dd>
              </div>
              <div>
                <dt className="label-xs text-muted-foreground uppercase">Tracking</dt>
                <dd className="mt-1 text-sm">{order.tracking_number || "—"}</dd>
              </div>
            </dl>
          </Panel>

          <TableShell toolbar={<h3 className="text-base font-semibold">Items</h3>}>
            <thead>
              <tr>
                <Th>Barcode</Th>
                <Th>Product</Th>
                <Th className="text-right">Qty</Th>
                <Th>Location</Th>
              </tr>
            </thead>
            <tbody>
              {order.items.length > 0 ? (
                order.items.map((it, idx) => {
                  const locations = locationsByBarcode[it.barcode] ?? [];
                  return (
                    <Tr key={`${it.barcode}-${idx}`}>
                      <Td className="font-mono text-[12px] text-muted-foreground">{it.barcode}</Td>
                      <Td className="font-medium">{it.product_name}</Td>
                      <Td className="text-right">{it.quantity}</Td>
                      <Td className="font-mono text-[12px]">
                        {unitsLoading && !unitsData
                          ? "…"
                          : locations.length > 0
                            ? locations.join(", ")
                            : order.status === "PENDING"
                              ? "Not reserved yet"
                              : "—"}
                      </Td>
                    </Tr>
                  );
                })
              ) : (
                <Tr>
                  <Td colSpan={4} className="py-8 text-center text-muted-foreground">
                    No items on this order
                  </Td>
                </Tr>
              )}
            </tbody>
          </TableShell>

          <p className="text-[12px] text-muted-foreground">Created {order.created_at}</p>
        </div>

        <div className="space-y-4">
          <Panel>
            <h3>Status Timeline</h3>
            {order.status === "CANCELLED" ? (
              <div className="mt-3 rounded-md border border-destructive bg-destructive/10 p-3 text-sm text-destructive">
                This order was cancelled.
              </div>
            ) : (
              <ol className="mt-4 space-y-1">
                {steps.map((s, i) => (
                  <li key={s} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <span
                        className={
                          "grid size-6 place-items-center rounded-full border " +
                          (i <= currentStepIndex
                            ? "border-primary bg-primary/20 text-primary"
                            : "border-border text-muted-foreground")
                        }
                      >
                        {i < currentStepIndex ? (
                          <Check className="size-3.5" />
                        ) : (
                          <span className="size-1.5 rounded-full bg-current" />
                        )}
                      </span>
                      {i < steps.length - 1 && (
                        <span className={"h-8 w-px " + (i < currentStepIndex ? "bg-primary" : "bg-border")} />
                      )}
                    </div>
                    <span
                      className={
                        "pt-0.5 text-sm " +
                        (i === currentStepIndex ? "font-semibold text-primary" : "text-secondary-foreground")
                      }
                    >
                      {s}
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </Panel>

          <Panel>
            <h3>Fulfillment Actions</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {totalUnits} units across {order.items.length} line item{order.items.length === 1 ? "" : "s"}.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <Btn
                disabled={!canReserve || actionLoading === "reserve"}
                title={!canReserve ? "Order must be PENDING to reserve stock" : undefined}
                onClick={() =>
                  runAction("reserve", () => ordersAPI.reserve(order.id), `Stock reserved for ${order.order_id}`)
                }
              >
                {actionLoading === "reserve" && <Loader2 className="size-4 animate-spin" />} Reserve Stock
              </Btn>
              <Btn
                variant="secondary"
                disabled={!canPack}
                title={!canPack ? "Order must be RESERVED to pack" : undefined}
                onClick={() => setPackOpen(true)}
              >
                Pack Order
              </Btn>
              <Btn
                variant="ghost"
                disabled={!canGenerateLabel || actionLoading === "label"}
                title={!canGenerateLabel ? "Order must be PACKED to generate a label" : undefined}
                onClick={() =>
                  runAction("label", async () => {
                    const res = (await ordersAPI.generateLabel(order.id)) as {
                      tracking_number?: string;
                      label_url?: string;
                    };
                    toast.success(`Label generated · ${res?.tracking_number ?? "tracking pending"}`);
                  })
                }
              >
                {actionLoading === "label" && <Loader2 className="size-4 animate-spin" />}
                <Tag className="size-4" /> Generate Label
              </Btn>
              <Btn
                variant="secondary"
                disabled={!canShip || actionLoading === "ship"}
                title={!canShip ? "Order must be PACKED with a label to ship" : undefined}
                onClick={() => runAction("ship", () => ordersAPI.ship(order.id), "Order marked as shipped")}
              >
                {actionLoading === "ship" && <Loader2 className="size-4 animate-spin" />}
                <Ship className="size-4" /> Ship
              </Btn>
              <Btn
                variant="danger"
                disabled={!canCancel || actionLoading === "cancel"}
                title={!canCancel ? "Order can no longer be cancelled" : undefined}
                onClick={() => runAction("cancel", () => ordersAPI.cancel(order.id), "Order cancelled")}
              >
                {actionLoading === "cancel" && <Loader2 className="size-4 animate-spin" />}
                <XCircle className="size-4" /> Cancel Order
              </Btn>
            </div>
          </Panel>

          <Panel>
            <h3>Item Locations</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {order.status === "PENDING"
                ? "Reserve stock to pull each unit's live bin location into the table."
                : (unitsData?.total ?? 0) > 0
                  ? `${unitsData!.total} unit${unitsData!.total === 1 ? "" : "s"} reserved from stock — bin locations shown in the Items table.`
                  : "No physical units are currently linked to this order."}
            </p>
            <div className="mt-4 flex items-center gap-3">
              <Btn variant="secondary" disabled={unitsLoading} onClick={() => refetchUnits()}>
                {unitsLoading && <Loader2 className="size-4 animate-spin" />} Refresh Locations
              </Btn>
              <Link
                to="/tickets"
                className="text-[12px] font-semibold text-primary hover:underline"
              >
                View inbound arrivals
              </Link>
            </div>
          </Panel>
        </div>
      </div>

      <Dialog open={packOpen} onOpenChange={setPackOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[520px]">
          <DialogHeader>
            <DialogTitle>Pack {order.order_id}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4">
            {(
              [
                ["Packed Weight (lbs)", "packed_weight"],
                ["Width (in)", "width"],
                ["Height (in)", "height"],
                ["Length (in)", "length"],
              ] as const
            ).map(([label, key]) => (
              <div key={key}>
                <label className="label-xs text-secondary-foreground">{label}</label>
                <Field
                  type="number"
                  min="0"
                  step="0.01"
                  className="mt-1"
                  placeholder="0"
                  value={packForm[key]}
                  onChange={(e) => setPackForm((f) => ({ ...f, [key]: e.target.value }))}
                  disabled={isPacking}
                />
              </div>
            ))}
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setPackOpen(false)} disabled={isPacking}>
              Cancel
            </Btn>
            <Btn onClick={handlePackSubmit} disabled={isPacking}>
              {isPacking && <Loader2 className="size-4 animate-spin" />} Pack Order
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

function OrderDetailWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER", "STAFF"]}>
      <OrderDetailContent />
    </ProtectedRoute>
  );
}
