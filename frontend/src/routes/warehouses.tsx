import { createFileRoute } from "@tanstack/react-router";
import { MapPin, MoreHorizontal, Plus, User } from "lucide-react";
import { useState } from "react";
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
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { tickets, warehouseList } from "@/lib/wms-data";

export const Route = createFileRoute("/warehouses")({
  head: () => ({
    meta: [
      { title: "Warehouse Facilities — Whitfield WMS" },
      {
        name: "description",
        content:
          "Manage warehouse facilities, assigned managers, storage locations and capacity utilization.",
      },
      { property: "og:title", content: "Warehouse Facilities — Whitfield WMS" },
      {
        property: "og:description",
        content: "Facilities, managers, storage locations and capacity utilization.",
      },
    ],
  }),
  component: WarehousesPage,
});

const locations = [
  { zone: "A", rack: "04", bin: "12", code: "A-04-12", occupied: true, capacity: "48 units" },
  { zone: "A", rack: "05", bin: "02", code: "A-05-02", occupied: false, capacity: "48 units" },
  { zone: "B", rack: "02", bin: "07", code: "B-02-07", occupied: true, capacity: "96 units" },
  { zone: "C", rack: "11", bin: "30", code: "C-11-30", occupied: false, capacity: "24 units" },
];

function WarehousesPage() {
  const [open, setOpen] = useState(false);

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Warehouses" }]}
      title="Warehouse Facilities"
      actions={
        <Btn onClick={() => setOpen(true)}>
          <Plus className="size-4" /> Create Warehouse
        </Btn>
      }
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {warehouseList.map((w) => (
          <Panel key={w.code} className="hover:border-primary hover:shadow-e2">
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
                  <DropdownMenuItem>Edit</DropdownMenuItem>
                  <DropdownMenuItem>View details</DropdownMenuItem>
                  <DropdownMenuItem className="text-destructive focus:text-destructive">
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <p className="mt-3 flex items-start gap-2 text-[12px] text-muted-foreground">
              <MapPin className="mt-0.5 size-3.5 shrink-0" /> {w.address}
            </p>
            <p className="mt-2 flex items-center gap-2 text-[13px] text-secondary-foreground">
              <User className="size-3.5" /> {w.manager}
            </p>

            <div className="mt-4 flex flex-wrap gap-2 text-[11px] font-semibold">
              {[
                `Tickets: ${w.tickets}`,
                `Items: ${w.items}`,
                `Storage: ${w.utilization}%`,
              ].map((b) => (
                <span key={b} className="rounded-[20px] bg-secondary px-3 py-1 text-secondary-foreground">
                  {b}
                </span>
              ))}
            </div>

            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-secondary">
              <div className="h-full rounded-full bg-primary" style={{ width: `${w.utilization}%` }} />
            </div>

            <div className="mt-4">
              <StatusBadge status={w.active ? "ACTIVE" : "INACTIVE"} />
            </div>
          </Panel>
        ))}
      </div>

      <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div>
          <TableShell toolbar={<h3 className="mr-auto text-base font-semibold">Storage Locations</h3>}>
            <thead>
              <tr>
                <Th>Zone</Th>
                <Th>Rack</Th>
                <Th>Bin</Th>
                <Th>Code</Th>
                <Th>Occupied</Th>
                <Th>Capacity</Th>
              </tr>
            </thead>
            <tbody>
              {locations.map((l) => (
                <Tr key={l.code}>
                  <Td>{l.zone}</Td>
                  <Td>{l.rack}</Td>
                  <Td>{l.bin}</Td>
                  <Td className="font-mono text-[12px] text-primary">{l.code}</Td>
                  <Td>
                    <StatusBadge status={l.occupied ? "STORED" : "PENDING"} />
                  </Td>
                  <Td className="text-[12px] text-muted-foreground">{l.capacity}</Td>
                </Tr>
              ))}
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
                <Th>Arrived</Th>
              </tr>
            </thead>
            <tbody>
              {tickets.slice(0, 6).map((t) => (
                <Tr key={t.id}>
                  <Td className="font-mono text-[12px] text-primary">{t.id}</Td>
                  <Td className="text-[12px] text-muted-foreground">{t.warehouse}</Td>
                  <Td>
                    <StatusBadge status={t.status} />
                  </Td>
                  <Td className="text-[12px] text-muted-foreground">{t.arrived}</Td>
                </Tr>
              ))}
            </tbody>
          </TableShell>
        </div>
      </section>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Create Warehouse</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Code *</label>
              <Field className="mt-1 uppercase" maxLength={6} placeholder="WHT-04" />
              <p className="mt-1 text-[11px] text-muted-foreground">Short uppercase facility code.</p>
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Name *</label>
              <Field className="mt-1" placeholder="Eastgate Depot" />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Address</label>
              <Textarea className="mt-1 bg-input" placeholder="Street, city, state" />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Assign Manager</label>
              <Select className="mt-1 w-full">
                <option>Unassigned</option>
                <option>John Mercer</option>
                <option>Ada Sloane</option>
                <option>Ravi Menon</option>
              </Select>
            </div>
            <label className="flex items-center justify-between text-sm">
              Active facility
              <Switch defaultChecked />
            </label>
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Btn>
            <Btn
              onClick={() => {
                setOpen(false);
                toast.success("Warehouse created");
              }}
            >
              Create Warehouse
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
