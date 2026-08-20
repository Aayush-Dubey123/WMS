import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
  Loader2,
  CheckCircle2,
  ArrowRight,
  Eye,
  EyeOff,
  Mail,
  Lock,
  Cpu,
  Radio,
  ShieldCheck,
  Package,
  Boxes,
  ClipboardList,
  Truck,
  BarChart3,
  Sparkles,
  Users,
  TrendingUp,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export const Route = createFileRoute("/landing")({
  head: () => ({
    meta: [
      { title: "Whitfield WMS — Intelligent Warehouse Management" },
      {
        name: "description",
        content:
          "Smarter warehouses. Stronger supply chains. Real-time visibility, better decisions, exceptional fulfillment.",
      },
    ],
  }),
  component: LandingPage,
});

/* ─── Auth schemas & demo credentials ─── */
const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});
type LoginFormValues = z.infer<typeof loginSchema>;

const DEMO_CREDENTIALS = [
  {
    role: "OWNER",
    email: "owner@whitfield.com",
    password: "OwnerPass123!",
    description: "Full visibility & control",
  },
  {
    role: "MANAGER",
    email: "manager@whitfield.com",
    password: "ManagerPass123!",
    description: "Manage operations & teams",
  },
  {
    role: "STAFF",
    email: "staff@whitfield.com",
    password: "StaffPass123!",
    description: "Complete daily tasks",
  },
];

/* ─── Feature story sections ─── */
const STORY_SECTIONS = [
  {
    icon: Boxes,
    label: "WAREHOUSE OPERATIONS",
    title: "Complete visibility across every warehouse",
    description:
      "Monitor all your facilities in real-time. Track utilization, manage zones, racks, and bins with a centralized dashboard that gives you instant operational awareness.",
    features: [
      "Multi-warehouse management",
      "Zone & bin tracking",
      "Real-time utilization metrics",
      "Role-based access controls",
    ],
  },
  {
    icon: Package,
    label: "INVENTORY MANAGEMENT",
    title: "Know exactly what you have and where",
    description:
      "Maintain accurate stock counts across all locations. Our system tracks every item from receiving to shipping, with barcode scanning and automated stock adjustments.",
    features: [
      "SKU-level tracking",
      "Barcode scanning",
      "Stock reservation system",
      "Damage detection & reporting",
    ],
  },
  {
    icon: ClipboardList,
    label: "RECEIVING & ARRIVALS",
    title: "Streamlined receiving with smart ticket workflows",
    description:
      "Every arrival gets a ticket. Inspect, log dimensions, assign storage — all with a guided workflow that catches discrepancies before items hit the floor.",
    features: [
      "Ticket-based receiving",
      "Multi-item inspection",
      "Storage assignment",
      "Manager approval queues",
    ],
  },
  {
    icon: Truck,
    label: "PICKING, PACKING & SHIPPING",
    title: "From order to doorstep, handled with precision",
    description:
      "Fulfill orders with guided pick, pack, and ship workflows. Automated label generation, weight validation, and real-time status updates keep everything moving.",
    features: [
      "Guided picking queues",
      "Pack & weigh verification",
      "Automated label generation",
      "Real-time shipment tracking",
    ],
  },
  {
    icon: BarChart3,
    label: "ANALYTICS & REPORTING",
    title: "Data-driven decisions for smarter operations",
    description:
      "Access daily summaries, trend analysis, and operational KPIs. Understand arrival patterns, fulfillment velocity, and warehouse performance at a glance.",
    features: [
      "Daily operational summaries",
      "Order fulfillment analytics",
      "Arrival trend reports",
      "Complete audit trail",
    ],
  },
  {
    icon: Sparkles,
    label: "AI-POWERED CAPABILITIES",
    title: "Voice, vision, and natural language at your command",
    description:
      "Dictate item details hands-free with our voice pipeline. Measure dimensions with camera vision. Ask questions in plain English and get instant answers from your data.",
    features: [
      "Voice-to-data pipeline",
      "Vision-based measurement",
      "Natural language queries",
      "AI-assisted workflows",
    ],
  },
];

/* ─── Product preview mockup data ─── */
const PREVIEW_SCREENS = [
  {
    title: "Executive Dashboard",
    description: "Real-time KPIs, order status, and arrival tracking at a glance",
    metrics: [
      { label: "Orders Today", value: "1,284", trend: "+18.4%" },
      { label: "Items Sold", value: "3,921", trend: "+12.1%" },
      { label: "Pending", value: "42", trend: "-8.2%" },
      { label: "Shipped", value: "88", trend: "+24.6%" },
    ],
  },
  {
    title: "Order Management",
    description: "Full lifecycle from creation to delivery with guided workflows",
    metrics: [
      { label: "Active Orders", value: "156", trend: "+5.3%" },
      { label: "Ready to Ship", value: "34", trend: "+11.7%" },
      { label: "Avg Fulfillment", value: "2.4h", trend: "-15.2%" },
      { label: "Success Rate", value: "99.1%", trend: "+0.3%" },
    ],
  },
  {
    title: "Receiving & Tickets",
    description: "Smart ticket workflows with inspection, storage assignment, and approvals",
    metrics: [
      { label: "Today's Arrivals", value: "67", trend: "+22.1%" },
      { label: "Inspected", value: "54", trend: "+18.5%" },
      { label: "Awaiting Approval", value: "8", trend: "-33.0%" },
      { label: "Storage Assigned", value: "46", trend: "+15.7%" },
    ],
  },
  {
    title: "AI Voice Assistance",
    description: "Hands-free item logging with speech-to-data conversion",
    metrics: [
      { label: "Transcriptions", value: "234", trend: "+40.2%" },
      { label: "Accuracy", value: "97.8%", trend: "+1.2%" },
      { label: "Time Saved", value: "14h", trend: "+25.0%" },
      { label: "Items Logged", value: "892", trend: "+35.4%" },
    ],
  },
];

