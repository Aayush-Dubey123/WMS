import { useState, useRef, useCallback, useEffect } from "react";
import React from "react";
import { useAuth } from "./auth-context";
import { toast } from "sonner";
import { CheckCircle2 } from "lucide-react";

export interface DemoCredential {
  role: string;
  email: string;
  password: string;
  description: string;
}

export function useDemoLogin(
  demoCredentials: DemoCredential[],
  onSuccessCallback?: () => void
) {
  const { login: authLogin } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDemo, setSelectedDemo] = useState<number | null>(null);
  const [demoModalOpen, setDemoModalOpen] = useState(false);
  const [demoStatus, setDemoStatus] = useState<"connecting" | "success" | "error">("connecting");
  const [demoErrorMessage, setDemoErrorMessage] = useState<string | null>(null);
  const [demoRoleName, setDemoRoleName] = useState<string | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const handleDemoLogin = useCallback(
    async (index: number) => {
      setSelectedDemo(index);
      const cred = demoCredentials[index];
      if (!cred) return;

      setDemoRoleName(cred.role);
      setDemoStatus("connecting");
      setDemoErrorMessage(null);
      setElapsedSeconds(0);
      setDemoModalOpen(true);
      setIsLoading(true);

      stopTimer();
      timerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);

      try {
        console.log(`🔐 Initiating ${cred.role} demo login with Render cold-start handler...`);
        await authLogin(cred.email, cred.password);
        stopTimer();
        setDemoStatus("success");

        setTimeout(() => {
          setDemoModalOpen(false);
          setIsLoading(false);
          toast.success(`Welcome, ${cred.role}!`, {
            icon: React.createElement(CheckCircle2, { className: "size-4" }),
          });
          if (onSuccessCallback) {
            onSuccessCallback();
          }
        }, 500);
      } catch (error) {
        stopTimer();
        setDemoStatus("error");
        console.error(`❌ Demo login error for ${cred.role}:`, error);
        const msg =
          error instanceof Error
            ? error.message
            : `Login failed for ${cred.role}. Please verify backend status.`;
        setDemoErrorMessage(msg);
        setIsLoading(false);
      }
    },
    [authLogin, demoCredentials, onSuccessCallback, stopTimer]
  );

  const handleCloseModal = useCallback(() => {
    stopTimer();
    setDemoModalOpen(false);
    setIsLoading(false);
    setSelectedDemo(null);
  }, [stopTimer]);

  const handleRetry = useCallback(() => {
    if (selectedDemo !== null) {
      handleDemoLogin(selectedDemo);
    }
  }, [handleDemoLogin, selectedDemo]);

  useEffect(() => {
    return () => {
      stopTimer();
    };
  }, [stopTimer]);

  return {
    isLoading,
    selectedDemo,
    setSelectedDemo,
    demoModalOpen,
    demoStatus,
    demoErrorMessage,
    demoRoleName,
    elapsedSeconds,
    handleDemoLogin,
    handleCloseModal,
    handleRetry,
  };
}
