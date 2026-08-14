import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import {
  Bell,
  Boxes,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  LifeBuoy,
  LogOut,
  Menu,
  MessageCircle,
  Mic,
  PackageSearch,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Users,
  Warehouse,
  X,
} from "lucide-react";
import { useState, type ReactNode, useRef } from "react";

import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Role-based navigation configuration
const ALL_NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/orders", label: "Orders & Fulfillment", icon: PackageSearch, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/tickets", label: "Tickets & Arrivals", icon: ClipboardList, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/voice", label: "Voice Pipeline", icon: Mic, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/chatbot", label: "AI Assistant", icon: Sparkles, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/reports", label: "Reports", icon: Boxes, roles: ["OWNER", "MANAGER"] },
  { to: "/users", label: "User Management", icon: Users, roles: ["OWNER", "MANAGER"] },
  { to: "/warehouses", label: "Warehouses", icon: Warehouse, roles: ["OWNER"] },
] as const;

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { user, hasRole } = useAuth();

  // Filter navigation items based on user role
  const visibleNav = ALL_NAV.filter((item) => {
    if (!user) return false;
    return item.roles.includes(user.role);
  });

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
          {visibleNav.map((item) => {
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
            { label: "Settings", icon: Settings, to: "/settings" },
            { label: "Help & Support", icon: LifeBuoy, to: "/help" },
          ].map((i) => {
            const active = pathname === i.to;
            return (
              <li key={i.label}>
                <Link
                  to={i.to}
                  onClick={onNavigate}
                  className={cn(
                    "flex h-9 w-full items-center gap-3 rounded-md px-3 text-sm transition-colors duration-150",
                    active
                      ? "bg-surface-hover font-medium text-primary"
                      : "text-sidebar-foreground hover:bg-surface-hover",
                  )}
                >
                  <i.icon className="size-[18px]" />
                  {i.label}
                </Link>
              </li>
            );
          })}
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
  const [searchValue, setSearchValue] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { user, logout, isLoading } = useAuth();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchValue.trim()) return;

    const query = searchValue.trim();
    if (query.match(/^[A-Z]{2,}-/)) {
      navigate({ to: "/tickets", search: { q: query } });
    } else {
      navigate({ to: "/orders", search: { q: query } });
    }
    setSearchValue("");
  };

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const userInitials = user ? getInitials(user.full_name) : "U";
  const userName = user?.full_name || "User";
  const userEmail = user?.email || "";
  const userRole = user?.role || "UNKNOWN";

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="fixed inset-x-0 top-0 z-40 flex h-16 items-center gap-3 border-b border-border bg-card px-4 lg:px-6">
        <button
          aria-label="Toggle navigation"
          onClick={() => setOpen((v) => !v)}
          className="grid size-10 shrink-0 place-items-center rounded-md hover:bg-surface-hover lg:hidden"
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>

        <Link to="/" className="flex shrink-0 items-center gap-3 lg:w-60">
          <div className="grid size-8 shrink-0 place-items-center rounded-md bg-primary text-primary-foreground">
            <ShieldCheck className="size-[18px]" />
          </div>
          <span className="hidden text-sm font-semibold sm:block">Whitfield WMS</span>
        </Link>

        <div className="hidden flex-1 justify-center px-2 md:flex">
          <form onSubmit={handleSearch} className="relative w-full max-w-2xl">
            <Search className="absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Search orders, tickets... (e.g. ORD-123 or RNO-001)"
              className="h-10 w-full rounded-lg border border-border bg-surface-hover text-sm text-foreground transition-all duration-150 outline-none placeholder:text-muted-foreground py-2 pl-10 pr-3 hover:bg-input focus:border-primary focus:ring-[2px] focus:ring-primary/20 focus:bg-background"
            />
          </form>
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-2">
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
                {userInitials}
              </span>
              {!isLoading && (
                <span className="hidden text-left text-sm leading-tight sm:block">
                  {userName}
                  <span className="block text-[11px] text-muted-foreground capitalize">
                    {userRole.toLowerCase()}
                  </span>
                </span>
              )}
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 shadow-e3">
              <DropdownMenuLabel className="leading-tight">
                {userName}
                <span className="block text-[12px] font-normal text-muted-foreground">
                  {userEmail}
                </span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate({ to: "/settings" })}>
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate({ to: "/reports" })}>
                Activity
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate({ to: "/help" })}>
                Help
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-destructive focus:text-destructive"
              >
                <LogOut className="mr-2 size-4" />
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
