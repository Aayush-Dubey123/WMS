import { createFileRoute } from "@tanstack/react-router";
import { Loader2, MapPin, MoreHorizontal, Plus, User } from "lucide-react";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { StatusBadge } from "@/components/wms/status-badge";
import { Btn, Field, Panel, Select, TableShell, Td, Th, Tr } from "@/components/wms/ui-bits";
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
import { storageAPI, ticketsAPI, warehousesAPI } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ProtectedRoute } from "@/lib/protected-route";
import { useQueryClient } from "@tanstack/react-query";

export const Route = createFileRoute("/warehouses")({
  head: () => ({
    meta: [
      { title: "Warehouse Facilities — Whitfield WMS" },
      {
        name: "description",
        content: "Manage warehouse facilities, storage locations and recent inbound activity.",
      },
      { property: "og:title", content: "Warehouse Facilities — Whitfield WMS" },
      {
        property: "og:description",
        content: "Facilities, storage locations and recent tickets.",
      },
    ],
  }),
  component: WarehousesPageWrapper,
});

type Warehouse = {
  id: string;
  code: string;
  name: string;
  address: string | null;
  manager_id: string | null;
  is_active: boolean;
  created_at: string;
};

type StorageLocation = {
  id: string;
  warehouse_id: string;
  zone: string;
  rack: string;
  bin: string;
  location_code: string;
  is_occupied: boolean;
  created_at: string;
};

type Ticket = {
  id: string;
  ticket_id?: string;
  warehouse_id: string;
  status: string;
  created_at?: string;
};

type CreateForm = { code: string; name: string; address: string };
type EditForm = { name: string; address: string };
type LocationForm = { zone: string; rack: string; bin: string };

