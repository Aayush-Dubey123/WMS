import { Link, useRouterState } from "@tanstack/react-router";
import {
  Bell,
  Boxes,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LifeBuoy,
  Menu,
  Mic,
  PackageSearch,
  Search,
  Settings,
  ShieldCheck,
  Users,
  Warehouse,
  X,
} from "lucide-react";
import { useState, type ReactNode } from "react";

import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/orders", label: "Orders & Fulfillment", icon: PackageSearch },
  { to: "/tickets", label: "Tickets & Arrivals", icon: ClipboardList },
  { to: "/voice", label: "Voice Pipeline", icon: Mic },
  { to: "/reports", label: "Reports", icon: Boxes },
  { to: "/users", label: "User Management", icon: Users },
  { to: "/warehouses", label: "Warehouses", icon: Warehouse },
] as const;

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center gap-3 border-b border-border px-4">
        <div className="grid size-8 place-items-center rounded-md bg-primary/15 text-primary">
          <ShieldCheck className="size-[18px]" />
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold">Whitfield WMS</p>
          <p className="text-[11px] font-medium text-muted-foreground">Operations console</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-3">
        <p className="label-xs mb-2 px-3 text-muted-foreground uppercase">Workspace</p>
        <ul className="space-y-[2px]">
          {nav.map((item) => {
            const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  onClick={onNavigate}
                  className={cn(
                    "flex h-9 items-center gap-3 rounded-md border-l-4 border-transparent pr-4 pl-2 text-sm transition-colors duration-150",
                    active
                      ? "border-primary bg-surface-hover font-medium text-primary"
                      : "text-sidebar-foreground hover:bg-surface-hover",
                  )}
                >
                  <item.icon className="size-[18px] shrink-0" />
                  <span className="truncate">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-border p-3">
        <ul className="space-y-[2px]">
          {[
            { label: "Settings", icon: Settings },
            { label: "Help & Support", icon: LifeBuoy },
          ].map((i) => (
            <li key={i.label}>
              <button className="flex h-9 w-full items-center gap-3 rounded-md px-3 text-sm text-sidebar-foreground transition-colors duration-150 hover:bg-surface-hover">
                <i.icon className="size-[18px]" />
                {i.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export type Crumb = { label: string; to?: string };

export function AppShell({
  children,
  crumbs = [],
  title,
  actions,
}: {
  children: ReactNode;
  crumbs?: Crumb[];
  title?: string;
  actions?: ReactNode;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <header className="fixed inset-x-0 top-0 z-40 flex h-16 items-center gap-4 border-b border-border bg-card px-4">
        <button
          aria-label="Toggle navigation"
          onClick={() => setOpen((v) => !v)}
          className="grid size-10 place-items-center rounded-md hover:bg-surface-hover lg:hidden"
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>

        <Link to="/" className="flex items-center gap-3 lg:w-[240px]">
          <div className="grid size-8 place-items-center rounded-md bg-primary text-primary-foreground">
            <ShieldCheck className="size-[18px]" />
          </div>
          <span className="hidden text-sm font-semibold sm:block">Whitfield WMS</span>
        </Link>

        <div className="relative mx-auto hidden w-[320px] md:block">
          <Search className="absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            placeholder="Search orders, tickets..."
            className="h-10 w-full rounded-md border border-border bg-input py-[10px] pr-3 pl-9 text-sm text-foreground transition-all duration-150 outline-none placeholder:text-muted-foreground focus:border-primary focus:ring-[3px] focus:ring-primary/10"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <button
            aria-label="Notifications"
            className="relative grid size-10 place-items-center rounded-md hover:bg-surface-hover"
          >
            <Bell className="size-[18px]" />
            <span className="absolute top-2 right-2 size-2 rounded-full bg-primary" />
          </button>
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-md p-1 hover:bg-surface-hover">
              <span className="grid size-8 place-items-center rounded-full bg-primary/20 text-[12px] font-semibold text-primary">
                SW
              </span>
              <span className="hidden text-left text-sm leading-tight sm:block">
                Sam Whitfield
                <span className="block text-[11px] text-muted-foreground">Owner</span>
              </span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 shadow-e3">
              <DropdownMenuLabel className="leading-tight">
                Sam Whitfield
                <span className="block text-[12px] font-normal text-muted-foreground">
                  sam@whitfieldwms.com
                </span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Activity</DropdownMenuItem>
              <DropdownMenuItem>Help</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive focus:text-destructive">
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <aside
        className={cn(
          "fixed top-16 bottom-0 left-0 z-30 w-64 border-r border-border bg-sidebar transition-transform duration-200 lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <SidebarContent onNavigate={() => setOpen(false)} />
      </aside>

      <main className="pt-16 lg:pl-64">
        <div className="page-enter mx-auto max-w-[1440px] px-6 py-6">
          {(crumbs.length > 0 || title) && (
            <div className="mb-6">
              <nav className="flex items-center py-2 text-[12px] text-muted-foreground">
                {crumbs.map((c, i) => (
                  <span key={c.label} className="flex items-center">
                    {i > 0 && <ChevronRight className="mx-1 size-3" />}
                    {c.to ? (
                      <Link to={c.to} className="transition-colors hover:text-primary">
                        {c.label}
                      </Link>
                    ) : (
                      <span className="text-foreground">{c.label}</span>
                    )}
                  </span>
                ))}
              </nav>
              <div className="flex flex-wrap items-center justify-between gap-3">
                {title && <h1>{title}</h1>}
                {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
              </div>
            </div>
          )}
          {children}
        </div>
      </main>
    </div>
  );
}
