import { createFileRoute } from "@tanstack/react-router";
import { Check, Eye, EyeOff, Loader2, MoreHorizontal, Plus, X } from "lucide-react";
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
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
import { useAuth } from "@/lib/auth-context";
import { ProtectedRoute } from "@/lib/protected-route";
import { usersAPI, warehousesAPI } from "@/lib/api";

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
  component: UsersPageWrapper,
});

type WmsUser = {
  id: string;
  email: string;
  full_name: string;
  role: "OWNER" | "MANAGER" | "STAFF";
  warehouse_id: string | null;
  experience_tier: "ROOKIE" | "EXPERIENCED" | null;
  function_roles: string[];
  status: "ACTIVE" | "INACTIVE" | "SUSPENDED";
  created_at: string;
};

type Warehouse = { id: string; code: string; name: string };

const functionRoleOptions = ["LISTING", "PACKING", "RECEIVING", "INSPECTION", "STORAGE"] as const;

const rules = [
  { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
  { label: "Contains uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "Contains number", test: (p: string) => /\d/.test(p) },
  { label: "Contains special character", test: (p: string) => /[^A-Za-z0-9]/.test(p) },
];

function UsersPageContent() {
  const { hasRole } = useAuth();
  const isOwner = hasRole(["OWNER"]);
  const isManager = hasRole(["MANAGER"]);

  const [query, setQuery] = useState("");
  const [role, setRole] = useState("ALL");
  const [activeOnly, setActiveOnly] = useState(false);

  const [createOpen, setCreateOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [managerForm, setManagerForm] = useState({ full_name: "", email: "", warehouse_id: "" });
  const [staffForm, setStaffForm] = useState({
    full_name: "",
    email: "",
    experience_tier: "ROOKIE" as "ROOKIE" | "EXPERIENCED",
    function_roles: [] as string[],
  });

  const [editOpen, setEditOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<WmsUser | null>(null);
  const [editForm, setEditForm] = useState({
    full_name: "",
    experience_tier: "ROOKIE" as "ROOKIE" | "EXPERIENCED",
    function_roles: [] as string[],
  });
  const [isEditing, setIsEditing] = useState(false);

  const {
    data: usersData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["users"],
    queryFn: () => usersAPI.getAll(0, 50) as Promise<{ users: WmsUser[]; total: number }>,
  });

  const { data: warehousesData } = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehousesAPI.getAll(0, 100) as Promise<{ warehouses: Warehouse[]; total: number }>,
    enabled: isOwner,
  });

  const users = usersData?.users ?? [];
  const warehouses = warehousesData?.warehouses ?? [];

  const rows = useMemo(
    () =>
      users.filter(
        (u) =>
          (role === "ALL" || u.role === role) &&
          (!activeOnly || u.status === "ACTIVE") &&
          (u.full_name.toLowerCase().includes(query.toLowerCase()) ||
            u.email.toLowerCase().includes(query.toLowerCase())),
      ),
    [users, query, role, activeOnly],
  );

  const resetCreateForm = () => {
    setManagerForm({ full_name: "", email: "", warehouse_id: "" });
    setStaffForm({ full_name: "", email: "", experience_tier: "ROOKIE", function_roles: [] });
    setPassword("");
    setShow(false);
  };

  const onCreateSubmit = async () => {
    setIsCreating(true);
    try {
      if (isOwner) {
        if (!managerForm.full_name.trim() || !managerForm.email.trim() || !managerForm.warehouse_id || !password) {
          toast.error("Fill in all required fields");
          setIsCreating(false);
          return;
        }
        await usersAPI.createManager({
          email: managerForm.email.trim(),
          full_name: managerForm.full_name.trim(),
          password,
          warehouse_id: managerForm.warehouse_id,
        });
        toast.success("Manager account created");
      } else if (isManager) {
        if (!staffForm.full_name.trim() || !staffForm.email.trim() || !password) {
          toast.error("Fill in all required fields");
          setIsCreating(false);
          return;
        }
        await usersAPI.createStaff({
          email: staffForm.email.trim(),
          full_name: staffForm.full_name.trim(),
          password,
          experience_tier: staffForm.experience_tier,
          function_roles: staffForm.function_roles,
        });
        toast.success("Staff account created");
      }
      setCreateOpen(false);
      resetCreateForm();
      refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create account");
    } finally {
      setIsCreating(false);
    }
  };

  const openEdit = (u: WmsUser) => {
    setEditTarget(u);
    setEditForm({
      full_name: u.full_name,
      experience_tier: u.experience_tier ?? "ROOKIE",
      function_roles: u.function_roles ?? [],
    });
    setEditOpen(true);
  };

  const onEditSubmit = async () => {
    if (!editTarget) return;
    setIsEditing(true);
    try {
      await usersAPI.updateStaff(editTarget.id, {
        full_name: editForm.full_name.trim(),
        experience_tier: editForm.experience_tier,
        function_roles: editForm.function_roles,
      });
      toast.success("Staff account updated");
      setEditOpen(false);
      setEditTarget(null);
      refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update staff account");
    } finally {
      setIsEditing(false);
    }
  };

  const onDeactivate = async (u: WmsUser) => {
    try {
      await usersAPI.remove(u.id);
      toast.success(`${u.full_name} deactivated`);
      refetch();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to deactivate user");
    }
  };

  const canCreate = isOwner || isManager;

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Users" }]}
      title="User Management"
      actions={
        canCreate ? (
          <Btn onClick={() => setCreateOpen(true)}>
            <Plus className="size-4" /> {isOwner ? "Create Manager" : "Create Staff"}
          </Btn>
        ) : undefined
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
          <Checkbox checked={activeOnly} onCheckedChange={(v) => setActiveOnly(!!v)} /> Active only
        </label>
      </div>

      {isLoading ? (
        <div className="py-12 text-center">
          <Loader2 className="mx-auto size-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">Loading users...</p>
        </div>
      ) : (
        <>
          <TableShell>
            <thead>
              <tr>
                <Th>User</Th>
                <Th>Role</Th>
                <Th>Warehouse</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th className="w-[60px]" />
              </tr>
            </thead>
            <tbody>
              {rows.length > 0 ? (
                rows.map((u, i) => (
                  <Tr key={u.id}>
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
                          {u.full_name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .slice(0, 2)}
                        </span>
                        <span className="leading-tight">
                          <span className="block text-sm font-semibold">{u.full_name}</span>
                          <span className="block text-[12px] text-muted-foreground">{u.email}</span>
                        </span>
                      </div>
                    </Td>
                    <Td>
                      <StatusBadge status={u.role} />
                    </Td>
                    <Td className="text-[12px] text-muted-foreground">{u.warehouse_id || "—"}</Td>
                    <Td>
                      <StatusBadge status={u.status} />
                    </Td>
                    <Td className="text-[12px] text-muted-foreground">{u.created_at}</Td>
                    <Td>
                      <DropdownMenu>
                        <DropdownMenuTrigger
                          aria-label={`Actions for ${u.full_name} ${i}`}
                          className="grid size-8 place-items-center rounded-md hover:bg-border"
                        >
                          <MoreHorizontal className="size-4" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="shadow-e3">
                          <DropdownMenuItem disabled={u.role !== "STAFF"} onClick={() => openEdit(u)}>
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() => onDeactivate(u)}
                          >
                            Deactivate
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </Td>
                  </Tr>
                ))
              ) : (
                <Tr>
                  <Td colSpan={6} className="py-8 text-center text-muted-foreground">
                    No users found
                  </Td>
                </Tr>
              )}
            </tbody>
          </TableShell>
          <div className="rounded-b-xl border-x border-b border-border bg-card">
            <Pager total={rows.length} shown={25} />
          </div>
        </>
      )}

      <Dialog
        open={createOpen}
        onOpenChange={(v) => {
          setCreateOpen(v);
          if (!v) resetCreateForm();
        }}
      >
        <DialogContent className="shadow-e3 sm:max-w-[520px]">
          <DialogHeader>
            <DialogTitle>{isOwner ? "Create New Manager" : "Create New Staff"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Full Name *</label>
              <Field
                className="mt-1"
                placeholder="Ada Sloane"
                value={isOwner ? managerForm.full_name : staffForm.full_name}
                onChange={(e) =>
                  isOwner
                    ? setManagerForm((f) => ({ ...f, full_name: e.target.value }))
                    : setStaffForm((f) => ({ ...f, full_name: e.target.value }))
                }
                disabled={isCreating}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Email *</label>
              <Field
                className="mt-1"
                type="email"
                placeholder="ada@whitfieldwms.com"
                value={isOwner ? managerForm.email : staffForm.email}
                onChange={(e) =>
                  isOwner
                    ? setManagerForm((f) => ({ ...f, email: e.target.value }))
                    : setStaffForm((f) => ({ ...f, email: e.target.value }))
                }
                disabled={isCreating}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Password *</label>
              <div className="relative mt-1">
                <Field
                  type={show ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10"
                  disabled={isCreating}
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

            {isOwner && (
              <div>
                <label className="label-xs text-secondary-foreground">Warehouse *</label>
                <Select
                  className="mt-1 w-full"
                  value={managerForm.warehouse_id}
                  onChange={(e) => setManagerForm((f) => ({ ...f, warehouse_id: e.target.value }))}
                  disabled={isCreating || warehouses.length === 0}
                >
                  <option value="">
                    {warehouses.length === 0 ? "No warehouses available" : "Select a warehouse..."}
                  </option>
                  {warehouses.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.code} · {w.name}
                    </option>
                  ))}
                </Select>
              </div>
            )}

            {isManager && (
              <>
                <div>
                  <label className="label-xs text-secondary-foreground">Experience Tier</label>
                  <Select
                    className="mt-1 w-full"
                    value={staffForm.experience_tier}
                    onChange={(e) =>
                      setStaffForm((f) => ({
                        ...f,
                        experience_tier: e.target.value as "ROOKIE" | "EXPERIENCED",
                      }))
                    }
                    disabled={isCreating}
                  >
                    <option value="ROOKIE">Rookie</option>
                    <option value="EXPERIENCED">Experienced</option>
                  </Select>
                </div>
                <div>
                  <label className="label-xs text-secondary-foreground">Function Roles</label>
                  <div className="mt-2 flex flex-wrap gap-3">
                    {functionRoleOptions.map((fr) => (
                      <label key={fr} className="flex items-center gap-2 text-sm">
                        <Checkbox
                          checked={staffForm.function_roles.includes(fr)}
                          onCheckedChange={(checked) =>
                            setStaffForm((f) => ({
                              ...f,
                              function_roles: checked
                                ? [...f.function_roles, fr]
                                : f.function_roles.filter((r) => r !== fr),
                            }))
                          }
                          disabled={isCreating}
                        />
                        {fr}
                      </label>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
          <DialogFooter className="gap-3">
            <Btn variant="secondary" onClick={() => setCreateOpen(false)} disabled={isCreating}>
              Cancel
            </Btn>
            <Btn onClick={onCreateSubmit} disabled={isCreating}>
              {isCreating && <Loader2 className="size-4 animate-spin" />}{" "}
              {isOwner ? "Create Manager" : "Create Staff"}
            </Btn>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="shadow-e3 sm:max-w-[480px]">
          <DialogHeader>
            <DialogTitle>Edit {editTarget?.full_name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="label-xs text-secondary-foreground">Full Name</label>
              <Field
                className="mt-1"
                value={editForm.full_name}
                onChange={(e) => setEditForm((f) => ({ ...f, full_name: e.target.value }))}
                disabled={isEditing}
              />
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Experience Tier</label>
              <Select
                className="mt-1 w-full"
                value={editForm.experience_tier}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, experience_tier: e.target.value as "ROOKIE" | "EXPERIENCED" }))
                }
                disabled={isEditing}
              >
                <option value="ROOKIE">Rookie</option>
                <option value="EXPERIENCED">Experienced</option>
              </Select>
            </div>
            <div>
              <label className="label-xs text-secondary-foreground">Function Roles</label>
              <div className="mt-2 flex flex-wrap gap-3">
                {functionRoleOptions.map((fr) => (
                  <label key={fr} className="flex items-center gap-2 text-sm">
                    <Checkbox
                      checked={editForm.function_roles.includes(fr)}
                      onCheckedChange={(checked) =>
                        setEditForm((f) => ({
                          ...f,
                          function_roles: checked
                            ? [...f.function_roles, fr]
                            : f.function_roles.filter((r) => r !== fr),
                        }))
                      }
                      disabled={isEditing}
                    />
                    {fr}
                  </label>
                ))}
              </div>
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
    </AppShell>
  );
}

function UsersPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER"]}>
      <UsersPageContent />
    </ProtectedRoute>
  );
}