function WarehousesPageContent() {
  const { hasRole } = useAuth();
  const canManage = hasRole(["OWNER"]);
  const canManageLocations = hasRole(["OWNER", "MANAGER"]);
  const queryClient = useQueryClient();

  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>({ code: "", name: "", address: "" });
  const [isCreating, setIsCreating] = useState(false);

  const [editOpen, setEditOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Warehouse | null>(null);
  const [editForm, setEditForm] = useState<EditForm>({ name: "", address: "" });
  const [isEditing, setIsEditing] = useState(false);

  const [selectedWarehouseId, setSelectedWarehouseId] = useState<string>("");

  const [locationOpen, setLocationOpen] = useState(false);
  const [locationForm, setLocationForm] = useState<LocationForm>({ zone: "", rack: "", bin: "" });
  const [isCreatingLocation, setIsCreatingLocation] = useState(false);

  const {
    data: warehousesData,
    isLoading: warehousesLoading,
    refetch: refetchWarehouses,
  } = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehousesAPI.getAll(0, 100) as Promise<{ warehouses: Warehouse[]; total: number }>,
  });

  const warehouses = warehousesData?.warehouses ?? [];

  useEffect(() => {
    if (!selectedWarehouseId && warehouses.length > 0) {
      setSelectedWarehouseId(warehouses[0]!.id);
    }
  }, [warehouses, selectedWarehouseId]);

  const { data: storageData, isLoading: storageLoading } = useQuery({
    queryKey: ["storage-locations", selectedWarehouseId],
    queryFn: () =>
      storageAPI.list(0, 100, selectedWarehouseId) as Promise<{ locations: StorageLocation[]; total: number }>,
    enabled: !!selectedWarehouseId,
  });

  const { data: ticketsData, isLoading: ticketsLoading } = useQuery({
    queryKey: ["tickets", "recent"],
    queryFn: () => ticketsAPI.getAll(0, 6) as Promise<{ tickets: Ticket[]; total: number }>,
  });

  const locations = storageData?.locations ?? [];
  const tickets = ticketsData?.tickets ?? [];

  const onCreateSubmit = async () => {
    if (!createForm.code.trim() || !createForm.name.trim()) {
      toast.error("Code and name are required");
      return;
    }
    setIsCreating(true);
    try {
      const trimmedAddress = createForm.address.trim();
      await warehousesAPI.create({
        code: createForm.code.trim().toUpperCase(),
        name: createForm.name.trim(),
        ...(trimmedAddress ? { address: trimmedAddress } : {}),
      });
      toast.success("Warehouse created");
      setCreateOpen(false);
      setCreateForm({ code: "", name: "", address: "" });
      refetchWarehouses();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create warehouse");
    } finally {
      setIsCreating(false);
    }
  };

  const openEdit = (w: Warehouse) => {
    setEditTarget(w);
    setEditForm({ name: w.name, address: w.address ?? "" });
    setEditOpen(true);
  };

  const onEditSubmit = async () => {
    if (!editTarget) return;
    setIsEditing(true);
    try {
      await warehousesAPI.update(editTarget.id, {
        name: editForm.name.trim(),
        address: editForm.address.trim() || undefined,
      });
      toast.success("Warehouse updated");
      setEditOpen(false);
      setEditTarget(null);
      refetchWarehouses();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update warehouse");
    } finally {
      setIsEditing(false);
    }
  };

  const onCreateLocationSubmit = async () => {
    if (!selectedWarehouseId) {
      toast.error("Select a warehouse first");
      return;
    }
    if (!locationForm.zone.trim() || !locationForm.rack.trim() || !locationForm.bin.trim()) {
      toast.error("Zone, rack and bin are required");
      return;
    }
    setIsCreatingLocation(true);
    try {
      await storageAPI.create({
        warehouse_id: selectedWarehouseId,
        zone: locationForm.zone.trim(),
        rack: locationForm.rack.trim(),
        bin: locationForm.bin.trim(),
      });
      toast.success("Storage location created");
      setLocationOpen(false);
      setLocationForm({ zone: "", rack: "", bin: "" });
      queryClient.invalidateQueries({ queryKey: ["storage-locations", selectedWarehouseId] });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create storage location");
    } finally {
      setIsCreatingLocation(false);
    }
  };

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Warehouses" }]}
      title="Warehouse Facilities"
      actions={
        canManage ? (
          <Btn onClick={() => setCreateOpen(true)}>
            <Plus className="size-4" /> Create Warehouse
          </Btn>
        ) : undefined
      }
    >
      {warehousesLoading ? (
        <div className="py-12 text-center">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">Loading warehouses...</p>
        </div>
      ) : warehouses.length === 0 ? (
        <Panel className="py-12 text-center text-sm text-muted-foreground">No warehouses found.</Panel>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {warehouses.map((w) => (
            <Panel
              key={w.id}
              className={
                "hover:border-primary hover:shadow-e2 " +
                (w.id === selectedWarehouseId ? "border-primary" : "")
              }
            >
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-primary">{w.code}</h2>
                  <p className="mt-1 text-base font-medium">{w.name}</p>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger
                    aria-label={`Actions for ${w.code}`}
                    className="grid size-8 place-items-center rounded-md hover:bg-border"
                  >
                    <MoreHorizontal className="size-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="shadow-e3">
                    <DropdownMenuItem disabled={!canManage} onClick={() => openEdit(w)}>
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setSelectedWarehouseId(w.id)}>
                      View storage &amp; tickets
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              <p className="mt-3 flex items-start gap-2 text-[12px] text-muted-foreground">
                <MapPin className="mt-0.5 size-3.5 shrink-0" /> {w.address || "No address on file"}
              </p>
              <p className="mt-2 flex items-center gap-2 text-[13px] text-secondary-foreground">
                <User className="size-3.5" /> {w.manager_id || "Unassigned"}
              </p>

              <div className="mt-4">
                <StatusBadge status={w.is_active ? "ACTIVE" : "INACTIVE"} />
              </div>
            </Panel>
          ))}
        </div>
      )}

      <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div>
          <TableShell
            toolbar={
              <div className="flex w-full flex-wrap items-center gap-3">
                <h3 className="mr-auto text-base font-semibold">Storage Locations</h3>
                {warehouses.length > 1 && (
                  <Select
                    value={selectedWarehouseId}
                    onChange={(e) => setSelectedWarehouseId(e.target.value)}
                  >
                    {warehouses.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.code}
                      </option>
                    ))}
                  </Select>
                )}
                {canManageLocations && (
                  <Btn
                    variant="secondary"
                    disabled={!selectedWarehouseId}
                    onClick={() => setLocationOpen(true)}
                  >
                    <Plus className="size-4" /> Add Location
                  </Btn>
                )}
              </div>
            }
          >
            <thead>
              <tr>
                <Th>Zone</Th>
                <Th>Rack</Th>
                <Th>Bin</Th>
                <Th>Code</Th>
                <Th>Occupied</Th>
              </tr>
            </thead>
            <tbody>
              {storageLoading ? (
                <Tr>
                  <Td colSpan={5} className="py-8 text-center text-muted-foreground">
                    <Loader2 className="mx-auto size-5 animate-spin text-primary" />
                  </Td>
                </Tr>
              ) : locations.length > 0 ? (
                locations.map((l) => (
                  <Tr key={l.id}>
                    <Td>{l.zone}</Td>
                    <Td>{l.rack}</Td>
                    <Td>{l.bin}</Td>
                    <Td className="font-mono text-[12px] text-primary">{l.location_code}</Td>
                    <Td>
                      <StatusBadge status={l.is_occupied ? "STORED" : "PENDING"} />
                    </Td>
                  </Tr>
                ))
              ) : (
                <Tr>
                  <Td colSpan={5} className="py-8 text-center text-muted-foreground">
                    No storage locations found
                  </Td>
                </Tr>
              )}
            </tbody>
          </TableShell>
        </div>

        <div>
          <TableShell toolbar={<h3 className="mr-auto text-base font-semibold">Recent Tickets</h3>}>
            <thead>
              <tr>
                <Th>Ticket</Th>
                <Th>Warehouse</Th>
                <Th>Status</Th>
              </tr>
            </thead>
            <tbody>
              {ticketsLoading ? (
                <Tr>
                  <Td colSpan={3} className="py-8 text-center text-muted-foreground">
                    <Loader2 className="mx-auto size-5 animate-spin text-primary" />
                  </Td>
                </Tr>
              ) : tickets.length > 0 ? (
                tickets.map((t) => (
                  <Tr key={t.id}>
                    <Td className="font-mono text-[12px] text-primary">{t.ticket_id || t.id}</Td>
                    <Td className="text-[12px] text-muted-foreground">{t.warehouse_id}</Td>
                    <Td>
                      <StatusBadge status={t.status} />
                    </Td>
                  </Tr>
                ))
              ) : (
                <Tr>
                  <Td colSpan={3} className="py-8 text-center text-muted-foreground">
                    No tickets found
                  </Td>
                </Tr>
              )}
            </tbody>
          </TableShell>
        </div>
      </section>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Create Warehouse</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Code *</label>
              <Field
                className="mt-1 uppercase"
                maxLength={6}
                placeholder="WHT-04"
                value={createForm.code}
                onChange={(e) => setCreateForm((f) => ({ ...f, code: e.target.value }))}
                disabled={isCreating}
              />
              <p className="mt-1 text-[11px] text-muted-foreground">Short uppercase facility code.</p>
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Name *</label>
              <Field
                className="mt-1"
                placeholder="Eastgate Depot"
                value={createForm.name}
                onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))}
                disabled={isCreating}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Address</label>
              <Textarea
                className="mt-1 bg-input"
                placeholder="Street, city, state"
                value={createForm.address}
                onChange={(e) => setCreateForm((f) => ({ ...f, address: e.target.value }))}
                disabled={isCreating}
              />
            </div>
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setCreateOpen(false)} disabled={isCreating}>
              Cancel
            </Btn>
            <Btn onClick={onCreateSubmit} disabled={isCreating}>
              {isCreating && <Loader2 className="size-4 animate-spin" />} Create Warehouse
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Edit {editTarget?.code}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Name</label>
              <Field
                className="mt-1"
                value={editForm.name}
                onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))}
                disabled={isEditing}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Address</label>
              <Textarea
                className="mt-1 bg-input"
                value={editForm.address}
                onChange={(e) => setEditForm((f) => ({ ...f, address: e.target.value }))}
                disabled={isEditing}
              />
            </div>
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setEditOpen(false)} disabled={isEditing}>
              Cancel
            </Btn>
            <Btn onClick={onEditSubmit} disabled={isEditing}>
              {isEditing && <Loader2 className="size-4 animate-spin" />} Save Changes
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={locationOpen} onOpenChange={setLocationOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Add Storage Location</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label-xs text-secondary-foreground">Zone *</label>
              <Field
                className="mt-1"
                placeholder="A"
                value={locationForm.zone}
                onChange={(e) => setLocationForm((f) => ({ ...f, zone: e.target.value }))}
                disabled={isCreatingLocation}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Rack *</label>
              <Field
                className="mt-1"
                placeholder="04"
                value={locationForm.rack}
                onChange={(e) => setLocationForm((f) => ({ ...f, rack: e.target.value }))}
                disabled={isCreatingLocation}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Bin *</label>
              <Field
                className="mt-1"
                placeholder="12"
                value={locationForm.bin}
                onChange={(e) => setLocationForm((f) => ({ ...f, bin: e.target.value }))}
                disabled={isCreatingLocation}
              />
            </div>
          </div>
          <p className="text-[11px] text-muted-foreground">
            Creates location code {locationForm.zone || "A"}-{locationForm.rack || "04"}-{locationForm.bin || "12"} for{" "}
            {warehouses.find((w) => w.id === selectedWarehouseId)?.code ?? "the selected warehouse"}.
          </p>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setLocationOpen(false)} disabled={isCreatingLocation}>
              Cancel
            </Btn>
            <Btn onClick={onCreateLocationSubmit} disabled={isCreatingLocation}>
              {isCreatingLocation && <Loader2 className="size-4 animate-spin" />} Add Location
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

function WarehousesPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER"]}>
      <WarehousesPageContent />
    </ProtectedRoute>
  );
}
