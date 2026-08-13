import { createFileRoute } from "@tanstack/react-router";
import { Check, Eye, EyeOff, MoreHorizontal, Plus, X } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { users } from "@/lib/wms-data";

export const Route = createFileRoute("/users")({
  head: () => ({
    meta: [
      { title: "User Management — Whitfield WMS" },
      {
        name: "description",
        content:
          "Create managers, assign warehouses and control access for owners, managers and floor staff.",
      },
      { property: "og:title", content: "User Management — Whitfield WMS" },
      {
        property: "og:description",
        content: "Manage warehouse roles, access and account status.",
      },
    ],
  }),
  component: UsersPage,
});

const rules = [
  { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
  { label: "Contains uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "Contains number", test: (p: string) => /\d/.test(p) },
  { label: "Contains special character", test: (p: string) => /[^A-Za-z0-9]/.test(p) },
];

function UsersPage() {
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("ALL");
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);

  const rows = useMemo(
    () =>
      users.filter(
        (u) =>
          (role === "ALL" || u.role === role) &&
          (u.name.toLowerCase().includes(query.toLowerCase()) ||
            u.email.toLowerCase().includes(query.toLowerCase())),
      ),
    [query, role],
  );

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Users" }]}
      title="User Management"
      actions={
        <Btn onClick={() => setOpen(true)}>
          <Plus className="size-4" /> Create Manager
        </Btn>
      }
    >
      <div className="mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-border bg-card p-4 shadow-e1">
        <SearchField
          className="w-full sm:w-[280px]"
          placeholder="Search name or email..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="ALL">All roles</option>
          <option value="OWNER">Owner</option>
          <option value="MANAGER">Manager</option>
          <option value="STAFF">Staff</option>
        </Select>
        <label className="flex items-center gap-2 text-sm text-secondary-foreground">
          <Checkbox defaultChecked /> Active only
        </label>
      </div>

      <TableShell>
        <thead>
          <tr>
            <Th className="w-10" />
            <Th>User</Th>
            <Th>Role</Th>
            <Th>Warehouse</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th className="w-[60px]" />
          </tr>
        </thead>
        <tbody>
          {rows.map((u, i) => (
            <Tr key={u.email}>
              <Td>
                <Checkbox aria-label={`Select ${u.name}`} />
              </Td>
              <Td>
                <div className="flex items-center gap-3">
                  <span
                    className={
                      "grid size-8 shrink-0 place-items-center rounded-full text-[12px] font-semibold " +
                      (u.role === "OWNER"
                        ? "bg-primary/20 text-primary"
                        : u.role === "MANAGER"
                          ? "bg-info/20 text-info"
                          : "bg-secondary text-secondary-foreground")
                    }
                  >
                    {u.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </span>
                  <span className="leading-tight">
                    <span className="block text-sm font-semibold">{u.name}</span>
                    <span className="block text-[12px] text-muted-foreground">{u.email}</span>
                  </span>
                </div>
              </Td>
              <Td>
                <StatusBadge status={u.role} />
              </Td>
              <Td className="text-[12px] text-muted-foreground">{u.warehouse}</Td>
              <Td>
                <StatusBadge status={u.active ? "ACTIVE" : "INACTIVE"} />
              </Td>
              <Td className="text-[12px] text-muted-foreground">{u.created}</Td>
              <Td>
                <DropdownMenu>
                  <DropdownMenuTrigger
                    aria-label={`Actions for ${u.name} ${i}`}
                    className="grid size-8 place-items-center rounded-md hover:bg-border"
                  >
                    <MoreHorizontal className="size-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="shadow-e3">
                    <DropdownMenuItem>Edit</DropdownMenuItem>
                    <DropdownMenuItem>Reset password</DropdownMenuItem>
                    <DropdownMenuItem className="text-destructive focus:text-destructive">
                      Deactivate
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

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[520px]">
          <DialogHeader>
            <DialogTitle>Create New Manager</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Full Name *</label>
              <Field className="mt-1" placeholder="Ada Sloane" />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Email *</label>
              <Field className="mt-1" type="email" placeholder="ada@whitfieldwms.com" />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Password *</label>
              <div className="relative mt-1">
                <Field
                  type={show ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10"
                />
                <button
                  type="button"
                  aria-label="Toggle password visibility"
                  onClick={() => setShow((s) => !s)}
                  className="absolute top-1/2 right-2 grid size-7 -translate-y-1/2 place-items-center rounded-md text-muted-foreground hover:bg-surface-hover"
                >
                  {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              </div>
              <ul className="mt-2 space-y-1">
                {rules.map((r) => {
                  const ok = r.test(password);
                  return (
                    <li
                      key={r.label}
                      className={
                        "flex items-center gap-2 text-[11px] " +
                        (ok ? "text-primary" : "text-muted-foreground")
                      }
                    >
                      {ok ? <Check className="size-3" /> : <X className="size-3" />} {r.label}
                    </li>
                  );
                })}
              </ul>
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Warehouse *</label>
              <Select className="mt-1 w-full">
                <option>WHT-01 · Whitfield North</option>
                <option>WHT-02 · Dalton Yard</option>
                <option>WHT-03 · Redmoor</option>
              </Select>
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Status</label>
              <RadioGroup defaultValue="active" className="mt-2 flex gap-6">
                <label className="flex items-center gap-2 text-sm">
                  <RadioGroupItem value="active" /> Active
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <RadioGroupItem value="inactive" /> Inactive
                </label>
              </RadioGroup>
            </div>
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Btn>
            <Btn
              onClick={() => {
                setOpen(false);
                toast.success("Manager account created");
              }}
            >
              Create Manager
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
