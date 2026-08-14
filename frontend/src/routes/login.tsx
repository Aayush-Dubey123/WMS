import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2, ShieldCheck, Zap, CheckCircle2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
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
    color: "bg-blue-600",
  },
  {
    role: "MANAGER",
    email: "manager@whitfield.com",
    password: "ManagerPass123!",
    description: "Warehouse operations, staff management",
    color: "bg-purple-600",
  },
  {
    role: "STAFF",
    email: "staff@whitfield.com",
    password: "StaffPass123!",
    description: "Operational tasks, receiving, packing",
    color: "bg-green-600",
  },
];

export const Route = createFileRoute("/login")({
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
    const cred = DEMO_CREDENTIALS[index];
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
      <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 flex items-center justify-center px-4">
        <div className="text-center space-y-6 animate-in fade-in duration-500">
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-cyan-400 rounded-full blur-xl opacity-50 animate-pulse" />
              <div className="relative grid size-20 place-items-center rounded-full bg-gradient-to-br from-primary to-cyan-400 text-white">
                <CheckCircle2 className="size-10" />
              </div>
            </div>
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-white">Welcome!</h2>
            <p className="text-slate-400">Redirecting to dashboard...</p>
          </div>
          <div className="flex justify-center">
            <Loader2 className="size-5 animate-spin text-primary" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left side - Premium Branding */}
          <div className="hidden lg:flex flex-col justify-center space-y-10">
            {/* Logo & Title */}
            <div className="space-y-6">
              <div className="flex items-end gap-4">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl blur-2xl opacity-40" />
                  <div className="relative grid size-16 place-items-center rounded-2xl bg-gradient-to-br from-primary to-cyan-400 text-white shadow-2xl">
                    <ShieldCheck className="size-8" />
                  </div>
                </div>
                <div>
                  <h1 className="text-5xl font-black text-white tracking-tight">Whitfield</h1>
                  <p className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                    WMS
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-xl font-semibold text-white">
                  Enterprise Warehouse Management
                </p>
                <p className="text-slate-400 leading-relaxed">
                  Real-time operations platform for modern fulfillment centers
                </p>
              </div>
            </div>

            {/* Feature List */}
            <div className="space-y-4">
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
                <div key={i} className="flex gap-4 group">
                  <div className="flex-shrink-0 mt-1">
                    <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-400/20 to-blue-500/20 group-hover:from-cyan-400/40 group-hover:to-blue-500/40 transition-all duration-300">
                      <feature.icon className="h-5 w-5 text-cyan-400" />
                    </div>
                  </div>
                  <div>
                    <p className="font-semibold text-white text-sm">{feature.title}</p>
                    <p className="text-slate-400 text-sm">{feature.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right side - Premium Login Card */}
          <Card className="border-slate-700/50 bg-gradient-to-br from-slate-800/95 to-slate-900/95 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
            {/* Gradient Background Effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5 pointer-events-none" />

            <CardHeader className="space-y-4 text-center pb-8 relative z-10">
              <div className="flex justify-center lg:hidden mb-2">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-xl blur-xl opacity-40" />
                  <div className="relative grid size-14 place-items-center rounded-xl bg-gradient-to-br from-primary to-cyan-400 text-white">
                    <ShieldCheck className="size-7" />
                  </div>
                </div>
              </div>
              <div>
                <CardTitle className="text-3xl font-black text-white">Access WMS</CardTitle>
                <CardDescription className="text-base mt-2 text-slate-400">
                  Sign in to manage your warehouse operations
                </CardDescription>
              </div>
            </CardHeader>

            <CardContent className="space-y-6 relative z-10">
              <Tabs defaultValue="demo" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-slate-700/30 border border-slate-600/30 p-1 rounded-lg">
                  <TabsTrigger
                    value="demo"
                    className="rounded-md font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500/20 data-[state=active]:to-blue-500/20 data-[state=active]:text-white"
                  >
                    Quick Demo
                  </TabsTrigger>
                  <TabsTrigger
                    value="credentials"
                    className="rounded-md font-semibold data-[state=active]:bg-gradient-to-r data-[state=active]:from-cyan-500/20 data-[state=active]:to-blue-500/20 data-[state=active]:text-white"
                  >
                    Sign In
                  </TabsTrigger>
                </TabsList>

                {/* Demo Tab */}
                <TabsContent value="demo" className="space-y-4 mt-8">
                  <p className="text-sm text-slate-400 font-medium">
                    Select your role for instant access:
                  </p>
                  <div className="space-y-3">
                    {DEMO_CREDENTIALS.map((cred, idx) => (
                      <button
                        key={cred.role}
                        disabled={isLoading}
                        onClick={() => handleDemoLogin(idx)}
                        className="w-full group relative overflow-hidden rounded-xl border border-slate-600/30 bg-slate-700/20 hover:bg-slate-700/40 disabled:opacity-50 disabled:cursor-not-allowed p-4 transition-all duration-300"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-500/10 to-blue-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        <div className="relative flex items-center justify-between">
                          <div className="text-left">
                            <div className="flex items-center gap-3 mb-1">
                              <Badge
                                className={`${cred.color} text-white text-xs font-bold px-3 py-1 rounded-full`}
                              >
                                {cred.role}
                              </Badge>
                            </div>
                            <p className="text-sm text-slate-400 font-medium">
                              {cred.description}
                            </p>
                          </div>
                          {isLoading && selectedDemo === idx ? (
                            <Loader2 className="size-5 animate-spin text-primary flex-shrink-0" />
                          ) : (
                            <div className="size-5 rounded-full bg-slate-600/30 group-hover:bg-cyan-400/30 transition-colors" />
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </TabsContent>

                {/* Credentials Tab */}
                <TabsContent value="credentials" className="space-y-5 mt-8">
                  <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                      <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-sm font-semibold text-slate-200">
                              Email Address
                            </FormLabel>
                            <FormControl>
                              <Input
                                type="email"
                                placeholder="admin@whitfield.com"
                                disabled={isLoading}
                                autoComplete="email"
                                className="bg-slate-700/30 border-slate-600/30 text-white placeholder:text-slate-500 focus:border-cyan-500/50 focus:ring-cyan-500/20 h-11 rounded-lg"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="text-sm font-semibold text-slate-200">
                              Password
                            </FormLabel>
                            <FormControl>
                              <Input
                                type="password"
                                placeholder="••••••••"
                                disabled={isLoading}
                                autoComplete="current-password"
                                className="bg-slate-700/30 border-slate-600/30 text-white placeholder:text-slate-500 focus:border-cyan-500/50 focus:ring-cyan-500/20 h-11 rounded-lg"
                                {...field}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <Button
                        type="submit"
                        disabled={isLoading}
                        size="lg"
                        className="w-full h-12 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold rounded-lg transition-all duration-300 shadow-lg hover:shadow-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Signing in...
                          </>
                        ) : (
                          "Sign In"
                        )}
                      </Button>
                    </form>
                  </Form>
                </TabsContent>
              </Tabs>

              {/* Info Box */}
              <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 mt-6">
                <p className="text-xs font-semibold text-amber-200 mb-1">
                  🔐 Development Environment
                </p>
                <p className="text-xs text-amber-100/70">
                  Use demo credentials or your production account. In production, only verified credentials work.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
