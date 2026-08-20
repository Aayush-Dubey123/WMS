import { createFileRoute, useNavigate, redirect } from "@tanstack/react-router";
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
  ShieldCheck,
  Zap,
  Boxes,
  Users,
} from "lucide-react";

import { useAuth } from "@/lib/auth-context";

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
    description: "Full system access, facility management",
    color: "bg-primary",
  },
  {
    role: "MANAGER",
    email: "manager@whitfield.com",
    password: "ManagerPass123!",
    description: "Warehouse operations, staff management",
    color: "bg-info",
  },
  {
    role: "STAFF",
    email: "staff@whitfield.com",
    password: "StaffPass123!",
    description: "Operational tasks, receiving, packing",
    color: "bg-warning",
  },
];

export const Route = createFileRoute("/login")({
  beforeLoad: () => {
    throw redirect({ to: "/landing" });
  },
  head: () => ({
    meta: [
      { title: "Login — Whitfield WMS" },
      { name: "description", content: "Sign in to your Whitfield WMS account" },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading, login: authLogin } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState<number | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // Redirect if already authenticated or after success login
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      // Wait 1 second for success animation before redirect
      const timer = setTimeout(() => {
        navigate({ to: "/" });
      }, 1000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [isAuthenticated, authLoading, navigate]);

  const onSubmit = async (data: LoginFormValues) => {
    if (!data.email || !data.password) {
      toast.error("Email and password are required");
      return;
    }

    setIsLoading(true);
    try {
      await authLogin(data.email, data.password);
      setShowSuccess(true);
      toast.success("Logged in successfully!", {
        icon: <CheckCircle2 className="size-4" />,
      });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Login failed. Please try again.";
      toast.error(errorMessage);
      console.error("Login error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (index: number) => {
    setSelectedDemo(index);
    const cred = DEMO_CREDENTIALS[index]!;
    setIsLoading(true);
    try {
      console.log(`🔐 Attempting ${cred.role} login with ${cred.email}...`);
      await authLogin(cred.email, cred.password);
      console.log(`✅ Login successful for ${cred.role}`);
      setShowSuccess(true);
      toast.success(`Welcome, ${cred.role}!`, {
        icon: <CheckCircle2 className="size-4" />,
      });
    } catch (error) {
      console.error(`❌ Login failed for ${cred.role}:`, error);
      const errorMessage =
        error instanceof Error ? error.message : `Login failed for ${cred.role}. Check backend credentials.`;
      toast.error(errorMessage);
      setSelectedDemo(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Show success animation
  if (showSuccess && isAuthenticated) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "var(--wf-cream)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 16,
        }}
      >
        <div style={{ textAlign: "center" }} className="animate-in fade-in duration-500">
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
            <div style={{ position: "relative" }}>
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  borderRadius: "50%",
                  background: "var(--wf-orange)",
                  filter: "blur(20px)",
                  opacity: 0.3,
                }}
                className="animate-pulse"
              />
              <div
                style={{
                  position: "relative",
                  width: 80,
                  height: 80,
                  borderRadius: "50%",
                  background: "var(--wf-orange)",
                  display: "grid",
                  placeItems: "center",
                  color: "#fff",
                }}
              >
                <CheckCircle2 size={40} />
              </div>
            </div>
          </div>
          <h2
            style={{
              fontFamily: "'Outfit', sans-serif",
              fontSize: 30,
              fontWeight: 800,
              color: "var(--wf-dark)",
              marginBottom: 8,
            }}
          >
            Welcome!
          </h2>
          <p style={{ color: "var(--wf-muted)", marginBottom: 16 }}>
            Redirecting to dashboard...
          </p>
          <Loader2
            size={20}
            className="animate-spin"
            style={{ color: "var(--wf-orange)", margin: "0 auto" }}
          />
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--wf-cream)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "32px 16px",
      }}
    >
      <div style={{ width: "100%", maxWidth: 1100 }}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr",
            gap: 48,
            alignItems: "center",
          }}
          className="wf-login-grid"
        >
          {/* Left side - Branding */}
          <div className="wf-login-left" style={{ display: "none" }}>
            {/* Logo & Title */}
            <div style={{ marginBottom: 40 }}>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 16, marginBottom: 24 }}>
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: 16,
                    background: "var(--wf-orange)",
                    display: "grid",
                    placeItems: "center",
                    boxShadow: "var(--wf-shadow-md)",
                  }}
                >
                  <span
                    style={{
                      color: "#fff",
                      fontFamily: "'Outfit', sans-serif",
                      fontWeight: 900,
                      fontSize: 28,
                    }}
                  >
                    W
                  </span>
                </div>
                <div>
                  <h1
                    style={{
                      fontFamily: "'Outfit', sans-serif",
                      fontSize: 48,
                      fontWeight: 900,
                      color: "var(--wf-dark)",
                      letterSpacing: "-0.03em",
                      lineHeight: 1,
                    }}
                  >
                    Whitfield
                  </h1>
                  <p
                    style={{
                      fontSize: 20,
                      fontWeight: 700,
                      color: "var(--wf-orange)",
                    }}
                  >
                    WMS
                  </p>
                </div>
              </div>
              <p
                style={{
                  fontSize: 20,
                  fontWeight: 600,
                  color: "var(--wf-dark)",
                  marginBottom: 8,
                }}
              >
                Enterprise Warehouse Management
              </p>
              <p
                style={{
                  fontSize: 15,
                  color: "var(--wf-muted)",
                  lineHeight: 1.6,
                }}
              >
                Real-time operations platform for modern fulfillment centers
              </p>
            </div>

            {/* Feature List */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {[
                {
                  icon: Zap,
                  title: "Real-Time Operations",
                  desc: "Live tracking of orders, arrivals, and inventory",
                },
                {
                  icon: ShieldCheck,
                  title: "Role-Based Access",
                  desc: "OWNER, MANAGER, STAFF with granular permissions",
                },
                {
                  icon: CheckCircle2,
                  title: "Advanced Features",
                  desc: "Voice pipeline, vision AI, complete audit logs",
                },
              ].map((feature, i) => (
                <div
                  key={i}
                  style={{ display: "flex", gap: 14, alignItems: "flex-start" }}
                >
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: 10,
                      background: "var(--wf-orange-pale)",
                      display: "grid",
                      placeItems: "center",
                      flexShrink: 0,
                      marginTop: 2,
                    }}
                  >
                    <feature.icon size={20} color="var(--wf-orange)" />
                  </div>
                  <div>
                    <p
                      style={{
                        fontSize: 14,
                        fontWeight: 700,
                        color: "var(--wf-dark)",
                      }}
                    >
                      {feature.title}
                    </p>
                    <p style={{ fontSize: 14, color: "var(--wf-muted)" }}>
                      {feature.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right side - Login Card */}
          <div
            style={{
              background: "var(--wf-card)",
              borderRadius: 20,
              padding: "36px 32px",
              boxShadow: "var(--wf-shadow-xl)",
              border: "1px solid var(--wf-border)",
              maxWidth: 440,
              width: "100%",
              margin: "0 auto",
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginBottom: 8,
              }}
              className="wf-login-mobile-logo"
            >
              <div
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 14,
                  background: "var(--wf-orange)",
                  display: "grid",
                  placeItems: "center",
                  boxShadow: "var(--wf-shadow-sm)",
                }}
              >
                <span
                  style={{
                    color: "#fff",
                    fontFamily: "'Outfit', sans-serif",
                    fontWeight: 900,
                    fontSize: 24,
                  }}
                >
                  W
                </span>
              </div>
            </div>

            <div style={{ textAlign: "center", marginBottom: 28 }}>
              <h2
                style={{
                  fontFamily: "'Outfit', sans-serif",
                  fontSize: 28,
                  fontWeight: 800,
                  color: "var(--wf-dark)",
                  marginBottom: 6,
                }}
              >
                Access WMS
              </h2>
              <p style={{ fontSize: 14, color: "var(--wf-muted)" }}>
                Sign in to manage your warehouse operations
              </p>
            </div>

            {/* Tab selector */}
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
              <TabButton
                active={selectedDemo === null && !form.formState.isDirty}
                label="Quick Demo"
                onClick={() => setSelectedDemo(null)}
              />
              <TabButton
                active={form.formState.isDirty || selectedDemo !== null}
                label="Sign In"
                onClick={() => {}}
              />
            </div>

            {/* Demo Credentials */}
            <div style={{ marginBottom: 20 }}>
              <p
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: "var(--wf-muted)",
                  marginBottom: 12,
                }}
              >
                Select your role for instant access:
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {DEMO_CREDENTIALS.map((cred, idx) => (
                  <button
                    key={cred.role}
                    disabled={isLoading}
                    onClick={() => handleDemoLogin(idx)}
                    style={{
                      width: "100%",
                      padding: "14px 16px",
                      borderRadius: 12,
                      border: "1px solid var(--wf-border)",
                      background: "var(--wf-cream)",
                      cursor: isLoading ? "not-allowed" : "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      transition: "all 0.2s",
                      opacity: isLoading && selectedDemo !== idx ? 0.5 : 1,
                    }}
                    onMouseEnter={(e) => {
                      if (!isLoading) {
                        e.currentTarget.style.borderColor = "var(--wf-orange)";
                        e.currentTarget.style.background = "var(--wf-orange-pale)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = "var(--wf-border)";
                      e.currentTarget.style.background = "var(--wf-cream)";
                    }}
                  >
                    <div style={{ textAlign: "left" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
                        <span
                          style={{
                            display: "inline-block",
                            padding: "2px 10px",
                            borderRadius: 20,
                            background: "var(--wf-orange)",
                            color: "#fff",
                            fontSize: 11,
                            fontWeight: 800,
                          }}
                        >
                          {cred.role}
                        </span>
                      </div>
                      <p style={{ fontSize: 13, color: "var(--wf-muted)", fontWeight: 500 }}>
                        {cred.description}
                      </p>
                    </div>
                    {isLoading && selectedDemo === idx ? (
                      <Loader2 size={18} className="animate-spin" style={{ color: "var(--wf-orange)", flexShrink: 0 }} />
                    ) : (
                      <div
                        style={{
                          width: 20,
                          height: 20,
                          borderRadius: "50%",
                          border: "2px solid var(--wf-border)",
                          flexShrink: 0,
                        }}
                      />
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Divider */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                margin: "20px 0",
              }}
            >
              <div style={{ flex: 1, height: 1, background: "var(--wf-border)" }} />
              <span style={{ fontSize: 12, color: "var(--wf-muted)", fontWeight: 500 }}>
                OR SIGN IN
              </span>
              <div style={{ flex: 1, height: 1, background: "var(--wf-border)" }} />
            </div>

            {/* Login Form */}
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <div style={{ marginBottom: 16 }}>
                <label
                  style={{
                    display: "block",
                    fontSize: 13,
                    fontWeight: 600,
                    color: "var(--wf-dark)",
                    marginBottom: 6,
                  }}
                >
                  Email Address
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
                    placeholder="admin@whitfield.com"
                    disabled={isLoading}
                    autoComplete="email"
                    {...form.register("email")}
                    style={{
                      width: "100%",
                      height: 44,
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

              <div style={{ marginBottom: 20 }}>
                <label
                  style={{
                    display: "block",
                    fontSize: 13,
                    fontWeight: 600,
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
                    placeholder="••••••••"
                    disabled={isLoading}
                    autoComplete="current-password"
                    {...form.register("password")}
                    style={{
                      width: "100%",
                      height: 44,
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
                }}
                onMouseEnter={(e) => {
                  if (!isLoading)
                    e.currentTarget.style.background = "var(--wf-orange-hover)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "var(--wf-orange)";
                }}
              >
                {isLoading && selectedDemo === null ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>

            {/* Info Box */}
            <div
              style={{
                borderRadius: 12,
                border: "1px solid var(--wf-orange-light)",
                background: "var(--wf-orange-pale)",
                padding: 14,
                marginTop: 20,
              }}
            >
              <p
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: "var(--wf-orange)",
                  marginBottom: 2,
                }}
              >
                Development Environment
              </p>
              <p style={{ fontSize: 12, color: "var(--wf-brown)" }}>
                Use demo credentials or your production account. In production, only verified
                credentials work.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Responsive styles */}
      <style>{`
        .wf-login-grid {
          grid-template-columns: 1fr !important;
        }
        @media (min-width: 1024px) {
          .wf-login-grid {
            grid-template-columns: 1fr 1fr !important;
          }
          .wf-login-left {
            display: flex !important;
            flex-direction: column;
            justify-content: center;
          }
          .wf-login-mobile-logo {
            display: none !important;
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
