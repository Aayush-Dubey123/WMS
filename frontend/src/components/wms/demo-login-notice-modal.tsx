import React from "react";
import {
  Server,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  X,
  Clock,
  Sparkles,
  RefreshCw,
} from "lucide-react";

export interface DemoLoginNoticeModalProps {
  isOpen: boolean;
  onClose: () => void;
  roleName: string | null;
  status: "connecting" | "success" | "error";
  errorMessage?: string | null;
  onRetry?: () => void;
  elapsedSeconds: number;
}

export const DemoLoginNoticeModal: React.FC<DemoLoginNoticeModalProps> = ({
  isOpen,
  onClose,
  roleName,
  status,
  errorMessage,
  onRetry,
  elapsedSeconds,
}) => {
  if (!isOpen) return null;

  // Calculate estimated progress percentage for cold start (caps at 95% while waiting)
  const progressPercent = Math.min(95, Math.round((elapsedSeconds / 45) * 100));

  const getStatusCaption = () => {
    if (elapsedSeconds < 4) {
      return "Contacting demo backend server...";
    } else if (elapsedSeconds < 15) {
      return "Render server waking up from free-tier sleep state...";
    } else if (elapsedSeconds < 35) {
      return "Cold start in progress. Booting database and app containers (may take up to a minute)...";
    } else {
      return "Almost ready! Finalizing server startup...";
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        backgroundColor: "rgba(15, 15, 15, 0.65)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        animation: "fadeIn 0.2s ease-out",
      }}
    >
      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "480px",
          backgroundColor: "var(--wf-card, #ffffff)",
          borderRadius: "20px",
          border: "1px solid var(--wf-border, #E8E0D4)",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(212, 116, 11, 0.08)",
          padding: "28px 24px",
          boxSizing: "border-box",
          fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
          color: "var(--wf-dark, #1A1A1A)",
        }}
      >
        {/* Close button (top right) */}
        <button
          onClick={onClose}
          type="button"
          aria-label="Close dialog"
          style={{
            position: "absolute",
            top: "16px",
            right: "16px",
            background: "none",
            border: "none",
            color: "var(--wf-muted, #7A7A6E)",
            cursor: "pointer",
            padding: "6px",
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "all 0.15s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "var(--wf-cream, #FAF6F0)";
            e.currentTarget.style.color = "var(--wf-dark, #1A1A1A)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "transparent";
            e.currentTarget.style.color = "var(--wf-muted, #7A7A6E)";
          }}
        >
          <X size={18} />
        </button>

        {/* Top Render Free Badge */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            padding: "4px 12px",
            borderRadius: "20px",
            backgroundColor: "var(--wf-orange-pale, #FFF4E6)",
            border: "1px solid rgba(212, 116, 11, 0.2)",
            color: "var(--wf-orange, #D4740B)",
            fontSize: "12px",
            fontWeight: 700,
            marginBottom: "16px",
          }}
        >
          <Server size={14} className={status === "connecting" ? "animate-pulse" : ""} />
          <span>Render Free Tier Demo Host</span>
        </div>

        {/* Title & Role Info */}
        <h3
          style={{
            fontSize: "20px",
            fontWeight: 800,
            color: "var(--wf-dark, #1A1A1A)",
            margin: "0 0 6px 0",
            letterSpacing: "-0.01em",
          }}
        >
          Demo Server Startup Notice
        </h3>

        {roleName && (
          <div
            style={{
              fontSize: "13px",
              color: "var(--wf-muted, #7A7A6E)",
              marginBottom: "16px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <span>Logging in as demo role:</span>
            <span
              style={{
                backgroundColor: "var(--wf-orange, #D4740B)",
                color: "#ffffff",
                padding: "2px 8px",
                borderRadius: "12px",
                fontSize: "11px",
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              {roleName}
            </span>
          </div>
        )}

        {/* Core Explanatory Message Box */}
        <div
          style={{
            backgroundColor: "var(--wf-cream, #FAF6F0)",
            border: "1px solid var(--wf-border, #E8E0D4)",
            borderRadius: "14px",
            padding: "16px",
            marginBottom: "20px",
            fontSize: "13.5px",
            lineHeight: 1.55,
            color: "var(--wf-dark-secondary, #4A4A4A)",
          }}
        >
          <p style={{ margin: "0 0 8px 0", fontWeight: 700, color: "var(--wf-dark, #1A1A1A)" }}>
            Thank you for visiting!
          </p>
          <p style={{ margin: 0 }}>
            Our demo backend is hosted on Render Free and may need a short cold-start period after inactivity. You'll be redirected shortly. Please be patient while the server starts (may take up to a minute if cold).
          </p>
        </div>

        {/* Dynamic Status Section */}
        {status === "connecting" && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "12px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "13px",
                fontWeight: 600,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--wf-orange, #D4740B)" }}>
                <Loader2 size={16} className="animate-spin" />
                <span>Please wait... Starting server</span>
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "12px",
                  color: "var(--wf-muted, #7A7A6E)",
                  fontVariantNumeric: "tabular-nums",
                }}
              >
                <Clock size={12} />
                <span>Elapsed: {elapsedSeconds}s</span>
              </div>
            </div>

            {/* Progress Bar Container */}
            <div
              style={{
                width: "100%",
                height: "6px",
                backgroundColor: "var(--wf-border, #E8E0D4)",
                borderRadius: "3px",
                overflow: "hidden",
                position: "relative",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progressPercent}%`,
                  backgroundColor: "var(--wf-orange, #D4740B)",
                  borderRadius: "3px",
                  transition: "width 1s linear",
                }}
              />
            </div>

            <p
              style={{
                fontSize: "12px",
                color: "var(--wf-muted, #7A7A6E)",
                margin: 0,
                fontStyle: "italic",
              }}
            >
              {getStatusCaption()}
            </p>
          </div>
        )}

        {status === "success" && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "12px 14px",
              backgroundColor: "var(--wf-green-light, #E8F5E9)",
              border: "1px solid rgba(46, 125, 50, 0.2)",
              borderRadius: "12px",
              color: "var(--wf-green, #2E7D32)",
              fontSize: "13px",
              fontWeight: 600,
            }}
          >
            <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
            <span>Backend server connected! Redirecting to workspace...</span>
          </div>
        )}

        {status === "error" && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "14px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "10px",
                padding: "14px",
                backgroundColor: "#FEF2F2",
                border: "1px solid #FCA5A5",
                borderRadius: "12px",
                color: "#991B1B",
                fontSize: "13px",
              }}
            >
              <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                <p style={{ margin: "0 0 4px 0", fontWeight: 700 }}>
                  Connection Failed
                </p>
                <p style={{ margin: 0, fontSize: "12.5px" }}>
                  {errorMessage || "Unable to reach the backend server. The service might be temporarily offline or experiencing issues."}
                </p>
              </div>
            </div>

            <div
              style={{
                display: "flex",
                gap: "10px",
                justifyContent: "flex-end",
                marginTop: "4px",
              }}
            >
              <button
                type="button"
                onClick={onClose}
                style={{
                  padding: "8px 16px",
                  borderRadius: "10px",
                  border: "1px solid var(--wf-border, #E8E0D4)",
                  backgroundColor: "#ffffff",
                  color: "var(--wf-dark, #1A1A1A)",
                  fontSize: "13px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "8px 18px",
                    borderRadius: "10px",
                    border: "none",
                    backgroundColor: "var(--wf-orange, #D4740B)",
                    color: "#ffffff",
                    fontSize: "13px",
                    fontWeight: 700,
                    cursor: "pointer",
                    boxShadow: "var(--wf-shadow-sm)",
                  }}
                >
                  <RefreshCw size={14} />
                  <span>Retry Login</span>
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