/* ─── Main Component ─── */
function LandingPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading, login: authLogin } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState<number | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState<"signin" | "demo">("signin");

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const offset = 80; // height of sticky header + padding
      const bodyRect = document.body.getBoundingClientRect().top;
      const elementRect = el.getBoundingClientRect().top;
      const elementPosition = elementRect - bodyRect;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      navigate({ to: "/" });
    }
  }, [isAuthenticated, authLoading, navigate]);

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    try {
      await authLogin(data.email, data.password);
      toast.success("Signed in successfully!", {
        icon: <CheckCircle2 className="size-4" />,
      });
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Login failed. Please try again.";
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (index: number) => {
    setSelectedDemo(index);
    setIsLoading(true);
    const cred = DEMO_CREDENTIALS[index]!;
    try {
      await authLogin(cred.email, cred.password);
      toast.success(`Welcome, ${cred.role}!`, {
        icon: <CheckCircle2 className="size-4" />,
      });
    } catch (error) {
      const msg =
        error instanceof Error ? error.message : `Login failed for ${cred.role}.`;
      toast.error(msg);
      setSelectedDemo(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ background: "var(--wf-cream)", minHeight: "100vh" }}>
      {/* ─── TOP NAV ─── */}
      <nav
        style={{
          position: "sticky",
          top: 0,
          zIndex: 50,
          background: "rgba(250, 246, 240, 0.92)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid var(--wf-border)",
        }}
      >
        <div
          style={{
            maxWidth: 1400,
            margin: "0 auto",
            padding: "0 24px",
            height: 68,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                width: 38,
                height: 38,
                borderRadius: 10,
                background: "var(--wf-orange)",
                display: "grid",
                placeItems: "center",
                color: "#fff",
                fontFamily: "'Outfit', sans-serif",
                fontWeight: 800,
                fontSize: 18,
              }}
            >
              W
            </div>
            <span
              style={{
                fontFamily: "'Outfit', sans-serif",
                fontWeight: 700,
                fontSize: 22,
                color: "var(--wf-dark)",
                letterSpacing: "-0.02em",
              }}
            >
              WHITFIELD{" "}
              <span style={{ fontWeight: 400, color: "var(--wf-muted)" }}>WMS</span>
            </span>
          </div>

          {/* Nav Items */}
          <div
            style={{ display: "flex", alignItems: "center", gap: 24 }}
            className="wf-nav-links"
          >
            {[
              { label: "Platform", id: "platform" },
              { label: "How it works", id: "how-it-works" },
              { label: "Network", id: "network" },
              { label: "Resources", id: "resources" },
              { label: "About Us", id: "about-us" },
            ].map((item) => (
              <a
                key={item.label}
                href={`#${item.id}`}
                onClick={(e) => {
                  e.preventDefault();
                  scrollToSection(item.id);
                }}
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 14,
                  fontWeight: 600,
                  color: "var(--wf-dark-secondary)",
                  textDecoration: "none",
                  transition: "color 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "var(--wf-orange)")}
                onMouseLeave={(e) =>
                  (e.currentTarget.style.color = "var(--wf-dark-secondary)")
                }
              >
                {item.label}
              </a>
            ))}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 14px",
                borderRadius: 20,
                background: "var(--wf-green-light)",
                fontSize: 12,
                fontWeight: 600,
                color: "var(--wf-green)",
              }}
              className="wf-live-badge"
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: "var(--wf-green)",
                  display: "inline-block",
                }}
              />
              LIVE SYSTEM
            </div>
          </div>
        </div>
      </nav>

      {/* ─── HERO CONTAINER ─── */}
      <section
        style={{
          maxWidth: 1400,
          margin: "0 auto",
          padding: "48px 24px 0",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 0.8fr",
            gap: 40,
            alignItems: "start",
          }}
          className="wf-hero-split"
        >
          {/* LEFT AREA: Headline, Illustration, Features */}
          <div style={{ display: "flex", flexDirection: "column", gap: 36 }}>
            
            {/* Split layout inside Left column: Headline on the left, warehouse on the right */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1.3fr",
                gap: 24,
                alignItems: "center",
              }}
              className="wf-inner-left"
            >
              {/* Headline Block */}
              <div>
                <p
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: "0.12em",
                    color: "var(--wf-orange)",
                    marginBottom: 12,
                    textTransform: "uppercase",
                  }}
                >
                  INTELLIGENT OPERATIONS
                </p>

                <h1
                  style={{
                    fontFamily: "'Outfit', sans-serif",
                    fontSize: "clamp(30px, 3.5vw, 42px)",
                    fontWeight: 900,
                    lineHeight: 1.15,
                    color: "var(--wf-dark)",
                    marginBottom: 16,
                    letterSpacing: "-0.03em",
                  }}
                >
                  Smarter
                  <br />
                  warehouses.
                  <br />
                  <span style={{ color: "var(--wf-orange)" }}>Stronger supply</span>
                  <br />
                  <span style={{ color: "var(--wf-orange)" }}>chains.</span>
                </h1>

                <p
                  style={{
                    fontSize: 14,
                    lineHeight: 1.6,
                    color: "var(--wf-muted)",
                    marginBottom: 20,
                  }}
                >
                  Real-time visibility. Better decisions. Exceptional fulfillment.
                </p>

                <button
                  onClick={() => {
                    const el = document.getElementById("how-it-works");
                    if (el) {
                      const offset = 80; // height of sticky header + padding
                      const bodyRect = document.body.getBoundingClientRect().top;
                      const elementRect = el.getBoundingClientRect().top;
                      const elementPosition = elementRect - bodyRect;
                      const offsetPosition = elementPosition - offset;

                      window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth"
                      });
                    }
                  }}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    background: "none",
                    border: "none",
                    color: "var(--wf-orange)",
                    fontSize: 14,
                    fontWeight: 700,
                    cursor: "pointer",
                    padding: 0,
                    fontFamily: "'Inter', sans-serif",
                  }}
                >
                  See how it works <ArrowRight size={14} />
                </button>
              </div>

              {/* Warehouse Illustration Block with Concentric Circles & Floating Cards */}
              <div
                style={{
                  position: "relative",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  padding: "40px 0",
                }}
              >
                {/* ── Concentric Styling Circles ── */}
                <div
                  style={{
                    position: "absolute",
                    width: 280,
                    height: 280,
                    border: "1px dashed rgba(212, 116, 11, 0.12)",
                    borderRadius: "50%",
                    pointerEvents: "none",
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    width: 380,
                    height: 380,
                    border: "1px solid rgba(212, 116, 11, 0.08)",
                    borderRadius: "50%",
                    pointerEvents: "none",
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    width: 480,
                    height: 480,
                    border: "1px solid rgba(212, 116, 11, 0.04)",
                    borderRadius: "50%",
                    pointerEvents: "none",
                  }}
                />
                {/* Small styled orange dots on circles */}
                <div
                  style={{
                    position: "absolute",
                    width: 6,
                    height: 6,
                    background: "rgba(212, 116, 11, 0.4)",
                    borderRadius: "50%",
                    top: "30%",
                    left: "15%",
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    width: 6,
                    height: 6,
                    background: "rgba(212, 116, 11, 0.4)",
                    borderRadius: "50%",
                    bottom: "25%",
                    right: "12%",
                  }}
                />

                {/* Warehouse Image */}
                <div style={{ position: "relative", width: "100%", maxWidth: 360, zIndex: 5 }}>
                  <img
                    src="/warehouse-hero.jpg"
                    alt="Whitfield warehouse operations"
                    style={{
                      width: "100%",
                      height: "auto",
                      display: "block",
                    }}
                  />
                </div>

                {/* Floating Metric: Orders Today */}
                <div
                  style={{
                    position: "absolute",
                    top: -15,
                    right: -10,
                    background: "var(--wf-card)",
                    borderRadius: 12,
                    padding: "10px 14px",
                    boxShadow: "var(--wf-shadow-float)",
                    zIndex: 10,
                    minWidth: 100,
                  }}
                >
                  <p
                    style={{
                      fontSize: 8,
                      fontWeight: 800,
                      color: "var(--wf-muted)",
                      marginBottom: 2,
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}
                  >
                    ORDERS TODAY
                  </p>
                  <p
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: "var(--wf-dark)",
                      fontFamily: "'Outfit', sans-serif",
                      lineHeight: 1,
                    }}
                  >
                    1,284
                  </p>
                  <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 2 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: "var(--wf-green)" }}>
                      ↑ 18.4%
                    </span>
                    <svg viewBox="0 0 40 10" style={{ width: 30, height: 8 }}>
                      <path
                        d="M0,8 Q10,6 20,5 T40,2"
                        fill="none"
                        stroke="var(--wf-orange)"
                        strokeWidth="1.5"
                      />
                    </svg>
                  </div>
                </div>

                {/* Floating Metric: Inventory Health */}
                <div
                  style={{
                    position: "absolute",
                    bottom: 30,
                    left: -35,
                    background: "var(--wf-card)",
                    borderRadius: 12,
                    padding: "10px 14px",
                    boxShadow: "var(--wf-shadow-float)",
                    zIndex: 10,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <div>
                    <p
                      style={{
                        fontSize: 8,
                        fontWeight: 800,
                        color: "var(--wf-muted)",
                        marginBottom: 2,
                        textTransform: "uppercase",
                      }}
                    >
                      INVENTORY HEALTH
                    </p>
                    <p
                      style={{
                        fontSize: 18,
                        fontWeight: 800,
                        color: "var(--wf-dark)",
                        fontFamily: "'Outfit', sans-serif",
                        lineHeight: 1,
                      }}
                    >
                      94.8%
                    </p>
                    <p style={{ fontSize: 10, color: "var(--wf-green)", fontWeight: 700, marginTop: 1 }}>
                      Healthy
                    </p>
                  </div>
                  {/* Gauge */}
                  <div style={{ position: "relative", width: 30, height: 30 }}>
                    <svg viewBox="0 0 30 30" style={{ width: 30, height: 30 }}>
                      <circle cx="15" cy="15" r="12" fill="none" stroke="var(--wf-cream-dark)" strokeWidth="3" />
                      <circle
                        cx="15"
                        cy="15"
                        r="12"
                        fill="none"
                        stroke="var(--wf-green)"
                        strokeWidth="3"
                        strokeDasharray={`${0.948 * 75.4} 75.4`}
                        transform="rotate(-90 15 15)"
                      />
                    </svg>
                    <span
                      style={{
                        position: "absolute",
                        inset: 0,
                        display: "grid",
                        placeItems: "center",
                        fontSize: 8,
                        fontWeight: 800,
                        color: "var(--wf-dark)",
                      }}
                    >
                      95
                    </span>
                  </div>
                </div>

                {/* Floating Metric: On Time Shipments */}
                <div
                  style={{
                    position: "absolute",
                    bottom: -15,
                    right: 10,
                    background: "var(--wf-card)",
                    borderRadius: 12,
                    padding: "10px 14px",
                    boxShadow: "var(--wf-shadow-float)",
                    zIndex: 10,
                  }}
                >
                  <p
                    style={{
                      fontSize: 8,
                      fontWeight: 800,
                      color: "var(--wf-muted)",
                      marginBottom: 2,
                      textTransform: "uppercase",
                    }}
                  >
                    ON TIME SHIPMENTS
                  </p>
                  <p
                    style={{
                      fontSize: 18,
                      fontWeight: 800,
                      color: "var(--wf-dark)",
                      fontFamily: "'Outfit', sans-serif",
                      lineHeight: 1,
                    }}
                  >
                    98.2%
                  </p>
                  <p style={{ fontSize: 10, color: "var(--wf-muted)", marginTop: 1 }}>
                    This week
                  </p>
                </div>
              </div>
            </div>

            {/* Badges / Features list row */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: 20,
                borderTop: "1px solid var(--wf-border)",
                paddingTop: 24,
              }}
              className="wf-feature-badges"
            >
              {[
                { icon: Cpu, label: "AI Powered", sub: "Smart recommendations" },
                { icon: Radio, label: "Real-time", sub: "Live operational data" },
                { icon: ShieldCheck, label: "Secure", sub: "Enterprise grade security" },
              ].map((b) => (
                <div
                  key={b.label}
                  style={{ display: "flex", alignItems: "center", gap: 12 }}
                >
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 12,
                      background: "var(--wf-orange-pale)",
                      display: "grid",
                      placeItems: "center",
                      flexShrink: 0,
                    }}
                  >
                    <b.icon size={20} color="var(--wf-orange)" />
                  </div>
                  <div>
                    <p
                      style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: "var(--wf-dark)",
                        marginBottom: 2,
                      }}
                    >
                      {b.label}
                    </p>
                    <p style={{ fontSize: 11, color: "var(--wf-muted)", lineHeight: 1.3 }}>
                      {b.sub}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Security certifications footer */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                fontSize: 12,
                color: "var(--wf-muted)",
                borderTop: "1px solid var(--wf-border)",
                paddingTop: 16,
              }}
              className="wf-security-specs"
            >
              <ShieldCheck size={14} color="var(--wf-green)" />
              <span>Enterprise Grade Security</span>
              <span>•</span>
              <span>SOC 2 Compliant</span>
              <span>•</span>
              <span>256-bit Encryption</span>
            </div>
          </div>

          {/* RIGHT AREA: Sign In + OWNER/MANAGER/STAFF demo card */}
          <div
            id="signin-card"
            style={{
              background: "var(--wf-card)",
              borderRadius: 24,
              padding: "36px 32px",
              boxShadow: "var(--wf-shadow-xl)",
              border: "1px solid var(--wf-border)",
              maxWidth: 480,
              width: "100%",
              boxSizing: "border-box",
            }}
          >
            {/* Header: Title + Delivery Truck illustration */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: 28,
              }}
            >
              <div>
                <h2
                  style={{
                    fontFamily: "'Outfit', sans-serif",
                    fontSize: 28,
                    fontWeight: 800,
                    color: "var(--wf-dark)",
                    marginBottom: 4,
                  }}
                >
                  Welcome back
                </h2>
                <p style={{ fontSize: 13, color: "var(--wf-muted)" }}>
                  Sign in to your Whitfield workspace
                </p>
              </div>
              {/* Delivery Truck Isometric SVG */}
              <div style={{ width: 72, height: 56, flexShrink: 0 }}>
                <svg viewBox="0 0 100 80" style={{ width: "100%", height: "100%" }}>
                  {/* Isometric base */}
                  <polygon points="50,65 85,50 50,35 15,50" fill="var(--wf-cream-dark)" opacity="0.5" />
                  {/* Truck Cargo Body */}
                  <polygon points="45,45 75,32 75,12 45,25" fill="#E8E0D4" />
                  <polygon points="25,38 45,47 45,25 25,18" fill="#D4C8B5" />
                  <polygon points="25,18 45,25 75,12 55,5" fill="#FAF6F0" />
                  {/* Cabin */}
                  <polygon points="25,38 45,47 45,49 25,40" fill="var(--wf-orange-hover)" />
                  <polygon points="12,32 25,38 25,18 12,12" fill="var(--wf-orange)" />
                  {/* Wheels */}
                  <circle cx="32" cy="48" r="5" fill="#4A4A4A" />
                  <circle cx="65" cy="34" r="5" fill="#4A4A4A" />
                  {/* Cargo logo */}
                  <polygon points="32,25 38,28 38,20 32,17" fill="var(--wf-orange)" opacity="0.8" />
                </svg>
              </div>
            </div>

            {/* Tabs toggle */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 4,
                background: "var(--wf-cream)",
                borderRadius: 10,
                padding: 4,
                marginBottom: 24,
                border: "1px solid var(--wf-border)",
              }}
            >
              <button
                type="button"
                onClick={() => setActiveTab("signin")}
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: "none",
                  background: activeTab === "signin" ? "var(--wf-card)" : "transparent",
                  color: activeTab === "signin" ? "var(--wf-dark)" : "var(--wf-muted)",
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: "pointer",
                  fontFamily: "'Inter', sans-serif",
                  boxShadow: activeTab === "signin" ? "var(--wf-shadow-sm)" : "none",
                  transition: "all 0.2s",
                }}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("demo")}
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: "none",
                  background: activeTab === "demo" ? "var(--wf-card)" : "transparent",
                  color: activeTab === "demo" ? "var(--wf-dark)" : "var(--wf-muted)",
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: "pointer",
                  fontFamily: "'Inter', sans-serif",
                  boxShadow: activeTab === "demo" ? "var(--wf-shadow-sm)" : "none",
                  transition: "all 0.2s",
                }}
              >
                Quick Demo
              </button>
            </div>

            {/* Conditional Rendering based on activeTab */}
            <div style={{ minHeight: 270, display: "flex", flexDirection: "column", justifyContent: "center" }}>
              {activeTab === "signin" ? (
                /* Sign In Tab */
                <form onSubmit={form.handleSubmit(onSubmit)} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: 13,
                        fontWeight: 700,
                        color: "var(--wf-dark)",
                        marginBottom: 6,
                      }}
                    >
                      Work email
                    </label>
                    <div style={{ position: "relative" }}>
                      <Mail
                        size={16}
                        color="var(--wf-muted)"
                        style={{
                          position: "absolute",
                          left: 14,
                          top: "50%",
                          transform: "translateY(-50%)",
                        }}
                      />
                      <input
                        type="email"
                        placeholder="you@company.com"
                        disabled={isLoading}
                        autoComplete="email"
                        {...form.register("email")}
                        style={{
                          width: "100%",
                          height: 46,
                          borderRadius: 10,
                          border: "1px solid var(--wf-border)",
                          paddingLeft: 42,
                          paddingRight: 14,
                          fontSize: 14,
                          color: "var(--wf-dark)",
                          background: "var(--wf-cream)",
                          outline: "none",
                          fontFamily: "'Inter', sans-serif",
                          transition: "border-color 0.2s",
                          boxSizing: "border-box",
                        }}
                        onFocus={(e) =>
                          (e.currentTarget.style.borderColor = "var(--wf-orange)")
                        }
                        onBlur={(e) =>
                          (e.currentTarget.style.borderColor = "var(--wf-border)")
                        }
                      />
                    </div>
                    {form.formState.errors.email && (
                      <p style={{ fontSize: 12, color: "#DC4444", marginTop: 4 }}>
                        {form.formState.errors.email.message}
                      </p>
                    )}
                  </div>

                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: 13,
                        fontWeight: 700,
                        color: "var(--wf-dark)",
                        marginBottom: 6,
                      }}
                    >
                      Password
                    </label>
                    <div style={{ position: "relative" }}>
                      <Lock
                        size={16}
                        color="var(--wf-muted)"
                        style={{
                          position: "absolute",
                          left: 14,
                          top: "50%",
                          transform: "translateY(-50%)",
                        }}
                      />
                      <input
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••••"
                        disabled={isLoading}
                        autoComplete="current-password"
                        {...form.register("password")}
                        style={{
                          width: "100%",
                          height: 46,
                          borderRadius: 10,
                          border: "1px solid var(--wf-border)",
                          paddingLeft: 42,
                          paddingRight: 42,
                          fontSize: 14,
                          color: "var(--wf-dark)",
                          background: "var(--wf-cream)",
                          outline: "none",
                          fontFamily: "'Inter', sans-serif",
                          transition: "border-color 0.2s",
                          boxSizing: "border-box",
                        }}
                        onFocus={(e) =>
                          (e.currentTarget.style.borderColor = "var(--wf-orange)")
                        }
                        onBlur={(e) =>
                          (e.currentTarget.style.borderColor = "var(--wf-border)")
                        }
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        style={{
                          position: "absolute",
                          right: 12,
                          top: "50%",
                          transform: "translateY(-50%)",
                          background: "none",
                          border: "none",
                          cursor: "pointer",
                          padding: 4,
                          color: "var(--wf-muted)",
                        }}
                      >
                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                    {form.formState.errors.password && (
                      <p style={{ fontSize: 12, color: "#DC4444", marginTop: 4 }}>
                        {form.formState.errors.password.message}
                      </p>
                    )}
                  </div>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <label
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: 13,
                        color: "var(--wf-dark-secondary)",
                        cursor: "pointer",
                      }}
                    >
                      <input
                        type="checkbox"
                        defaultChecked
                        style={{
                          width: 16,
                          height: 16,
                          accentColor: "var(--wf-orange)",
                          cursor: "pointer",
                        }}
                      />
                      Remember me
                    </label>
                    <button
                      type="button"
                      style={{
                        background: "none",
                        border: "none",
                        color: "var(--wf-orange)",
                        fontSize: 13,
                        fontWeight: 700,
                        cursor: "pointer",
                      }}
                    >
                      Forgot password?
                    </button>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    style={{
                      width: "100%",
                      height: 48,
                      borderRadius: 10,
                      background: "var(--wf-orange)",
                      border: "none",
                      color: "#fff",
                      fontSize: 15,
                      fontWeight: 700,
                      cursor: isLoading ? "not-allowed" : "pointer",
                      fontFamily: "'Inter', sans-serif",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 8,
                      opacity: isLoading ? 0.7 : 1,
                      transition: "background 0.2s, opacity 0.2s",
                      boxShadow: "var(--wf-shadow-md)",
                      marginTop: 6,
                    }}
                    onMouseEnter={(e) => {
                      if (!isLoading)
                        e.currentTarget.style.background = "var(--wf-orange-hover)";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = "var(--wf-orange)";
                    }}
                  >
                    {isLoading && !selectedDemo ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : (
                      <>
                        Sign in <ArrowRight size={16} />
                      </>
                    )}
                  </button>
                </form>
              ) : (
                /* Quick Demo Tab */
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div>
                    <h3
                      style={{
                        fontFamily: "'Outfit', sans-serif",
                        fontSize: 15,
                        fontWeight: 800,
                        color: "var(--wf-dark)",
                        marginBottom: 2,
                      }}
                    >
                      Explore Whitfield Demo
                    </h3>
                    <p
                      style={{
                        fontSize: 12,
                        color: "var(--wf-muted)",
                      }}
                    >
                      Experience the platform with preloaded data
                    </p>
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(3, 1fr)",
                      gap: 8,
                    }}
                  >
                    {DEMO_CREDENTIALS.map((cred, idx) => (
                      <button
                        key={cred.role}
                        disabled={isLoading}
                        onClick={() => handleDemoLogin(idx)}
                        style={{
                          background: "var(--wf-card)",
                          border: "1px solid var(--wf-border)",
                          borderRadius: 12,
                          padding: "24px 8px",
                          cursor: isLoading ? "not-allowed" : "pointer",
                          textAlign: "center",
                          transition: "all 0.2s",
                          opacity: isLoading && selectedDemo !== idx ? 0.5 : 1,
                          boxSizing: "border-box",
                          minHeight: 180,
                          display: "flex",
                          flexDirection: "column",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                        onMouseEnter={(e) => {
                          if (!isLoading) {
                            e.currentTarget.style.borderColor = "var(--wf-orange)";
                            e.currentTarget.style.background = "var(--wf-orange-pale)";
                          }
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = "var(--wf-border)";
                          e.currentTarget.style.background = "var(--wf-card)";
                        }}
                      >
                        <div
                          style={{
                            width: 32,
                            height: 32,
                            borderRadius: "50%",
                            background: "var(--wf-orange-pale)",
                            display: "grid",
                            placeItems: "center",
                            margin: "0 auto",
                          }}
                        >
                          {isLoading && selectedDemo === idx ? (
                            <Loader2
                              size={14}
                              color="var(--wf-orange)"
                              className="animate-spin"
                            />
                          ) : (
                            <Users size={14} color="var(--wf-orange)" />
                          )}
                        </div>
                        <div>
                          <p
                            style={{
                              fontSize: 11,
                              fontWeight: 900,
                              color: "var(--wf-dark)",
                              marginBottom: 2,
                            }}
                          >
                            {cred.role}
                          </p>
                          <p
                            style={{
                              fontSize: 9,
                              color: "var(--wf-muted)",
                              lineHeight: 1.3,
                              height: 36,
                              overflow: "hidden",
                              margin: 0,
                            }}
                          >
                            {cred.description}
                          </p>
                        </div>
                        <span
                          style={{
                            fontSize: 10,
                            fontWeight: 700,
                            color: "var(--wf-orange)",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 2,
                          }}
                        >
                          Enter demo →
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ─── TRUSTED NETWORK SECTION ─── */}
      <section
        id="network"
        style={{
          borderTop: "1px solid var(--wf-border)",
          borderBottom: "1px solid var(--wf-border)",
          background: "var(--wf-cream)",
          padding: "96px 24px",
          textAlign: "center",
        }}
      >
        <div style={{ maxWidth: 1280, margin: "0 auto" }}>
          <p
            style={{
              fontSize: 12,
              fontWeight: 700,
              letterSpacing: "0.12em",
              color: "var(--wf-orange)",
              marginBottom: 16,
              textTransform: "uppercase",
            }}
          >
            COMPATIBLE LOGISTICS NETWORK
          </p>
          <h2
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: "clamp(26px, 3.5vw, 36px)",
              fontWeight: 800,
              color: "var(--wf-dark)",
              letterSpacing: "-0.02em",
              marginBottom: 16,
            }}
          >
            Integrated with active logistics and carrier systems
          </h2>
          <p
            style={{
              fontSize: 15,
              color: "var(--wf-muted)",
              maxWidth: 580,
              margin: "0 auto 48px",
              lineHeight: 1.6,
            }}
          >
            Whitfield coordinates operations with recognized carrier services and logistics networks
            to synchronize arrivals and tracking natively.
          </p>

          {/* Operational Client Groups */}
          <div style={{ marginBottom: 48 }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: "var(--wf-muted)", letterSpacing: "0.08em", marginBottom: 20, textTransform: "uppercase" }}>
              COMPATIBLE LOGISTICS GROUPS
            </p>
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: "clamp(24px, 5vw, 56px)",
                flexWrap: "wrap",
              }}
            >
              {["Kestrel Logistics", "Sable Freight Group", "Northline Supply Co.", "Harper & Vale Retail"].map((brand) => (
                <span
                  key={brand}
                  style={{
                    fontFamily: "'Outfit', sans-serif",
                    fontSize: 20,
                    fontWeight: 700,
                    color: "var(--wf-dark)",
                    letterSpacing: "0.02em",
                    opacity: 0.75,
                  }}
                >
                  {brand}
                </span>
              ))}
            </div>
          </div>

          {/* Real Carrier partners tags */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: 12,
              flexWrap: "wrap",
            }}
          >
            {["FedEx Freight", "UPS Ground", "Estes Express"].map((partner) => (
              <span
                key={partner}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "8px 16px",
                  borderRadius: 24,
                  background: "var(--wf-card)",
                  border: "1px solid var(--wf-border)",
                  fontSize: 13,
                  fontWeight: 600,
                  color: "var(--wf-dark-secondary)",
                  boxShadow: "var(--wf-shadow-sm)",
                }}
              >
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--wf-orange)" }} />
                {partner}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ─── HOW IT WORKS ─── */}
      <section
        id="how-it-works"
        style={{
          maxWidth: 1400,
          margin: "96px auto 0",
          padding: "0 24px",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 64 }}>
          <p
            style={{
              fontSize: 12,
              fontWeight: 700,
              letterSpacing: "0.12em",
              color: "var(--wf-orange)",
              marginBottom: 12,
              textTransform: "uppercase",
            }}
          >
            HOW IT WORKS
          </p>
          <h2
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: "clamp(28px, 4vw, 40px)",
              fontWeight: 800,
              color: "var(--wf-dark)",
              letterSpacing: "-0.02em",
              marginBottom: 12,
            }}
          >
            Everything you need to run
            <br />
            <span style={{ color: "var(--wf-orange)" }}>
              modern warehouse operations
            </span>
          </h2>
          <p
            style={{
              fontSize: 16,
              color: "var(--wf-muted)",
              maxWidth: 520,
              margin: "0 auto",
            }}
          >
            From receiving to shipping, Whitfield covers the complete warehouse lifecycle
            with intelligent automation.
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
            gap: 24,
          }}
        >
          {STORY_SECTIONS.map((section, idx) => (
            <div
              key={section.label}
              style={{
                background: "var(--wf-card)",
                borderRadius: 16,
                padding: "32px 28px",
                border: "1px solid var(--wf-border)",
                transition: "box-shadow 0.3s, border-color 0.3s",
                cursor: "default",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = "var(--wf-shadow-lg)";
                e.currentTarget.style.borderColor = "var(--wf-orange)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = "none";
                e.currentTarget.style.borderColor = "var(--wf-border)";
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 12,
                  background: "var(--wf-orange-pale)",
                  display: "grid",
                  placeItems: "center",
                  marginBottom: 20,
                }}
              >
                <section.icon size={24} color="var(--wf-orange)" />
              </div>

              <p
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  letterSpacing: "0.1em",
                  color: "var(--wf-orange)",
                  marginBottom: 8,
                  textTransform: "uppercase",
                }}
              >
                {section.label}
              </p>

              <h3
                style={{
                  fontFamily: "'Outfit', sans-serif",
                  fontSize: 20,
                  fontWeight: 700,
                  color: "var(--wf-dark)",
                  lineHeight: 1.3,
                  marginBottom: 12,
                }}
              >
                {section.title}
              </h3>

              <p
                style={{
                  fontSize: 14,
                  lineHeight: 1.6,
                  color: "var(--wf-muted)",
                  marginBottom: 20,
                }}
              >
                {section.description}
              </p>

              <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                {section.features.map((f) => (
                  <li
                    key={f}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      fontSize: 13,
                      color: "var(--wf-dark-secondary)",
                      marginBottom: 8,
                    }}
                  >
                    <CheckCircle2 size={14} color="var(--wf-green)" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* ─── PRODUCT PREVIEWS ─── */}
      <section
        id="platform"
        style={{
          maxWidth: 1400,
          margin: "0 auto",
          padding: "96px 24px",
          borderTop: "1px solid var(--wf-border)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 56 }}>
          <p
            style={{
              fontSize: 12,
              fontWeight: 700,
              letterSpacing: "0.12em",
              color: "var(--wf-orange)",
              marginBottom: 12,
              textTransform: "uppercase",
            }}
          >
            INSIDE THE PLATFORM
          </p>
          <h2
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: "clamp(28px, 4vw, 40px)",
              fontWeight: 800,
              color: "var(--wf-dark)",
              letterSpacing: "-0.02em",
              marginBottom: 12,
            }}
          >
            See what you'll get
            <br />
            <span style={{ color: "var(--wf-orange)" }}>after signing in</span>
          </h2>
          <p
            style={{
              fontSize: 16,
              color: "var(--wf-muted)",
              maxWidth: 480,
              margin: "0 auto",
            }}
          >
            Real screens from the Whitfield WMS. Every metric, every workflow — ready for
            your team on day one.
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 20,
          }}
        >
          {PREVIEW_SCREENS.map((screen) => (
            <div
              key={screen.title}
              style={{
                background: "var(--wf-card)",
                borderRadius: 16,
                border: "1px solid var(--wf-border)",
                overflow: "hidden",
                transition: "box-shadow 0.3s",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.boxShadow = "var(--wf-shadow-lg)")
              }
              onMouseLeave={(e) => (e.currentTarget.style.boxShadow = "none")}
            >
              {/* Fake browser chrome */}
              <div
                style={{
                  padding: "10px 16px",
                  borderBottom: "1px solid var(--wf-border)",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: "#FF5F57",
                  }}
                />
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: "#FFBD2E",
                  }}
                />
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: "#28C840",
                  }}
                />
                <div
                  style={{
                    flex: 1,
                    height: 22,
                    borderRadius: 6,
                    background: "var(--wf-cream)",
                    marginLeft: 12,
                    display: "flex",
                    alignItems: "center",
                    paddingLeft: 10,
                    fontSize: 10,
                    color: "var(--wf-muted)",
                  }}
                >
                  app.whitfield.io/{screen.title.toLowerCase().replace(/ /g, "-")}
                </div>
              </div>

              {/* Screen content */}
              <div style={{ padding: "20px 20px 24px" }}>
                <h4
                  style={{
                    fontFamily: "'Outfit', sans-serif",
                    fontSize: 16,
                    fontWeight: 700,
                    color: "var(--wf-dark)",
                    marginBottom: 4,
                  }}
                >
                  {screen.title}
                </h4>
                <p
                  style={{
                    fontSize: 12,
                    color: "var(--wf-muted)",
                    marginBottom: 16,
                  }}
                >
                  {screen.description}
                </p>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 10,
                  }}
                >
                  {screen.metrics.map((m) => (
                    <div
                      key={m.label}
                      style={{
                        background: "var(--wf-cream)",
                        borderRadius: 10,
                        padding: "12px 14px",
                      }}
                    >
                      <p
                        style={{
                          fontSize: 10,
                          fontWeight: 600,
                          color: "var(--wf-muted)",
                          marginBottom: 4,
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                        }}
                      >
                        {m.label}
                      </p>
                      <p
                        style={{
                          fontSize: 22,
                          fontWeight: 800,
                          color: "var(--wf-dark)",
                          fontFamily: "'Outfit', sans-serif",
                          lineHeight: 1,
                        }}
                      >
                        {m.value}
                      </p>
                      <p
                        style={{
                          fontSize: 11,
                          fontWeight: 600,
                          color: "var(--wf-green)",
                          marginTop: 2,
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                        }}
                      >
                        <TrendingUp size={11} /> {m.trend}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── RESOURCES SECTION ─── */}
      <section
        id="resources"
        style={{
          borderTop: "1px solid var(--wf-border)",
          background: "var(--wf-cream)",
          padding: "96px 24px",
        }}
      >
        <div style={{ maxWidth: 1280, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <p
              style={{
                fontSize: 12,
                fontWeight: 700,
                letterSpacing: "0.12em",
                color: "var(--wf-orange)",
                marginBottom: 12,
                textTransform: "uppercase",
              }}
            >
              RESOURCES & INSIGHTS
            </p>
            <h2
              style={{
                fontFamily: "'Outfit', sans-serif",
                fontSize: "clamp(26px, 3.5vw, 36px)",
                fontWeight: 800,
                color: "var(--wf-dark)",
                letterSpacing: "-0.02em",
                marginBottom: 12,
              }}
            >
              Knowledge to power your operations
            </h2>
            <p
              style={{
                fontSize: 15,
                color: "var(--wf-muted)",
                maxWidth: 480,
                margin: "0 auto",
              }}
            >
              Read guides, technical documentation, and best practices curated by Whitfield logistics experts.
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
              gap: 24,
            }}
          >
            {[
              {
                title: "Inbound Cargo Workflows",
                desc: "Guided step-by-step procedures for logging incoming shipments, scanning item barcodes, measuring dimensions, and managing manager approvals.",
                tag: "Receiving Guides",
              },
              {
                title: "Atomic Order Reservation",
                desc: "Technical explanation of how the reservation system locks stored items during order processing to prevent concurrent conflicts.",
                tag: "System Docs",
              },
              {
                title: "Voice-to-Data Pipeline",
                desc: "Instruction guide on using hands-free voice dictation to process cargo descriptions and transcribe logs via LLM parsing.",
                tag: "Voice scanning",
              },
            ].map((res) => (
              <div
                key={res.title}
                style={{
                  background: "var(--wf-card)",
                  borderRadius: 16,
                  padding: "32px 28px",
                  border: "1px solid var(--wf-border)",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  transition: "all 0.3s",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = "var(--wf-shadow-lg)";
                  e.currentTarget.style.borderColor = "var(--wf-orange)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = "none";
                  e.currentTarget.style.borderColor = "var(--wf-border)";
                }}
              >
                <div>
                  <span
                    style={{
                      display: "inline-block",
                      padding: "4px 10px",
                      borderRadius: 20,
                      background: "var(--wf-orange-pale)",
                      color: "var(--wf-orange)",
                      fontSize: 11,
                      fontWeight: 700,
                      marginBottom: 16,
                    }}
                  >
                    {res.tag}
                  </span>
                  <h4
                    style={{
                      fontFamily: "'Outfit', sans-serif",
                      fontSize: 18,
                      fontWeight: 700,
                      color: "var(--wf-dark)",
                      marginBottom: 12,
                      lineHeight: 1.3,
                    }}
                  >
                    {res.title}
                  </h4>
                  <p
                    style={{
                      fontSize: 14,
                      lineHeight: 1.6,
                      color: "var(--wf-muted)",
                      marginBottom: 20,
                    }}
                  >
                    {res.desc}
                  </p>
                </div>
                <a
                  href="#resources"
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: "var(--wf-orange)",
                    textDecoration: "none",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 4,
                  }}
                >
                  Read Article <ArrowRight size={14} />
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── FINAL CTA ─── */}
      <section
        style={{
          maxWidth: 800,
          margin: "96px auto 0",
          padding: "64px 24px",
          textAlign: "center",
        }}
      >
        <div
          style={{
            background: "var(--wf-card)",
            borderRadius: 24,
            padding: "56px 40px",
            boxShadow: "var(--wf-shadow-xl)",
            border: "1px solid var(--wf-border)",
          }}
        >
          <h2
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: "clamp(24px, 3.5vw, 36px)",
              fontWeight: 800,
              color: "var(--wf-dark)",
              letterSpacing: "-0.02em",
              marginBottom: 12,
            }}
          >
            Start managing your warehouse{" "}
            <span style={{ color: "var(--wf-orange)" }}>today</span>
          </h2>
          <p
            style={{
              fontSize: 16,
              color: "var(--wf-muted)",
              marginBottom: 28,
              maxWidth: 440,
              marginLeft: "auto",
              marginRight: "auto",
            }}
          >
            Join operations teams that trust Whitfield to power their warehouse workflows
            with real-time intelligence.
          </p>
          <div
            style={{
              display: "flex",
              gap: 12,
              justifyContent: "center",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={() => {
                const el = document.getElementById("signin-card");
                el?.scrollIntoView({ behavior: "smooth", block: "center" });
              }}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "14px 32px",
                borderRadius: 10,
                background: "var(--wf-orange)",
                border: "none",
                color: "#fff",
                fontSize: 15,
                fontWeight: 700,
                cursor: "pointer",
                fontFamily: "'Inter', sans-serif",
                boxShadow: "var(--wf-shadow-md)",
                transition: "background 0.2s",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background = "var(--wf-orange-hover)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.background = "var(--wf-orange)")
              }
            >
              Get started free <ArrowRight size={16} />
            </button>
            <button
              onClick={() => {
                const el = document.getElementById("how-it-works");
                if (el) {
                  const offset = 80; // height of sticky header + padding
                  const bodyRect = document.body.getBoundingClientRect().top;
                  const elementRect = el.getBoundingClientRect().top;
                  const elementPosition = elementRect - bodyRect;
                  const offsetPosition = elementPosition - offset;

                  window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                  });
                }
              }}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "14px 32px",
                borderRadius: 10,
                background: "transparent",
                border: "1px solid var(--wf-border)",
                color: "var(--wf-dark)",
                fontSize: 15,
                fontWeight: 600,
                cursor: "pointer",
                fontFamily: "'Inter', sans-serif",
              }}
            >
              Learn more
            </button>
          </div>
        </div>
      </section>

      {/* ─── ABOUT US / ACTIVE WAREHOUSE NETWORK SECTION ─── */}
      <section
        id="about-us"
        style={{
          borderTop: "1px solid var(--wf-border)",
          background: "var(--wf-cream)",
          padding: "96px 24px",
        }}
      >
        <div style={{ maxWidth: 1280, margin: "0 auto" }}>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr",
              gap: 48,
              alignItems: "start",
            }}
            className="wf-about-grid"
          >
            {/* Left: Operations Description */}
            <div>
              <p
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  color: "var(--wf-orange)",
                  marginBottom: 16,
                  textTransform: "uppercase",
                }}
              >
                ACTIVE WAREHOUSE NETWORK
              </p>
              <h2
                style={{
                  fontFamily: "'Outfit', sans-serif",
                  fontSize: "clamp(26px, 3.5vw, 36px)",
                  fontWeight: 800,
                  color: "var(--wf-dark)",
                  letterSpacing: "-0.02em",
                  marginBottom: 20,
                  lineHeight: 1.2,
                }}
              >
                Physical nodes powering the Whitfield system
              </h2>
              <p
                style={{
                  fontSize: 15,
                  lineHeight: 1.7,
                  color: "var(--wf-muted)",
                  marginBottom: 16,
                }}
              >
                The Whitfield Warehouse Management System governs operations across our physically active distribution yards. 
                Each facility utilizes zones, bins, and racks synchronized in real-time under manager oversight.
              </p>
              <p
                style={{
                  fontSize: 15,
                  lineHeight: 1.7,
                  color: "var(--wf-muted)",
                }}
              >
                Registered logistics managers coordinate arrivals, carrier tracking, and order picking directly within these locations.
              </p>
            </div>

            {/* Right: Actual Warehouses Stats */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 16,
                width: "100%",
              }}
            >
              {[
                {
                  code: "WHT-01",
                  name: "Whitfield North",
                  addr: "1420 Harbor Rd, Oakland, CA 94607",
                  manager: "John Mercer",
                  util: "85% Utilized",
                  items: "2,310 Items Logged",
                },
                {
                  code: "WHT-02",
                  name: "Dalton Yard",
                  addr: "88 Dalton Ave, Reno, NV 89502",
                  manager: "Ada Sloane",
                  util: "62% Utilized",
                  items: "1,408 Items Logged",
                },
                {
                  code: "WHT-03",
                  name: "Redmoor",
                  addr: "7 Redmoor Industrial Park, Boise, ID 83702",
                  manager: "Ravi Menon",
                  util: "44% Utilized",
                  items: "890 Items Logged",
                },
              ].map((wh) => (
                <div
                  key={wh.code}
                  style={{
                    background: "var(--wf-card)",
                    border: "1px solid var(--wf-border)",
                    borderRadius: 16,
                    padding: "20px 24px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 12,
                    boxShadow: "var(--wf-shadow-sm)",
                  }}
                >
                  <div style={{ textAlign: "left" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <span
                        style={{
                          fontSize: 10,
                          fontWeight: 800,
                          background: "var(--wf-orange-pale)",
                          color: "var(--wf-orange)",
                          padding: "2px 6px",
                          borderRadius: 4,
                        }}
                      >
                        {wh.code}
                      </span>
                      <h4
                        style={{
                          fontFamily: "'Outfit', sans-serif",
                          fontSize: 16,
                          fontWeight: 700,
                          color: "var(--wf-dark)",
                        }}
                      >
                        {wh.name}
                      </h4>
                    </div>
                    <p style={{ fontSize: 12, color: "var(--wf-muted)", marginBottom: 2 }}>{wh.addr}</p>
                    <p style={{ fontSize: 11, color: "var(--wf-muted)" }}>Manager: <strong>{wh.manager}</strong></p>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <p style={{ fontSize: 14, fontWeight: 800, color: "var(--wf-orange)" }}>{wh.util}</p>
                    <p style={{ fontSize: 11, color: "var(--wf-muted)" }}>{wh.items}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ─── FOOTER ─── */}
      <footer
        style={{
          maxWidth: 1400,
          margin: "64px auto 0",
          padding: "24px 24px 48px",
          borderTop: "1px solid var(--wf-border)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 16,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: "var(--wf-orange)",
              display: "grid",
              placeItems: "center",
              color: "#fff",
              fontFamily: "'Outfit', sans-serif",
              fontWeight: 800,
              fontSize: 13,
            }}
          >
            W
          </div>
          <span
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontWeight: 600,
              fontSize: 14,
              color: "var(--wf-dark)",
            }}
          >
            Whitfield WMS
          </span>
        </div>
        <p style={{ fontSize: 12, color: "var(--wf-muted)" }}>
          © 2025 Whitfield WMS. All rights reserved.
        </p>
      </footer>

      {/* ─── RESPONSIVE STYLES ─── */}
      <style>{`
        .wf-hero-split {
          grid-template-columns: 1fr !important;
        }
        .wf-inner-left {
          grid-template-columns: 1fr !important;
          text-align: center;
        }
        .wf-inner-left button {
          justify-content: center;
          margin: 0 auto;
        }
        .wf-nav-links {
          display: none !important;
        }
        .wf-feature-badges {
          grid-template-columns: 1fr !important;
        }
        .wf-security-specs {
          justify-content: center;
          flex-wrap: wrap;
        }
        #signin-card {
          margin: 0 auto !important;
        }

        @media (min-width: 768px) {
          .wf-inner-left {
            grid-template-columns: 1fr 1fr !important;
            text-align: left;
          }
          .wf-inner-left button {
            justify-content: flex-start;
            margin: 0;
          }
          .wf-feature-badges {
            grid-template-columns: repeat(3, 1fr) !important;
          }
          .wf-security-specs {
            justify-content: flex-start;
          }
        }

        .wf-about-grid {
          grid-template-columns: 1fr !important;
        }
        @media (min-width: 1024px) {
          .wf-hero-split {
            grid-template-columns: 1.25fr 0.75fr !important;
            gap: 48px !important;
          }
          .wf-nav-links {
            display: flex !important;
          }
          .wf-about-grid {
            grid-template-columns: 1.1fr 0.9fr !important;
            gap: 64px !important;
          }
        }
        @media (max-width: 640px) {
          .wf-stats-grid {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

/* ─── Tab Button helper ─── */
function TabButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        padding: "8px 12px",
        borderRadius: 8,
        border: "none",
        background: active ? "var(--wf-card)" : "transparent",
        color: active ? "var(--wf-dark)" : "var(--wf-muted)",
        fontSize: 13,
        fontWeight: 600,
        cursor: "pointer",
        fontFamily: "'Inter', sans-serif",
        boxShadow: active ? "var(--wf-shadow-sm)" : "none",
        transition: "all 0.2s",
      }}
    >
      {label}
    </button>
  );
}
