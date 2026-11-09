import { useCallback, useEffect, useState } from "react";
import * as api from "./api.js";
import Results from "./Results.jsx";

const MODE_LABEL = { no_model: "No model yet", no_prediction: "Too few beats", trained: "Predicted" };

export default function HistoryPage({ onAuthExpired }) {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(null);
  const [busyId, setBusyId] = useState(null);

  const handleError = useCallback(
    (err) => {
      if (err.status === 401) onAuthExpired();
      else setError(err.message);
    },
    [onAuthExpired],
  );

  useEffect(() => {
    let cancelled = false;
    api
      .listAnalyses()
      .then((d) => {
        if (!cancelled) setItems(d);
      })
      .catch((err) => {
        if (!cancelled) handleError(err);
      });
    return () => {
      cancelled = true;
    };
  }, [handleError]);

  async function view(id) {
    setBusyId(id);
    setError("");
    try {
      setOpen(await api.getAnalysis(id));
    } catch (err) {
      handleError(err);
    } finally {
      setBusyId(null);
    }
  }

  async function remove(id) {
    if (!window.confirm("Delete this analysis permanently?")) return;
    setError("");
    try {
      await api.deleteAnalysis(id);
      setItems((list) => list.filter((x) => x.id !== id));
      setOpen((o) => (o && o.id === id ? null : o));
    } catch (err) {
      handleError(err);
    }
  }

  if (open) {
    return (
      <div>
        <button type="button" onClick={() => setOpen(null)}>
          ← Back to history
        </button>
        <Results result={open} />
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Your saved analyses</h2>
      {error && <p className="error">{error}</p>}
      {items === null && !error && <p className="muted">Loading…</p>}
      {items && items.length === 0 && <p className="muted">Nothing saved yet. Upload a recording while logged in.</p>}
      {items && items.length > 0 && (
        <div className="scroll">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>File</th>
                <th>Duration</th>
                <th>Beats kept</th>
                <th>Quality</th>
                <th>HR (bpm)</th>
                <th>Prediction</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.id}>
                  <td>{new Date(it.created_at).toLocaleString()}</td>
                  <td>{it.filename}</td>
                  <td>{it.duration_s} s</td>
                  <td>{it.beats_kept}</td>
                  <td>
                    <span className={it.quality_ok ? "badge ok" : "badge bad"}>{it.quality_ok ? "Good" : "Low"}</span>
                  </td>
                  <td>{typeof it.hr === "number" ? it.hr.toFixed(1) : "–"}</td>
                  <td>{MODE_LABEL[it.prediction_mode] || it.prediction_mode}</td>
                  <td className="actions">
                    <button type="button" onClick={() => view(it.id)} disabled={busyId === it.id}>
                      {busyId === it.id ? "Opening…" : "Open"}
                    </button>
                    <button type="button" className="danger" onClick={() => remove(it.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}