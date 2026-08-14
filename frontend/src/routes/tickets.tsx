import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, Check, Copy, Loader2, MoreHorizontal, Plus } from "lucide-react";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import {
  Btn,
  Field,
  Pager,
  Panel,
  SearchField,
  Select,
  TableShell,
  Td,
  Th,
  Tr,
} from "@/components/wms/ui-bits";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from "@/lib/auth-context";
import { ProtectedRoute } from "@/lib/protected-route";
import { arrivalsAPI, storageAPI, ticketsAPI, warehousesAPI } from "@/lib/api";

export const Route = createFileRoute("/tickets")({
  head: () => ({
    meta: [
      { title: "Receiving Tickets — Whitfield WMS" },
      {
        name: "description",
        content:
          "Log arrivals, inspect inbound items, flag damage and assign storage locations across every warehouse.",
      },
      { property: "og:title", content: "Receiving Tickets — Whitfield WMS" },
      {
        property: "og:description",
        content: "Log arrivals, inspect items and assign storage locations.",
      },
    ],
  }),
  component: TicketsPageWrapper,
});

// ============================================================================
// Types (mirrors backend response_model shapes — see wms_response.py)
// ============================================================================

type TicketStatusValue =
  | "ANNOUNCED"
  | "ACCEPTED"
  | "ARRIVED"
  | "PENDING_INSPECTION"
  | "INSPECTED"
  | "SHIPMENT_ARRIVED"
  | "STORED"
  | "RESERVED"
  | "SOLD"
  | "DECLINED"
  | "NEEDS_SPEC"
  | "DAMAGED";

interface TicketResponse {
  id: string;
  ticket_id: string;
  warehouse_id: string;
  inbox_id: string | null;
  tracking_number: string | null;
  no_ticket_arrival: boolean;
  status: TicketStatusValue;
  arrived_by: string;
  approved_by: string | null;
  storage_location: string | null;
  created_at: string;
}

interface TicketListResponse {
  tickets: TicketResponse[];
  total: number;
}

interface DamageDetail {
  flag: boolean;
  note?: string | null;
}

interface ItemResponse {
  id: string;
  ticket_id: string;
  unit_seq: number;
  barcode: string;
  product_name: string;
  width: number;
  height: number;
  weight: number;
  image_url: string | null;
  damage: DamageDetail;
  status: TicketStatusValue;
  warehouse_id: string;
  storage_location: string | null;
  order_id?: string | null;
  logged_by?: string;
  created_at: string;
}

interface ItemListResponse {
  items: ItemResponse[];
  total: number;
}

interface WarehouseResponse {
  id: string;
  code: string;
  name: string;
  address?: string | null;
  manager_id?: string | null;
  is_active: boolean;
  created_at: string;
}

interface WarehouseListResponse {
  warehouses: WarehouseResponse[];
  total: number;
}

interface StorageLocationResponse {
  id: string;
  warehouse_id: string;
  zone: string;
  rack: string;
  bin: string;
  location_code: string;
  is_occupied: boolean;
  created_at: string;
}

interface StorageLocationListResponse {
  locations: StorageLocationResponse[];
  total: number;
}

// Real TicketStatus enum values relevant to the receiving/ticketing flow
// (backend/core/models/wms_models.py TicketStatus).
const TICKET_STATUS_FILTERS: Array<"ALL" | TicketStatusValue> = [
  "ALL",
  "ARRIVED",
  "PENDING_INSPECTION",
  "INSPECTED",
  "SHIPMENT_ARRIVED",
  "STORED",
];

// Rough stage index per status, used only to render the (informational) timeline.
const STAGE_INDEX: Record<string, number> = {
  ANNOUNCED: 0,
  ACCEPTED: 0,
  ARRIVED: 0,
  PENDING_INSPECTION: 1,
  INSPECTED: 1,
  DAMAGED: 1,
  SHIPMENT_ARRIVED: 2,
  STORED: 3,
  RESERVED: 3,
  SOLD: 3,
};
const TIMELINE_STEPS = ["Arrived", "Inspected", "Approved", "Stored"];

