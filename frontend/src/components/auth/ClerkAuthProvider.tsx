import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { ClerkProvider } from "@clerk/react";

const appearance = {
  variables: {
    colorPrimary: "#3b82f6",
    colorPrimaryForeground: "#ffffff",
    colorBackground: "#12161f",
    colorForeground: "#f4f6fb",
    colorInput: "#171d29",
    colorInputForeground: "#f4f6fb",
    colorBorder: "rgba(255,255,255,0.12)",
    fontFamily: "DM Sans, sans-serif",
    borderRadius: "0.75rem",
  },
};

interface ClerkConfig {
  enabled: boolean;
  publishable_key: string;
  proxy_url: string;
}

export default function ClerkAuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [config, setConfig] = useState<ClerkConfig | null>(null);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async (attempt = 0) => {
      try {
        const response = await fetch("/api/clerk/config");
        const nextConfig = (await response.json()) as ClerkConfig;
        if (nextConfig.enabled) {
          if (!cancelled) setConfig(nextConfig);
          return;
        }
      } catch {
        // Retry while the backend is restarting.
      }
      if (cancelled) return;
      if (attempt >= 20) {
        setUnavailable(true);
        return;
      }
      window.setTimeout(() => void load(attempt + 1), 1500);
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (unavailable) {
    return <div className="p-6 text-sm text-slate-300" data-testid="auth-unavailable-message">Sign-in is unavailable right now. The course preview remains available after refresh.</div>;
  }
  if (!config) return <div className="min-h-svh bg-[#0b0d11]" data-testid="auth-loading-shell" />;

  return (
    <ClerkProvider
      publishableKey={config.publishable_key}
      proxyUrl={config.proxy_url || undefined}
      appearance={appearance}
      routerPush={(to) => navigate(to)}
      routerReplace={(to) => navigate(to, { replace: true })}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      signInFallbackRedirectUrl="/"
      signUpFallbackRedirectUrl="/"
      afterSignOutUrl="/"
    >
      {children}
    </ClerkProvider>
  );
}