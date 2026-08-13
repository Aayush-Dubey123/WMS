import { createFileRoute } from "@tanstack/react-router";
import { AlertTriangle, Check, Copy, MoreHorizontal, Plus } from "lucide-react";
import { useMemo, useState } from "react";
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
import { tickets } from "@/lib/wms-data";

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
  component: TicketsPage,
});

function TicketsPage() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("ALL");
  const [openId, setOpenId] = useState<string | null>(null);
  const [arrivalOpen, setArrivalOpen] = useState(false);

  const rows = useMemo(
    () =>
      tickets.filter(
        (t) =>
          (status === "ALL" || t.status === status) &&
          t.id.toLowerCase().includes(query.toLowerCase()),
      ),
    [query, status],
  );

  const active = tickets.find((t) => t.id === openId) ?? null;

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
          {["ALL", "PENDING", "INSPECTED", "STORED", "PICKED"].map((s) => (
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
        <Select defaultValue="ALL" className="ml-auto">
          <option value="ALL">All warehouses</option>
          <option>WHT-01 · Whitfield North</option>
          <option>WHT-02 · Dalton Yard</option>
          <option>WHT-03 · Redmoor</option>
        </Select>
      </div>

      <TableShell>
        <thead>
          <tr>
            <Th className="w-10" />
            <Th>Ticket ID</Th>
            <Th>Warehouse</Th>
            <Th className="text-right">Items</Th>
            <Th>Status</Th>
            <Th>Arrived</Th>
            <Th>Storage</Th>
            <Th>Manager</Th>
            <Th className="w-[60px]" />
          </tr>
        </thead>
        <tbody>
          {rows.map((t) => (
            <Tr key={t.id} className="cursor-pointer" onClick={() => setOpenId(t.id)}>
              <Td onClick={(e) => e.stopPropagation()}>
                <Checkbox aria-label={`Select ${t.id}`} />
              </Td>
              <Td className="font-mono text-[13px] text-primary">{t.id}</Td>
              <Td className="text-[12px] text-muted-foreground">{t.warehouse}</Td>
              <Td className="text-right text-[12px] text-muted-foreground">{t.items.length}</Td>
              <Td>
                <StatusBadge status={t.status} />
              </Td>
              <Td className="text-[12px] text-muted-foreground">{t.arrived}</Td>
              <Td className="font-mono text-[12px]">{t.storage}</Td>
              <Td className="text-[12px] text-secondary-foreground">{t.manager}</Td>
              <Td onClick={(e) => e.stopPropagation()}>
                <DropdownMenu>
                  <DropdownMenuTrigger
                    aria-label="Row actions"
                    className="grid size-8 place-items-center rounded-md hover:bg-border"
                  >
                    <MoreHorizontal className="size-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="shadow-e3">
                    <DropdownMenuItem onClick={() => setOpenId(t.id)}>View</DropdownMenuItem>
                    <DropdownMenuItem>Assign storage</DropdownMenuItem>
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
        <Pager total={rows.length} shown={25} />
      </div>

      <Dialog open={!!active} onOpenChange={(o) => !o && setOpenId(null)}>
        <DialogContent className="max-h-[85vh] overflow-y-auto shadow-e3 sm:max-w-[900px]">
          {active && (
            <>
              <DialogHeader>
                <DialogTitle className="flex flex-wrap items-center gap-3">
                  <span className="font-mono">{active.id}</span>
                  <StatusBadge status={active.status} />
                </DialogTitle>
              </DialogHeader>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-[2fr_1fr]">
                <div className="space-y-4">
                  <Panel className="p-4">
                    <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                      {[
                        ["Tracking", active.tracking],
                        ["Carrier", active.carrier],
                        ["Arrived", active.arrived],
                      ].map(([k, v]) => (
                        <div key={k}>
                          <dt className="label-xs text-muted-foreground uppercase">{k}</dt>
                          <dd className="mt-1 flex items-center gap-2 font-mono text-[13px]">
                            {v}
                            {k === "Tracking" && (
                              <button
                                aria-label="Copy tracking number"
                                onClick={() => toast("Tracking number copied")}
                              >
                                <Copy className="size-3.5 text-muted-foreground hover:text-primary" />
                              </button>
                            )}
                          </dd>
                        </div>
                      ))}
                    </dl>
                    {active.noTicket && (
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
                        <Th className="text-right">Qty</Th>
                        <Th>Dimensions</Th>
                        <Th>Storage</Th>
                        <Th>Status</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {active.items.map((it, i) => (
                        <Tr key={i}>
                          <Td className="font-mono text-[12px] text-muted-foreground">{it.barcode}</Td>
                          <Td className="font-medium">
                            {it.product}
                            {it.damaged && (
                              <span className="ml-2 rounded-[20px] bg-warning/20 px-2 py-0.5 text-[11px] font-semibold text-warning">
                                DAMAGED
                              </span>
                            )}
                          </Td>
                          <Td className="text-right">{it.qty}</Td>
                          <Td className="text-[12px] text-muted-foreground">
                            {it.dims} · {it.weight}
                          </Td>
                          <Td>
                            <span className="rounded-[20px] bg-primary/15 px-2.5 py-1 font-mono text-[11px] text-primary">
                              {it.storage}
                            </span>
                          </Td>
                          <Td>
                            <StatusBadge status={it.status} />
                          </Td>
                        </Tr>
                      ))}
                    </tbody>
                  </TableShell>
                  <Btn variant="secondary">
                    <Plus className="size-4" /> Add Item
                  </Btn>
                </div>

                <div className="space-y-4">
                  <Panel className="p-4">
                    <h3 className="text-base">Timeline</h3>
                    <ol className="mt-3 space-y-3 text-sm">
                      {["Arrived", "Inspected", "Stored"].map((s, i) => (
                        <li key={s} className="flex items-center gap-3">
                          <span className="grid size-6 place-items-center rounded-full border border-primary bg-primary/20 text-primary">
                            <Check className="size-3.5" />
                          </span>
                          <span className={i === 2 ? "font-semibold text-primary" : ""}>{s}</span>
                        </li>
                      ))}
                    </ol>
                  </Panel>

                  {active.status === "INSPECTED" && (
                    <Panel className="p-4">
                      <h3 className="text-base">Manager approval</h3>
                      <p className="mt-1 text-[13px] text-muted-foreground">
                        Awaiting manager approval before storage.
                      </p>
                      <div className="mt-3 flex gap-3">
                        <Btn onClick={() => toast.success("Ticket approved")}>Approve</Btn>
                        <Btn variant="secondary" onClick={() => toast.error("Ticket rejected")}>
                          Reject
                        </Btn>
                      </div>
                    </Panel>
                  )}

                  <Panel className="p-4">
                    <h3 className="text-base">Assign storage</h3>
                    <Select className="mt-3 w-full">
                      <option>Select storage location</option>
                      <option>A-04-12</option>
                      <option>B-02-07</option>
                      <option>C-11-30</option>
                    </Select>
                    <Btn
                      variant="secondary"
                      className="mt-3 w-full"
                      onClick={() => toast.success("Storage assigned")}
                    >
                      Assign
                    </Btn>
                  </Panel>

                  <p className="text-[12px] text-muted-foreground">
                    Created by {active.manager} on {active.arrived}
                  </p>
                </div>
              </div>
            </>
          )}
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
              <Select className="mt-1 w-full">
                <option>WHT-01 · Whitfield North</option>
                <option>WHT-02 · Dalton Yard</option>
                <option>WHT-03 · Redmoor</option>
              </Select>
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Tracking Number</label>
              <Field className="mt-1" placeholder="1Z9884213US" />
              <p className="mt-1 text-[11px] text-muted-foreground">Optional for walk-in freight.</p>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox /> No-ticket arrival
            </label>
            <div>
              <label className="label-xs text-secondary-foreground">Comments</label>
              <Textarea className="mt-1 bg-input" placeholder="Notes for the receiving team..." />
            </div>
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setArrivalOpen(false)}>
              Cancel
            </Btn>
            <Btn
              onClick={() => {
                setArrivalOpen(false);
                toast.success("Ticket RNO-20260813-025 created");
              }}
            >
              Create Ticket
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
