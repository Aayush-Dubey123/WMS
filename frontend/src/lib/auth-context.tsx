import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { authAPI, tokenManager } from "./api";

export type UserRole = "OWNER" | "MANAGER" | "STAFF";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  warehouse_id?: string;
  experience_tier?: "ROOKIE" | "EXPERIENCED";
  function_roles?: string[];
  status: string;
}

export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: UserRole | UserRole[]) => boolean;
  canAccess: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    restoreSession();
  }, []);

  async function restoreSession() {
    try {
      const token = tokenManager.getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      const profile = (await authAPI.getProfile()) as AuthUser;
      setUser(profile);
    } catch (error) {
      tokenManager.clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }

  async function login(email: string, password: string) {
    const response = (await authAPI.login(email, password)) as {
      access_token: string;
      refresh_token: string;
    };
    tokenManager.setTokens(response.access_token, response.refresh_token);
    const profile = (await authAPI.getProfile()) as AuthUser;
    setUser(profile);
  }

  function logout() {
    tokenManager.clearTokens();
    setUser(null);
    window.location.href = "/landing";
  }

  function hasRole(role: UserRole | UserRole[]) {
    if (!user) return false;
    const roles = Array.isArray(role) ? role : [role];
    return roles.includes(user.role);
  }

  function canAccess(roles: UserRole[]) {
    return hasRole(roles);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasRole,
        canAccess,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
