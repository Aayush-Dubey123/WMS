import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import {
  Bell,
  Boxes,
  ChevronRight,
  ChevronDown,
  ClipboardList,
  LayoutDashboard,
  LifeBuoy,
  LogOut,
  Menu,
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
import { useState, type ReactNode, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { warehousesAPI, approvalsAPI, ordersAPI } from "@/lib/api";
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
  { to: "/voice", label: "Voice Assistance", icon: Mic, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/chatbot", label: "AI Assistant", icon: Sparkles, roles: ["OWNER", "MANAGER", "STAFF"] },
  { to: "/reports", label: "Reports", icon: Boxes, roles: ["OWNER", "MANAGER"] },
  { to: "/users", label: "User Management", icon: Users, roles: ["OWNER", "MANAGER"] },
  { to: "/warehouses", label: "Warehouses", icon: Warehouse, roles: ["OWNER"] },
] as const;

function SidebarContent({
  onNavigate,
  isCollapsed,
  setIsCollapsed,
}: {
  onNavigate?: () => void;
  isCollapsed: boolean;
  setIsCollapsed: (v: boolean) => void;
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const { user } = useAuth();

  // Filter navigation items based on user role
  const visibleNav = ALL_NAV.filter((item) => {
    if (!user) return false;
    return (item.roles as readonly string[]).includes(user.role);
  });

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Sidebar header: Logo + Console details */}
      <div
        className={cn(
          "flex h-16 items-center gap-3 border-b border-[var(--wf-border)] px-4",
          isCollapsed && "justify-center px-0"
        )}
      >
        <div className="grid size-8 shrink-0 place-items-center rounded-md bg-[var(--wf-orange-pale)] text-[var(--wf-orange)]">
          <ShieldCheck className="size-5" />
        </div>
        {!isCollapsed && (
          <div className="leading-tight">
            <p className="text-sm font-bold text-[var(--wf-dark)]">Whitfield WMS</p>
            <p className="text-[10px] font-medium text-muted-foreground">Operations console</p>
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto p-3">
        {!isCollapsed && (
          <p className="text-[10px] font-bold tracking-wider mb-2 px-3 text-[#7A7A6E] uppercase">
            Workspace
          </p>
        )}
        <ul className="space-y-[4px]">
          {visibleNav.map((item) => {
            const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  onClick={onNavigate}
                  className={cn(
                    "flex h-10 items-center rounded-lg border-l-4 pr-3 pl-2 text-sm transition-colors duration-150 relative group",
                    active
                      ? "border-[var(--wf-orange)] bg-[var(--wf-orange-pale)] font-semibold text-[var(--wf-orange)]"
                      : "border-transparent text-[var(--wf-dark-secondary)] hover:bg-[#FAF6F0] hover:text-[var(--wf-dark)]",
                    isCollapsed && "justify-center pr-2 pl-2 border-l-0"
                  )}
                >
                  <item.icon className="size-[18px] shrink-0" />
                  {!isCollapsed && <span className="ml-3 truncate">{item.label}</span>}
                  {isCollapsed && (
                    <div className="absolute left-16 bg-[var(--wf-dark)] text-white text-[11px] px-2 py-1 rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-150 whitespace-nowrap z-50 shadow-md">
                      {item.label}
                    </div>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom Actions */}
      <div className="border-t border-[var(--wf-border)] p-3">
        <ul className="space-y-[4px]">
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
                    "flex h-10 w-full items-center rounded-lg px-3 text-sm transition-colors duration-150 relative group",
                    active
                      ? "bg-[var(--wf-orange-pale)] font-semibold text-[var(--wf-orange)]"
                      : "text-[var(--wf-dark-secondary)] hover:bg-[#FAF6F0] hover:text-[var(--wf-dark)]",
                    isCollapsed && "justify-center px-0"
                  )}
                >
                  <i.icon className="size-[18px] shrink-0" />
                  {!isCollapsed && <span className="ml-3">{i.label}</span>}
                  {isCollapsed && (
                    <div className="absolute left-16 bg-[var(--wf-dark)] text-white text-[11px] px-2 py-1 rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-150 whitespace-nowrap z-50 shadow-md">
                      {i.label}
                    </div>
                  )}
                </Link>
              </li>
            );
          })}
          {/* Collapse Toggle */}
          <li>
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className={cn(
                "flex h-10 w-full items-center rounded-lg px-3 text-sm text-[var(--wf-dark-secondary)] hover:bg-[#FAF6F0] hover:text-[var(--wf-dark)] transition-colors duration-150",
                isCollapsed && "justify-center px-0"
              )}
            >
              {isCollapsed ? (
                <ChevronRight className="size-[18px] text-[var(--wf-orange)]" />
              ) : (
                <span className="flex items-center text-[#7A7A6E] font-semibold text-xs gap-1.5">
                  <span className="text-sm">&laquo;</span> Collapse
                </span>
              )}
            </button>
          </li>
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
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { user, logout, isLoading } = useAuth();

  // Fetch warehouse selector options from warehousesAPI
  const { data: whResponse } = useQuery({
    queryKey: ["warehouses"],
    queryFn: () => warehousesAPI.getAll(0, 100),
    staleTime: 30000,
  });
  const whList = (whResponse as any)?.warehouses || [];

  // Fetch approvals for OWNER/MANAGER notification count
  const { data: approvals } = useQuery({
    queryKey: ["approvals"],
    queryFn: () => approvalsAPI.listPending(0, 10),
    enabled: !!user && (user.role === "OWNER" || user.role === "MANAGER"),
    staleTime: 30000,
  });

  // Fetch orders for STAFF pending count
  const { data: orders } = useQuery({
    queryKey: ["orders"],
    queryFn: () => ordersAPI.getAll(0, 50),
    enabled: !!user && user.role === "STAFF",
    staleTime: 30000,
  });

  let pendingCount = 0;
  if (user?.role === "OWNER" || user?.role === "MANAGER") {
    pendingCount = (approvals as any)?.pending_tickets?.length || 0;
  } else if (user?.role === "STAFF") {
    pendingCount = ((orders as any)?.orders || []).filter((o: any) => o.status === "PENDING").length;
  }

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

  // Focus search input when user presses Ctrl /
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const [scrollPercent, setScrollPercent] = useState(0);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight <= 0) {
        setScrollPercent(0);
        return;
      }
      const pct = Math.min(1, Math.max(0, scrollTop / docHeight));
      setScrollPercent(pct);
    };

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mediaQuery.matches);
    const listener = (e: MediaQueryListEvent) => setReducedMotion(e.matches);

    window.addEventListener("scroll", handleScroll, { passive: true });
    mediaQuery.addEventListener("change", listener);
    handleScroll();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      mediaQuery.removeEventListener("change", listener);
    };
  }, []);

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

  const [selectedWH, setSelectedWH] = useState(() => {
    return localStorage.getItem("selected_warehouse_id") || "ALL";
  });

  useEffect(() => {
    const handleWHChange = () => {
      setSelectedWH(localStorage.getItem("selected_warehouse_id") || "ALL");
    };
    window.addEventListener("warehouseChanged", handleWHChange);
    return () => window.removeEventListener("warehouseChanged", handleWHChange);
  }, []);

  return (
    <div className="min-h-screen bg-[#FAF6F0]">
      {/* ─── HEADER ─── */}
      <header className="fixed inset-x-0 top-0 z-40 grid grid-cols-3 h-16 items-center border-b border-[var(--wf-border)] bg-white px-4 lg:px-6">
        {/* Left Column: Mobile Menu & Logo */}
        <div className="flex items-center gap-3 flex-1 overflow-visible">
          <button
            aria-label="Toggle navigation"
            onClick={() => setOpen((v) => !v)}
            className="grid size-10 shrink-0 place-items-center rounded-md hover:bg-[#FAF6F0] lg:hidden text-[#4A4A4A]"
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>

          {/* Orange W Logo */}
          <Link to="/" className="flex shrink-0 items-center">
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                background: "var(--wf-orange)",
                display: "grid",
                placeItems: "center",
                color: "#fff",
                fontFamily: "'Outfit', sans-serif",
                fontWeight: 800,
                fontSize: 16,
              }}
            >
              W
            </div>
          </Link>

          {/* Branded logistics micro-animation */}
          <div className="hidden lg:flex items-center flex-1 ml-5 mr-3 relative h-10 overflow-visible select-none pointer-events-none">
            {/* Premium Warehouse Icon with loading shutters */}
            <div className="shrink-0 flex items-end mr-1">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-gray-400 shrink-0">
                <path d="M3 10 L12 4 L21 10 L21 20 L3 20 Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M7 20 V13 H17 V20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="9" y1="15" x2="15" y2="15" stroke="currentColor" strokeWidth="1" />
                <line x1="9" y1="17" x2="15" y2="17" stroke="currentColor" strokeWidth="1" />
              </svg>
            </div>

            {/* The Path Container */}
            <div className="relative flex-1 h-10 overflow-visible mx-2">
              {/* Background dashed path */}
              <div className="absolute left-0 right-0 bottom-[19px] h-0.5 border-b border-dashed border-[var(--wf-orange)]/25" />

              {/* Foreground filled path */}
              <div
                style={{
                  width: `${scrollPercent * 92}%`,
                }}
                className="absolute left-0 bottom-[19px] h-0.5 border-b border-solid border-[var(--wf-orange)]"
              />

              {/* Animated Premium Whitfield Orange & Cream Truck */}
              <div
                style={{
                  position: "absolute",
                  bottom: 11,
                  left: `${reducedMotion ? 0 : scrollPercent * 92}%`,
                  transition: "left 150ms cubic-bezier(0.1, 0.8, 0.3, 1)",
                }}
                className="shrink-0 flex items-center"
              >
                <svg width="28" height="18" viewBox="0 0 28 18" fill="none" xmlns="http://www.w3.org/2000/svg" className="shrink-0">
                  {/* Orange cargo bed container */}
                  <rect x="1" y="2" width="16" height="11" fill="#D4740B" rx="1.5" />
                  {/* Visual horizontal highlights */}
                  <line x1="4" y1="5" x2="14" y2="5" stroke="#FAF6F0" strokeWidth="1" strokeOpacity="0.4" />
                  <line x1="4" y1="8" x2="14" y2="8" stroke="#FAF6F0" strokeWidth="1" strokeOpacity="0.4" />
                  {/* Cream colored cab */}
                  <path d="M17 5 H21 L25 9 V13 H17 Z" fill="#FAF6F0" stroke="#B8B5AB" strokeWidth="1" />
                  {/* wind shield screen */}
                  <path d="M20.5 6 H22.5 L24 9 H20.5 Z" fill="#26314A" opacity="0.8" />
                  {/* Wheels with detailed tires & hubs */}
                  <circle cx="6" cy="14" r="2.5" fill="#374151" stroke="#9CA3AF" strokeWidth="0.5" />
                  <circle cx="19" cy="14" r="2.5" fill="#374151" stroke="#9CA3AF" strokeWidth="0.5" />
                </svg>
              </div>
            </div>

            {/* Destination Marker */}
            <div className="shrink-0 ml-1 flex items-center">
              {scrollPercent >= 0.95 ? (
                <div className="text-green-600 animate-in fade-in zoom-in-50 duration-200">
                  <svg width="18" height="18" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="8" cy="8" r="7" fill="var(--wf-orange-pale)" stroke="var(--wf-orange)" strokeWidth="1.2" />
                    <path d="M5 8 L7 10 L11 6" stroke="var(--wf-orange)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
              ) : (
                <div className="text-[var(--wf-orange)] opacity-80">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
                    <circle cx="12" cy="10" r="3" fill="#fff" />
                  </svg>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Middle Column: Globally Centered Search */}
        <div className="hidden md:flex justify-center w-full">
          <form onSubmit={handleSearch} className="relative w-full max-w-lg">
            <Search className="absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Search orders, tickets... (e.g. ORD-123 or RNO-001)"
              style={{
                fontFamily: "'Inter', sans-serif",
                border: "1px solid var(--wf-border)",
                background: "#FAF6F0",
              }}
              className="h-10 w-full rounded-lg text-sm text-foreground transition-all duration-150 outline-none placeholder:text-[#7A7A6E] py-2 pl-10 pr-16 hover:bg-[#F0E9DD] focus:border-[var(--wf-orange)] focus:ring-2 focus:ring-[var(--wf-orange)]/20 focus:bg-white"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-semibold text-muted-foreground bg-[#FAF6F0] border border-[var(--wf-border)] px-1.5 py-0.5 rounded pointer-events-none">
              Ctrl /
            </div>
          </form>
        </div>

        {/* Right Column: Actions (Notifications, Selector, Profile) */}
        <div className="flex items-center gap-3 justify-end">
          {/* Notifications */}
          <button
            aria-label="Notifications"
            className="relative grid size-10 place-items-center rounded-md hover:bg-[#FAF6F0]"
          >
            <Bell className="size-[18px] text-[#4A4A4A]" />
            {pendingCount > 0 && (
              <span className="absolute top-2 right-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-[var(--wf-orange)] px-1 text-[9px] font-bold text-white leading-none">
                {pendingCount}
              </span>
            )}
          </button>

          {/* Warehouse Selector (Populated from warehousesAPI) */}
          <div className="relative hidden sm:block">
            <Warehouse className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            <select
              style={{
                border: "1px solid var(--wf-border)",
                fontFamily: "'Inter', sans-serif",
              }}
              className="h-10 rounded-lg pl-9 pr-8 bg-white text-xs font-semibold text-[#4A4A4A] appearance-none outline-none cursor-pointer hover:bg-[#FAF6F0]"
              value={selectedWH}
              onChange={(e) => {
                const val = e.target.value;
                setSelectedWH(val);
                localStorage.setItem("selected_warehouse_id", val);
                window.dispatchEvent(new Event("warehouseChanged"));
              }}
            >
              <option value="ALL">All Warehouses</option>
              {whList.map((wh: any) => (
                <option key={wh.id} value={wh.id}>
                  {wh.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          </div>

          {/* User Profile dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-md p-1 hover:bg-[#FAF6F0] outline-none">
              <span
                style={{
                  background: "var(--wf-orange-pale)",
                  color: "var(--wf-orange)",
                  fontFamily: "'Outfit', sans-serif",
                }}
                className="grid size-8 place-items-center rounded-full text-xs font-bold"
              >
                {userInitials}
              </span>
              {!isLoading && (
                <span className="hidden text-left text-xs leading-tight sm:block font-semibold text-[#4A4A4A]">
                  {userName}
                  <span className="block text-[10px] text-muted-foreground font-normal capitalize">
                    {userRole.toLowerCase()}
                  </span>
                </span>
              )}
              <ChevronDown className="size-3 text-muted-foreground ml-0.5 hidden sm:block" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 shadow-md border-[var(--wf-border)] bg-white">
              <DropdownMenuLabel className="leading-tight font-semibold">
                {userName}
                <span className="block text-[11px] font-normal text-muted-foreground">
                  {userEmail}
                </span>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-[var(--wf-border)]" />
              <DropdownMenuItem className="cursor-pointer" onClick={() => navigate({ to: "/settings" })}>
                Settings
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer" onClick={() => navigate({ to: "/reports" })}>
                Activity
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer" onClick={() => navigate({ to: "/help" })}>
                Help
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-[var(--wf-border)]" />
              <DropdownMenuItem
                onClick={handleLogout}
                className="text-destructive focus:text-destructive cursor-pointer"
              >
                <LogOut className="mr-2 size-4" />
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* ─── SIDEBAR ─── */}
      <aside
        style={{
          transitionProperty: "width, transform",
        }}
        className={cn(
          "fixed top-16 bottom-0 left-0 z-30 border-r border-[var(--wf-border)] bg-white transition-all duration-200 lg:translate-x-0",
          isCollapsed ? "w-20" : "w-64",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <SidebarContent
          onNavigate={() => setOpen(false)}
          isCollapsed={isCollapsed}
          setIsCollapsed={setIsCollapsed}
        />
      </aside>

      {/* ─── MAIN CONTENT ─── */}
      <main
        style={{
          transitionProperty: "padding-left",
        }}
        className={cn(
          "pt-16 transition-all duration-200 min-h-screen",
          isCollapsed ? "lg:pl-20" : "lg:pl-64"
        )}
      >
        <div className="page-enter mx-auto max-w-[1440px] px-6 py-6">
          {(crumbs.length > 0 || title) && (
            <div className="mb-6">
              <nav className="flex items-center py-1 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                {crumbs.map((c, i) => (
                  <span key={c.label} className="flex items-center">
                    {i > 0 && <ChevronRight className="mx-1.5 size-3" />}
                    {c.to ? (
                      <Link to={c.to} className="transition-colors hover:text-[var(--wf-orange)]">
                        {c.label}
                      </Link>
                    ) : (
                      <span className="text-[#7A7A6E]">{c.label}</span>
                    )}
                  </span>
                ))}
              </nav>
              <div className="flex flex-wrap items-center justify-between gap-3 mt-1">
                {title && (
                  <h1 className="text-2xl font-outfit font-extrabold text-[var(--wf-dark)] tracking-tight">
                    {title}
                  </h1>
                )}
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
