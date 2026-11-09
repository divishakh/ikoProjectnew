import { useCallback, useEffect, useState } from "react";
import * as api from "./api.js";
import AnalyzePage from "./AnalyzePage.jsx";
import AuthPage from "./AuthPage.jsx";
import HistoryPage from "./HistoryPage.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(() => Boolean(api.getToken()));
  const [view, setView] = useState("analyze");

  useEffect(() => {
    if (!api.getToken()) return;
    let cancelled = false;
    api
      .me()
      .then((u) => {
        if (!cancelled) setUser({ email: u.email });
      })
      .catch((err) => {
        if (err.status === 401) api.setToken(null);
      })
      .finally(() => {
        if (!cancelled) setChecking(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const expireSession = useCallback(() => {
    api.setToken(null);
    setUser(null);
    setView("login");
  }, []);

  async function logout() {
    try {
      await api.logout();
    } catch {
      /* server unreachable: still log out locally */
    }
    api.setToken(null);
    setUser(null);
    setView("analyze");
  }

  if (checking) return <p className="muted center">Loading…</p>;

  const onAuth = (email) => {
    setUser({ email });
    setView((v) => (v === "login" ? "analyze" : v));
  };

  return (
    <div className="app">
      <header>
        <h1>PRAKRITI AI</h1>
        <nav>
          <button type="button" className={view === "analyze" ? "tab active" : "tab"} onClick={() => setView("analyze")}>
            Analyze
          </button>
          <button type="button" className={view === "history" ? "tab active" : "tab"} onClick={() => setView("history")}>
            History
          </button>
        </nav>
        <div className="account">
          {user ? (
            <>
              <span className="muted">{user.email}</span>
              <button type="button" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <button type="button" onClick={() => setView("login")}>
              Log in
            </button>
          )}
        </div>
      </header>

      <main>
        {view === "analyze" && <AnalyzePage user={user} />}
        {view === "history" && (user ? <HistoryPage onAuthExpired={expireSession} /> : <AuthPage onSuccess={onAuth} />)}
        {view === "login" && <AuthPage onSuccess={onAuth} />}
      </main>
    </div>
  );
}