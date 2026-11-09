import { useState } from "react";
import * as api from "./api.js";

export default function AuthPage({ onSuccess }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const fn = mode === "login" ? api.login : api.register;
      const data = await fn(email, password);
      api.setToken(data.access_token);
      onSuccess(data.email);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card narrow">
      <h2>{mode === "login" ? "Log in" : "Create an account"}</h2>
      <form onSubmit={submit}>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
        </label>
        <label>
          Password {mode === "register" && <span className="muted">(8 to 128 characters)</span>}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={busy}>
          {busy ? "Please wait…" : mode === "login" ? "Log in" : "Register"}
        </button>
      </form>
      <p className="muted">
        {mode === "login" ? "No account yet? " : "Already registered? "}
        <button
          type="button"
          className="link"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError("");
          }}
        >
          {mode === "login" ? "Register" : "Log in"}
        </button>
      </p>
    </div>
  );
}