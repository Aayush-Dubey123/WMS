import { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useAuth, type UserRole } from "./auth-context";
import { Loader2 } from "lucide-react";

export interface ProtectedRouteProps {
  requiredRoles?: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * ProtectedRoute component that enforces authentication and role-based access
 *
 * Usage:
 * <ProtectedRoute requiredRoles={["OWNER", "MANAGER"]}>
 *   <YourComponent />
 * </ProtectedRoute>
 */
export function ProtectedRoute({
  requiredRoles,
  children,
  fallback,
}: ProtectedRouteProps) {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, hasRole } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    // Not authenticated - redirect to login
    if (!isAuthenticated) {
      navigate({ to: "/login" });
      return;
    }

    // Authenticated but doesn't have required role
    if (requiredRoles && requiredRoles.length > 0 && !hasRole(requiredRoles)) {
      navigate({ to: "/" });
      return;
    }
  }, [isAuthenticated, isLoading, requiredRoles, hasRole, navigate]);

  // Show loading state
  if (isLoading) {
    return (
      fallback || (
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto size-8 animate-spin text-primary" />
            <p className="mt-4 text-sm text-muted-foreground">Loading...</p>
          </div>
        </div>
      )
    );
  }

  // Not authenticated - show loading (will redirect shortly)
  if (!isAuthenticated) {
    return (
      fallback || (
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto size-8 animate-spin text-primary" />
            <p className="mt-4 text-sm text-muted-foreground">Redirecting to login...</p>
          </div>
        </div>
      )
    );
  }

  // Authenticated and authorized - render children
  return <>{children}</>;
}

/**
 * Hook to conditionally render content based on user role
 *
 * Usage:
 * const showAdminPanel = useCanAccess(["OWNER"]);
 * {showAdminPanel && <AdminPanel />}
 */
export function useCanAccess(roles: UserRole[]) {
  const { hasRole } = useAuth();
  return hasRole(roles);
}
