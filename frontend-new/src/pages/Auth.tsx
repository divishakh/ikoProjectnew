import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../api";
import { useAuth } from "../authContext";

export default function Auth() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = mode === "login" ? await api.login(email, password) : await api.register(email, password);
      signIn(res.access_token, res.email);
      navigate("/analyze");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  const field =
    "w-full rounded-full border border-ink/15 bg-ivory px-5 py-3 text-sm outline-none transition-colors focus:border-ink/50";

  return (
    <main className="flex min-h-screen items-center justify-center bg-ivory px-6">
      <form onSubmit={submit} className="w-full max-w-sm rounded-3xl bg-white p-8 shadow-sm">
        <h1 className="font-display text-5xl italic">{mode === "login" ? "Welcome back" : "Create account"}</h1>
        <p className="mt-2 text-sm font-light text-ink/60">
          {mode === "login" ? "Log in to save and review your analyses." : "Your analyses are saved to your account."}
        </p>

        <div className="mt-8 flex flex-col gap-3">
          <input
            type="email"
            required
            placeholder="Email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={field}
          />
          <input
            type="password"
            required
            minLength={8}
            placeholder="Password (8 or more characters)"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={field}
          />
        </div>

        {error && <p className="mt-4 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

        <button
          type="submit"
          disabled={busy}
          className="mt-6 w-full rounded-full bg-ink py-3 text-sm font-medium text-ivory transition-transform hover:scale-[1.02] active:scale-95 disabled:opacity-50"
        >
          {busy ? "Please wait…" : mode === "login" ? "Log in ↘" : "Create account ↘"}
        </button>

        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
          className="mt-4 w-full text-center text-xs text-ink/60 underline"
        >
          {mode === "login" ? "New here? Create an account" : "Already have an account? Log in"}
        </button>
      </form>
    </main>
  );
}