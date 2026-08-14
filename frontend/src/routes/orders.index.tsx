import { createFileRoute, Link } from "@tanstack/react-router";
import { Download, Filter, Loader2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import { Btn, SearchField, Select, TableShell, Td, Th, Tr } from "@/components/wms/ui-bits";
import { ProtectedRoute } from "@/lib/protected-route";
import { ordersAPI, warehousesAPI } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/orders/")({
  head: () => ({
    meta: [
      { title: "Orders & Fulfillment — Whitfield WMS" },
      {
        name: "description",
        content: "Manage customer orders: create, reserve stock, pack, label and ship.",
      },
    ],
  }),
  component: OrdersPageWrapper,
});

const createOrderSchema = z.object({
  order_id: z.string().min(1, "Order ID is required"),
  customer_name: z.string().min(1, "Customer name is required"),
  warehouse_id: z.string().min(1, "Warehouse is required"),
});

type CreateOrderForm = z.infer<typeof createOrderSchema>;

function OrdersPageContent() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("ALL");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const form = useForm<CreateOrderForm>({
    resolver: zodResolver(createOrderSchema),
    defaultValues: {
      order_id: "",
      customer_name: "",
      warehouse_id: "",
    },
  });

  // Fetch orders
  const { data: ordersData, isLoading, refetch } = useQuery({
    queryKey: ["orders", status],
    queryFn: () => ordersAPI.getAll(0, 100, status !== "ALL" ? status : undefined),
    staleTime: 30000,
  });

  // Fetch warehouses for dropdown
  const { data: warehousesData = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehousesAPI.getAll(0, 100),
    staleTime: 60000,
  });

  const warehouses = Array.isArray(warehousesData) ? warehousesData : warehousesData?.warehouses || [];

  const orders = Array.isArray(ordersData) ? ordersData : ordersData?.orders || [];

  const filteredOrders = orders.filter(
    (o) =>
      (status === "ALL" || o.status === status) &&
      (o.order_id?.toLowerCase().includes(query.toLowerCase()) ||
        o.customer_name?.toLowerCase().includes(query.toLowerCase()))
  );

  const onSubmit = async (data: CreateOrderForm) => {
    setIsCreating(true);
    try {
      await ordersAPI.create({
        order_id: data.order_id,
        customer_name: data.customer_name,
        warehouse_id: data.warehouse_id,
        items: [],
      });
      toast.success("Order created successfully!");
      form.reset();
      setDialogOpen(false);
      refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create order");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Orders" }]}
      title="Orders & Fulfillment"
      actions={
        <>
          <Btn variant="secondary">
            <Filter className="size-4" /> Filter
          </Btn>
          <Btn variant="secondary">
            <Download className="size-4" /> Export
          </Btn>
          <Btn onClick={() => setDialogOpen(true)}>
            <Plus className="size-4" /> Create Order
          </Btn>
        </>
      }
    >
      <div className="mb-6 space-y-4 rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm p-4 shadow-sm">
        <SearchField
          className="w-full"
          placeholder="Search order ID or customer..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          {["ALL", "PENDING", "RESERVED", "PACKED", "SHIPPED"].map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={
                "rounded-full px-4 py-1.5 text-xs font-bold transition-all " +
                (status === s
                  ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/20"
                  : "border border-slate-600/50 text-slate-300 hover:bg-slate-700/30 hover:border-slate-500")
              }
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">Loading orders...</p>
        </div>
      ) : (
        <TableShell>
          <thead>
            <tr>
              <Th>Order ID</Th>
              <Th>Customer</Th>
              <Th>Items</Th>
              <Th>Status</Th>
              <Th>Created</Th>
              <Th>Actions</Th>
            </tr>
          </thead>
          <tbody>
            {filteredOrders.length > 0 ? (
              filteredOrders.map((order) => (
                <Tr key={order.id}>
                  <Td className="font-mono text-sm font-semibold">{order.order_id}</Td>
                  <Td className="text-sm">{order.customer_name}</Td>
                  <Td className="text-sm">{order.items?.length || 0}</Td>
                  <Td>
                    <StatusBadge status={order.status} />
                  </Td>
                  <Td className="text-xs text-muted-foreground">{order.created_at}</Td>
                  <Td>
                    <Link
                      to={`/orders/${order.id}`}
                      className="text-xs font-semibold text-primary hover:underline"
                    >
                      View
                    </Link>
                  </Td>
                </Tr>
              ))
            ) : (
              <Tr>
                <Td colSpan={6} className="py-8 text-center text-muted-foreground">
                  No orders found
                </Td>
              </Tr>
            )}
          </tbody>
        </TableShell>
      )}

      {/* Create Order Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader className="border-b border-slate-700/50 pb-4">
            <DialogTitle className="text-lg font-bold">Create New Order</DialogTitle>
            <DialogDescription className="text-xs text-slate-400">Fill in the details to create a new order for fulfillment</DialogDescription>
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
              <FormField
                control={form.control}
                name="order_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Order ID</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="ORD-2024-001"
                        {...field}
                        disabled={isCreating}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="customer_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Customer Name</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="John Doe"
                        {...field}
                        disabled={isCreating}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="warehouse_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Warehouse</FormLabel>
                    <FormControl>
                      <select
                        {...field}
                        disabled={isCreating || warehouses.length === 0}
                        className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <option value="">
                          {warehouses.length === 0 ? "No warehouses available" : "Select a warehouse..."}
                        </option>
                        {warehouses.map((wh: any) => (
                          <option key={wh.id} value={wh.id}>
                            {wh.code || wh.id} {wh.name ? `- ${wh.name}` : ""}
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                  disabled={isCreating}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isCreating}>
                  {isCreating && <Loader2 className="mr-2 size-4 animate-spin" />}
                  Create Order
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

function OrdersPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER", "STAFF"]}>
      <OrdersPageContent />
    </ProtectedRoute>
  );
}