function TicketsPage() {
  const { user, hasRole } = useAuth();
  const isStaff = user?.role === "STAFF";

  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<"ALL" | TicketStatusValue>("ALL");
  const [warehouseFilter, setWarehouseFilter] = useState("ALL");
  const [openId, setOpenId] = useState<string | null>(null);
  const [arrivalOpen, setArrivalOpen] = useState(false);
  const [addItemOpen, setAddItemOpen] = useState(false);

  // ------------------------------------------------------------------------
  // Data fetching
  // ------------------------------------------------------------------------

  const ticketsQuery = useQuery({
    queryKey: ["tickets", status],
    queryFn: () =>
      ticketsAPI.getAll(0, 100, status !== "ALL" ? status : undefined) as Promise<TicketListResponse>,
    staleTime: 15000,
  });

  // GET /warehouses is OWNER/MANAGER only on the backend — STAFF gets a 403,
  // so only fetch it for roles that are actually allowed to call it.
  const warehousesQuery = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehousesAPI.getAll(0, 100) as Promise<WarehouseListResponse>,
    enabled: !isStaff,
    staleTime: 60000,
  });

  const warehouseCodeById = useMemo(() => {
    const map: Record<string, string> = {};
    for (const wh of warehousesQuery.data?.warehouses ?? []) {
      map[wh.id] = `${wh.code} · ${wh.name}`;
    }
    return map;
  }, [warehousesQuery.data]);

  const tickets = ticketsQuery.data?.tickets ?? [];

  const rows = useMemo(
    () =>
      tickets.filter(
        (t) =>
          (warehouseFilter === "ALL" || t.warehouse_id === warehouseFilter) &&
          t.ticket_id.toLowerCase().includes(query.toLowerCase()),
      ),
    [tickets, query, warehouseFilter],
  );

  const active = tickets.find((t) => t.ticket_id === openId) ?? null;

  const ticketDetailQuery = useQuery({
    queryKey: ["ticket", openId],
    queryFn: () => ticketsAPI.getById(openId as string) as Promise<TicketResponse>,
    enabled: !!openId,
  });

  const itemsQuery = useQuery({
    queryKey: ["ticket-items", openId],
    queryFn: () => ticketsAPI.getItems(openId as string) as Promise<ItemListResponse>,
    enabled: !!openId,
  });

  const detail = ticketDetailQuery.data ?? active;
  const items = itemsQuery.data?.items ?? [];

  const storageLocationsQuery = useQuery({
    queryKey: ["storage-locations", detail?.warehouse_id],
    queryFn: () =>
      storageAPI.list(0, 100, detail?.warehouse_id) as Promise<StorageLocationListResponse>,
    enabled: !!detail?.warehouse_id,
  });
  const availableLocations = (storageLocationsQuery.data?.locations ?? []).filter(
    (l) => !l.is_occupied,
  );

  // ------------------------------------------------------------------------
  // Mutations (no useMutation elsewhere in the codebase yet — following the
  // same manual async/await + local loading-state pattern as orders.index.tsx)
  // ------------------------------------------------------------------------

  const [approving, setApproving] = useState(false);
  async function handleApprove() {
    if (!detail) return;
    setApproving(true);
    try {
      const updated = (await ticketsAPI.approve(detail.ticket_id)) as TicketResponse;
      toast.success(`Ticket ${updated.ticket_id} approved`);
      ticketDetailQuery.refetch();
      ticketsQuery.refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to approve ticket");
    } finally {
      setApproving(false);
    }
  }

  const [storageLocation, setStorageLocation] = useState("");
  const [assigning, setAssigning] = useState(false);
  async function handleAssignStorage() {
    if (!detail || !storageLocation) {
      toast.error("Select a storage location first");
      return;
    }
    setAssigning(true);
    try {
      const updated = (await ticketsAPI.assignStorage(detail.ticket_id, {
        storage_location: storageLocation,
      })) as TicketResponse;
      toast.success(`Storage ${updated.storage_location ?? storageLocation} assigned to ${updated.ticket_id}`);
      setStorageLocation("");
      ticketDetailQuery.refetch();
      ticketsQuery.refetch();
      storageLocationsQuery.refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to assign storage");
    } finally {
      setAssigning(false);
    }
  }

  const [itemForm, setItemForm] = useState({
    barcode: "",
    product_name: "",
    width: "",
    height: "",
    weight: "",
    damageFlag: false,
    damageNote: "",
  });
  const [addingItem, setAddingItem] = useState(false);
  async function handleAddItem() {
    if (!detail) return;
    if (!itemForm.barcode || !itemForm.product_name || !itemForm.width || !itemForm.height || !itemForm.weight) {
      toast.error("Barcode, product name, width, height and weight are required");
      return;
    }
    setAddingItem(true);
    try {
      const damage: { flag: boolean; note?: string } = { flag: itemForm.damageFlag };
      if (itemForm.damageNote) damage.note = itemForm.damageNote;

      const created = (await ticketsAPI.logItem(detail.ticket_id, {
        barcode: itemForm.barcode,
        product_name: itemForm.product_name,
        width: Number(itemForm.width),
        height: Number(itemForm.height),
        weight: Number(itemForm.weight),
        damage,
      })) as ItemResponse;
      toast.success(`Item logged: unit #${created.unit_seq} (${created.barcode})`);
      setItemForm({
        barcode: "",
        product_name: "",
        width: "",
        height: "",
        weight: "",
        damageFlag: false,
        damageNote: "",
      });
      setAddItemOpen(false);
      itemsQuery.refetch();
      ticketDetailQuery.refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to log item");
    } finally {
      setAddingItem(false);
    }
  }

  const [arrivalWarehouseId, setArrivalWarehouseId] = useState("");
  const [trackingNumber, setTrackingNumber] = useState("");
  const [noTicketArrival, setNoTicketArrival] = useState(false);
  const [loggingArrival, setLoggingArrival] = useState(false);
  const effectiveArrivalWarehouseId = isStaff ? (user?.warehouse_id ?? "") : arrivalWarehouseId;

  async function handleLogArrival() {
    if (!effectiveArrivalWarehouseId) {
      toast.error("Select a warehouse");
      return;
    }
    setLoggingArrival(true);
    try {
      const payload: { warehouse_id: string; tracking_number?: string; no_ticket_arrival: boolean } = {
        warehouse_id: effectiveArrivalWarehouseId,
        no_ticket_arrival: noTicketArrival,
      };
      if (trackingNumber) payload.tracking_number = trackingNumber;

      const created = (await arrivalsAPI.log(payload)) as TicketResponse;
      toast.success(`Ticket ${created.ticket_id} created`);
      setArrivalOpen(false);
      setArrivalWarehouseId("");
      setTrackingNumber("");
      setNoTicketArrival(false);
      ticketsQuery.refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to log arrival");
    } finally {
      setLoggingArrival(false);
    }
  }

  function formatTimestamp(ts: string) {
    return ts.slice(0, 19).replace("T", " ");
  }

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Tickets" }]}
      title="Receiving Tickets"
      actions={
        <Btn onClick={() => setArrivalOpen(true)}>
          <Plus className="size-4" /> Log Arrival
        </Btn>
      }
    >
      <div className="mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-border bg-card p-4 shadow-e1">
        <SearchField
          className="w-full sm:w-[280px]"
          placeholder="Search ticket ID..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          {TICKET_STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={
                "rounded-[20px] px-3 py-1.5 text-[12px] font-semibold transition-colors " +
                (status === s
                  ? "bg-primary text-primary-foreground"
                  : "border border-border text-muted-foreground hover:bg-surface-hover")
              }
            >
              {s}
            </button>
          ))}
        </div>
        {!isStaff && (
          <Select
            value={warehouseFilter}
            onChange={(e) => setWarehouseFilter(e.target.value)}
            className="ml-auto"
          >
            <option value="ALL">All warehouses</option>
            {(warehousesQuery.data?.warehouses ?? []).map((wh) => (
              <option key={wh.id} value={wh.id}>
                {wh.code} · {wh.name}
              </option>
            ))}
          </Select>
        )}
      </div>

      <TableShell>
        <thead>
          <tr>
            <Th className="w-10" />
            <Th>Ticket ID</Th>
            <Th>Warehouse</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th>Storage</Th>
            <Th>Approved By</Th>
            <Th className="w-[60px]" />
          </tr>
        </thead>
        <tbody>
          {ticketsQuery.isLoading ? (
            <Tr>
              <Td colSpan={8} className="py-10 text-center text-muted-foreground">
                <Loader2 className="mx-auto size-6 animate-spin text-primary" />
                <p className="mt-2 text-sm">Loading tickets...</p>
              </Td>
            </Tr>
          ) : ticketsQuery.isError ? (
            <Tr>
              <Td colSpan={8} className="py-10 text-center text-destructive">
                {ticketsQuery.error instanceof Error
                  ? ticketsQuery.error.message
                  : "Failed to load tickets"}
              </Td>
            </Tr>
          ) : rows.length === 0 ? (
            <Tr>
              <Td colSpan={8} className="py-10 text-center text-muted-foreground">
                No tickets found
              </Td>
            </Tr>
          ) : (
            rows.map((t) => (
              <Tr key={t.id} className="cursor-pointer" onClick={() => setOpenId(t.ticket_id)}>
                <Td onClick={(e) => e.stopPropagation()}>
                  <Checkbox aria-label={`Select ${t.ticket_id}`} />
                </Td>
                <Td className="font-mono text-[13px] text-primary">{t.ticket_id}</Td>
                <Td className="text-[12px] text-muted-foreground">
                  {warehouseCodeById[t.warehouse_id] ?? t.warehouse_id}
                </Td>
                <Td>
                  <StatusBadge status={t.status} />
                </Td>
                <Td className="text-[12px] text-muted-foreground">{formatTimestamp(t.created_at)}</Td>
                <Td className="font-mono text-[12px]">{t.storage_location ?? "—"}</Td>
                <Td className="text-[12px] text-secondary-foreground">{t.approved_by ?? "—"}</Td>
                <Td onClick={(e) => e.stopPropagation()}>
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      aria-label="Row actions"
                      className="grid size-8 place-items-center rounded-md hover:bg-border"
                    >
                      <MoreHorizontal className="size-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="shadow-e3">
                      <DropdownMenuItem onClick={() => setOpenId(t.ticket_id)}>View</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </Td>
              </Tr>
            ))
          )}
        </tbody>
      </TableShell>
      <div className="rounded-b-xl border-x border-b border-border bg-card">
        <Pager total={rows.length} />
      </div>

      <Dialog
        open={!!openId}
        onOpenChange={(o) => {
          if (!o) setOpenId(null);
        }}
      >
        <DialogContent className="max-h-[85vh] overflow-y-auto shadow-e3 sm:max-w-[900px]">
          {detail && (
            <>
              <DialogHeader>
                <DialogTitle className="flex flex-wrap items-center gap-3">
                  <span className="font-mono">{detail.ticket_id}</span>
                  <StatusBadge status={detail.status} />
                </DialogTitle>
              </DialogHeader>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-[2fr_1fr]">
                <div className="space-y-4">
                  <Panel className="p-4">
                    <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                      {[
                        ["Tracking", detail.tracking_number ?? "—"],
                        ["Warehouse", warehouseCodeById[detail.warehouse_id] ?? detail.warehouse_id],
                        ["Created", formatTimestamp(detail.created_at)],
                      ].map(([k, v]) => (
                        <div key={k}>
                          <dt className="label-xs text-muted-foreground uppercase">{k}</dt>
                          <dd className="mt-1 flex items-center gap-2 font-mono text-[13px]">
                            {v}
                            {k === "Tracking" && detail.tracking_number && (
                              <button
                                aria-label="Copy tracking number"
                                onClick={() => {
                                  navigator.clipboard.writeText(detail.tracking_number ?? "");
                                  toast("Tracking number copied");
                                }}
                              >
                                <Copy className="size-3.5 text-muted-foreground hover:text-primary" />
                              </button>
                            )}
                          </dd>
                        </div>
                      ))}
                    </dl>
                    {detail.no_ticket_arrival && (
                      <p className="mt-3 inline-flex items-center gap-2 rounded-md border-l-4 border-warning bg-warning/10 px-3 py-2 text-[13px] text-warning">
                        <AlertTriangle className="size-4" /> Unannounced (no-ticket) arrival
                      </p>
                    )}
                  </Panel>

                  <TableShell toolbar={<h3 className="text-base font-semibold">Items checklist</h3>}>
                    <thead>
                      <tr>
                        <Th>Barcode</Th>
                        <Th>Product</Th>
                        <Th>Dimensions</Th>
                        <Th>Storage</Th>
                        <Th>Status</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {itemsQuery.isLoading ? (
                        <Tr>
                          <Td colSpan={5} className="py-6 text-center text-muted-foreground">
                            <Loader2 className="mx-auto size-5 animate-spin text-primary" />
                          </Td>
                        </Tr>
                      ) : items.length === 0 ? (
                        <Tr>
                          <Td colSpan={5} className="py-6 text-center text-muted-foreground">
                            No items logged yet
                          </Td>
                        </Tr>
                      ) : (
                        items.map((it) => (
                          <Tr key={it.id}>
                            <Td className="font-mono text-[12px] text-muted-foreground">{it.barcode}</Td>
                            <Td className="font-medium">
                              {it.product_name}
                              {it.damage.flag && (
                                <span
                                  className="ml-2 rounded-[20px] bg-warning/20 px-2 py-0.5 text-[11px] font-semibold text-warning"
                                  title={it.damage.note ?? undefined}
                                >
                                  DAMAGED
                                </span>
                              )}
                            </Td>
                            <Td className="text-[12px] text-muted-foreground">
                              {it.width}&quot; × {it.height}&quot; · {it.weight} lb
                            </Td>
                            <Td>
                              <span className="rounded-[20px] bg-primary/15 px-2.5 py-1 font-mono text-[11px] text-primary">
                                {it.storage_location ?? "—"}
                              </span>
                            </Td>
                            <Td>
                              <StatusBadge status={it.status} />
                            </Td>
                          </Tr>
                        ))
                      )}
                    </tbody>
                  </TableShell>
                  <Btn variant="secondary" onClick={() => setAddItemOpen(true)}>
                    <Plus className="size-4" /> Add Item
                  </Btn>
                </div>

                <div className="space-y-4">
                  <Panel className="p-4">
                    <h3 className="text-base">Timeline</h3>
                    <ol className="mt-3 space-y-3 text-sm">
                      {TIMELINE_STEPS.map((s, i) => {
                        const currentStage = STAGE_INDEX[detail.status] ?? 0;
                        const done = i <= currentStage;
                        return (
                          <li key={s} className="flex items-center gap-3">
                            <span
                              className={
                                "grid size-6 place-items-center rounded-full border " +
                                (done
                                  ? "border-primary bg-primary/20 text-primary"
                                  : "border-border bg-transparent text-muted-foreground")
                              }
                            >
                              {done && <Check className="size-3.5" />}
                            </span>
                            <span className={done ? "font-semibold text-primary" : "text-muted-foreground"}>
                              {s}
                            </span>
                          </li>
                        );
                      })}
                    </ol>
                  </Panel>

                  {hasRole(["OWNER", "MANAGER"]) && detail.status === "PENDING_INSPECTION" && (
                    <Panel className="p-4">
                      <h3 className="text-base">Manager approval</h3>
                      <p className="mt-1 text-[13px] text-muted-foreground">
                        Awaiting manager approval before storage.
                      </p>
                      <div className="mt-3 flex gap-3">
                        <Btn onClick={handleApprove} disabled={approving}>
                          {approving && <Loader2 className="size-4 animate-spin" />}
                          Approve
                        </Btn>
                      </div>
                      <p className="mt-2 text-[11px] text-muted-foreground">
                        No reject endpoint exists on the backend yet — only approve is available.
                      </p>
                    </Panel>
                  )}
                  {detail.approved_by && (
                    <p className="text-[12px] text-muted-foreground">Approved by {detail.approved_by}</p>
                  )}

                  <Panel className="p-4">
                    <h3 className="text-base">Assign storage</h3>
                    <Select
                      className="mt-3 w-full"
                      value={storageLocation}
                      onChange={(e) => setStorageLocation(e.target.value)}
                    >
                      <option value="">Select storage location</option>
                      {availableLocations.length === 0 && !storageLocationsQuery.isLoading && (
                        <option value="" disabled>
                          No available locations
                        </option>
                      )}
                      {availableLocations.map((loc) => (
                        <option key={loc.id} value={loc.location_code}>
                          {loc.location_code}
                        </option>
                      ))}
                    </Select>
                    <Btn
                      variant="secondary"
                      className="mt-3 w-full"
                      onClick={handleAssignStorage}
                      disabled={assigning || !storageLocation}
                    >
                      {assigning && <Loader2 className="size-4 animate-spin" />}
                      Assign
                    </Btn>
                  </Panel>

                  <p className="text-[12px] text-muted-foreground">
                    Received by {detail.arrived_by} on {formatTimestamp(detail.created_at)}
                  </p>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Add Item Dialog */}
      <Dialog open={addItemOpen} onOpenChange={setAddItemOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Log Item</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Barcode *</label>
              <Field
                className="mt-1"
                placeholder="0123456789012"
                value={itemForm.barcode}
                onChange={(e) => setItemForm((f) => ({ ...f, barcode: e.target.value }))}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Product Name *</label>
              <Field
                className="mt-1"
                placeholder="Cordless drill kit"
                value={itemForm.product_name}
                onChange={(e) => setItemForm((f) => ({ ...f, product_name: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="label-xs text-secondary-foreground">Width (in) *</label>
                <Field
                  className="mt-1"
                  type="number"
                  value={itemForm.width}
                  onChange={(e) => setItemForm((f) => ({ ...f, width: e.target.value }))}
                />
              </div>
              <div>
                <label className="label-xs text-secondary-foreground">Height (in) *</label>
                <Field
                  className="mt-1"
                  type="number"
                  value={itemForm.height}
                  onChange={(e) => setItemForm((f) => ({ ...f, height: e.target.value }))}
                />
              </div>
              <div>
                <label className="label-xs text-secondary-foreground">Weight (lb) *</label>
                <Field
                  className="mt-1"
                  type="number"
                  value={itemForm.weight}
                  onChange={(e) => setItemForm((f) => ({ ...f, weight: e.target.value }))}
                />
              </div>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox
                checked={itemForm.damageFlag}
                onCheckedChange={(v) => setItemForm((f) => ({ ...f, damageFlag: !!v }))}
              />
              Physical damage
            </label>
            {itemForm.damageFlag && (
              <div>
                <label className="label-xs text-secondary-foreground">Damage Note</label>
                <Textarea
                  className="mt-1 bg-input"
                  placeholder="Describe the damage..."
                  value={itemForm.damageNote}
                  onChange={(e) => setItemForm((f) => ({ ...f, damageNote: e.target.value }))}
                />
              </div>
            )}
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setAddItemOpen(false)} disabled={addingItem}>
              Cancel
            </Btn>
            <Btn onClick={handleAddItem} disabled={addingItem}>
              {addingItem && <Loader2 className="size-4 animate-spin" />}
              Log Item
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={arrivalOpen} onOpenChange={setArrivalOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Log New Arrival</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Warehouse *</label>
              {isStaff ? (
                <Field className="mt-1" disabled value={user?.warehouse_id ?? "Not assigned"} />
              ) : (
                <Select
                  className="mt-1 w-full"
                  value={arrivalWarehouseId}
                  onChange={(e) => setArrivalWarehouseId(e.target.value)}
                >
                  <option value="">Select a warehouse...</option>
                  {(warehousesQuery.data?.warehouses ?? []).map((wh) => (
                    <option key={wh.id} value={wh.id}>
                      {wh.code} · {wh.name}
                    </option>
                  ))}
                </Select>
              )}
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Tracking Number</label>
              <Field
                className="mt-1"
                placeholder="1Z9884213US"
                value={trackingNumber}
                onChange={(e) => setTrackingNumber(e.target.value)}
              />
              <p className="mt-1 text-[11px] text-muted-foreground">Optional for walk-in freight.</p>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox checked={noTicketArrival} onCheckedChange={(v) => setNoTicketArrival(!!v)} />
              No-ticket arrival
            </label>
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setArrivalOpen(false)} disabled={loggingArrival}>
              Cancel
            </Btn>
            <Btn onClick={handleLogArrival} disabled={loggingArrival}>
              {loggingArrival && <Loader2 className="size-4 animate-spin" />}
              Create Ticket
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

function TicketsPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER", "STAFF"]}>
      <TicketsPage />
    </ProtectedRoute>
  );
}
