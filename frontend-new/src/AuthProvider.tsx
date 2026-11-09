import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import * as api from "./api";
import { AuthContext } from "./authContext";

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null);
  const [checking, setChecking] = useState(() => api.getToken() !== null);

  useEffect(() => {
    if (!api.getToken()) return;
    let cancelled = false;
    api
      .me()
      .then((u) => {
        if (!cancelled) setEmail(u.email);
      })
      .catch((err) => {
        if (err instanceof api.ApiError && err.status === 401) api.setToken(null);
      })
      .finally(() => {
        if (!cancelled) setChecking(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback((token: string, userEmail: string) => {
    api.setToken(token);
    setEmail(userEmail);
  }, []);

  const signOut = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      /* server unreachable: still log out locally */
    }
    api.setToken(null);
    setEmail(null);
  }, []);

  const value = useMemo(() => ({ email, checking, signIn, signOut }), [email, checking, signIn, signOut]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}