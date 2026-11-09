import { useState } from "react";
import * as api from "./api.js";
import Results from "./Results.jsx";

export default function AnalyzePage({ user }) {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function run(e) {
    e.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.upload(file));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="card">
        <h2>Analyze a pulse recording</h2>
        <p className="muted">
          Upload a CSV with the columns <code>time_s</code> and <code>ch1</code>. The recording must be 10 to 300
          seconds long, sampled at 50 to 1000 Hz.
        </p>
        <form onSubmit={run} className="inline">
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0] || null)} />
          <button type="submit" disabled={!file || busy}>
            {busy ? "Analyzing…" : "Analyze"}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>

      {result && (
        <>
          {result.saved && <p className="notice">Saved to your history (analysis #{result.id}).</p>}
          {!result.saved && user && (
            <p className="warn">Not saved. Your session may have expired, so please log out and log in again.</p>
          )}
          {!user && <p className="notice">Log in to save analyses to your history.</p>}
          <Results result={result} />
        </>
      )}
    </div>
  );
}