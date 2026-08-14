import { createFileRoute } from "@tanstack/react-router";
import { KeyRound, Mail, Shield, User, Warehouse } from "lucide-react";

import { AppShell } from "@/components/wms/app-shell";
import { Panel } from "@/components/wms/ui-bits";
import { ProtectedRoute } from "@/lib/protected-route";
import { useAuth } from "@/lib/auth-context";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [{ title: "Account Settings — Whitfield WMS" }],
  }),
  component: SettingsPageWrapper,
});

function SettingsContent() {
  const { user } = useAuth();

  const rows = [
    { icon: User, label: "Full Name", value: user?.full_name ?? "—" },
    { icon: Mail, label: "Email", value: user?.email ?? "—" },
    { icon: Shield, label: "Role", value: user?.role ?? "—" },
    { icon: Warehouse, label: "Warehouse", value: user?.warehouse_id ?? "All warehouses" },
    {
      icon: KeyRound,
      label: "Experience Tier",
      value: user?.experience_tier ?? "N/A",
    },
  ];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Settings" }]}
      title="Account Settings"
    >
      <div className="max-w-xl space-y-6">
        <Panel>
          <h3 className="mb-4 font-semibold">Profile</h3>
          <dl className="space-y-4">
            {rows.map(({ icon: Icon, label, value }) => (
              <div key={label} className="flex items-center gap-4">
                <Icon className="size-4 shrink-0 text-muted-foreground" />
                <div className="flex flex-1 justify-between text-sm">
                  <dt className="text-muted-foreground">{label}</dt>
                  <dd className="font-medium">{value}</dd>
                </div>
              </div>
            ))}
          </dl>
        </Panel>

        <Panel>
          <h3 className="mb-2 font-semibold">Password Change</h3>
          <p className="text-sm text-muted-foreground">
            Password change is not available via the UI — contact your administrator
            to reset your password.
          </p>
        </Panel>
      </div>
    </AppShell>
  );
}

function SettingsPageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER", "STAFF"]}>
      <SettingsContent />
    </ProtectedRoute>
  );
}
