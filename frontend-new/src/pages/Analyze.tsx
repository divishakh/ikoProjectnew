import { useRef, useState } from "react";
import type { DragEvent } from "react";
import { Link } from "react-router-dom";
import * as api from "../api";
import type { AnalysisResult } from "../api";
import { useAuth } from "../authContext";
import AyurgenomicsCard from "../components/AyurgenomicsCard";
import SignalChart from "../components/SignalChart";

const MAX_BYTES = 20_000_000;

const FEATURES = [
  { key: "hr", label: "Heart rate", unit: "bpm", digits: 1, note: "60 divided by the average gap between beats." },
  { key: "amp", label: "Amplitude", unit: "sensor units", digits: 3, note: "Height of the pulse peak above the foot of the beat." },
  { key: "rise_s", label: "Rise time", unit: "s", digits: 3, note: "Time from the foot of the beat to its peak." },
  { key: "width_s", label: "Peak width", unit: "s", digits: 3, note: "Width of the main peak at half its height." },
  { key: "irregularity", label: "Irregularity", unit: "", digits: 4, note: "Spread of the gaps between beats, relative to their average." },
];

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-ivory px-4 py-3">
      <p className="text-[11px] font-light uppercase tracking-widest text-ink/60">{label}</p>
      <p className="mt-1 text-lg font-medium">{value}</p>
    </div>
  );
}

export default function Analyze() {
  const { email } = useAuth();
  const input = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [over, setOver] = useState(false);

  function pick(f: File | undefined) {
    setResult(null);
    setError(null);
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".csv")) {
      setFile(null);
      setError("Please choose a .csv file.");
      return;
    }
    if (f.size > MAX_BYTES) {
      setFile(null);
      setError("The file is too large (20 MB maximum).");
      return;
    }
    setFile(f);
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setOver(false);
    pick(e.dataTransfer.files[0]);
  }

  async function run() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.uploadRecording(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  const pred = result?.prediction;

  return (
    <main className="min-h-screen bg-ivory px-6 pb-24 pt-28 md:px-10">
      <div className="mx-auto max-w-5xl">
        <h1 className="font-display text-6xl italic md:text-7xl">Analyze a pulse</h1>
        <p className="mt-3 max-w-xl text-sm font-light text-ink/70">
          Upload a recording. Your own signal-processing code filters it, finds each heartbeat, checks its quality and
          measures the pulse features.
        </p>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setOver(true);
          }}
          onDragLeave={() => setOver(false)}
          onDrop={onDrop}
          className={`mt-8 rounded-3xl border border-dashed p-8 text-center transition-colors ${
            over ? "border-ink bg-white" : "border-ink/30 bg-white/60"
          }`}
        >
          <input
            ref={input}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => pick(e.target.files?.[0])}
          />
          <p className="text-sm">{file ? file.name : "Drop a .csv file here"}</p>
          <p className="mx-auto mt-2 max-w-md text-xs font-light text-ink/60">
            Needs the columns <b>time_s</b> and <b>ch1</b>. Length 10 to 300 s, sampling rate 50 to 1000 Hz, up to 20 MB.
          </p>
          <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={() => input.current?.click()}
              className="rounded-full border border-ink/40 px-6 py-2.5 text-sm transition-colors hover:bg-ink hover:text-ivory"
            >
              Choose file
            </button>
            <button
              onClick={() => void run()}
              disabled={!file || busy}
              className="rounded-full bg-ink px-6 py-2.5 text-sm font-medium text-ivory transition-transform hover:scale-105 active:scale-95 disabled:opacity-40"
            >
              {busy ? "Analysing…" : "Analyze ↘"}
            </button>
          </div>
        </div>

        {error && <p className="mt-4 rounded-2xl bg-red-50 px-5 py-3 text-sm text-red-700">{error}</p>}

        {result && pred && (
          <section className="mt-10 flex flex-col gap-6">
            <div className="flex flex-wrap items-center gap-3">
              <span
                className={`rounded-full px-4 py-1.5 text-xs font-medium ${
                  result.quality.ok ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
                }`}
              >
                {result.quality.ok ? "Good quality" : "Low quality: please re-record"}
              </span>
              <span className="text-xs font-light text-ink/60">
                {result.saved ? "Saved to your history." : null}
                {!result.saved && !email ? (
                  <>
                    Not saved. <Link to="/login" className="underline">Log in</Link> to keep your analyses.
                  </>
                ) : null}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <Stat label="Sampling rate" value={`${result.recording.sampling_hz} Hz`} />
              <Stat label="Duration" value={`${result.recording.duration_s} s`} />
              <Stat label="Beats found" value={String(result.quality.beats_found)} />
              <Stat
                label="Beats kept"
                value={`${result.quality.beats_kept} (${Math.round(result.quality.kept_fraction * 100)}%)`}
              />
            </div>
            <p className="text-xs font-light text-ink/60">Rule for good quality: {result.quality.rule}.</p>

            <div className="flex flex-col gap-4">
              <SignalChart
                title="Raw signal"
                subtitle={`Channel ${result.recording.channel}, first 10 seconds, as recorded.`}
                t={result.signal.t}
                y={result.signal.raw}
                color="#8a8591"
                syncId="pulse"
              />
              <SignalChart
                title="Filtered signal"
                subtitle="After the band-pass filter. Green lines mark the detected beats."
                t={result.signal.t}
                y={result.signal.filtered}
                peaks={result.signal.peaks_t}
                syncId="pulse"
              />
            </div>

            <div className="rounded-3xl bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium">Filter used</h2>
              <p className="mt-2 text-sm font-light text-ink/80">
                {result.filter.type}, order {result.filter.order}, passing {result.filter.low_hz} to {result.filter.high_hz}{" "}
                Hz. Applied {result.filter.zero_phase ? "forwards and backwards (zero phase)" : "forwards"} with{" "}
                {result.filter.method}.
              </p>
            </div>

            {result.median_beat && (
              <SignalChart
                title="Typical beat"
                subtitle="The median of the kept beats, aligned on the peak at time 0."
                t={result.median_beat.t}
                y={result.median_beat.y}
                xDecimals={1}
              />
            )}

            {result.features && (
              <div className="rounded-3xl bg-white p-6 shadow-sm">
                <h2 className="text-sm font-medium">Pulse features</h2>
                <p className="mt-1 text-xs font-light text-ink/60">Averages across the kept beats.</p>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {FEATURES.map((f) => (
                    <div key={f.key} className="rounded-2xl bg-ivory px-4 py-3">
                      <div className="flex items-baseline justify-between">
                        <span className="text-sm">{f.label}</span>
                        <span className="text-lg font-medium">
                          {result.features?.[f.key]?.toFixed(f.digits) ?? "n/a"}
                          <span className="ml-1 text-xs font-light text-ink/60">{f.unit}</span>
                        </span>
                      </div>
                      <p className="mt-1 text-xs font-light text-ink/60">{f.note}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="rounded-3xl bg-white p-6 shadow-sm">
              <h2 className="text-sm font-medium">Prakriti estimate</h2>
              {pred.mode === "trained" && pred.classes && pred.probabilities ? (
                <div className="mt-3">
                  <p className="text-sm">
                    Model output: <b>{pred.label}</b>
                  </p>
                  {pred.warning && <p className="mt-2 text-xs font-light text-amber-700">{pred.warning}</p>}
                  <div className="mt-3 flex flex-col gap-2">
                    {pred.classes.map((c, i) => (
                      <div key={c} className="flex items-center gap-3 text-xs">
                        <span className="w-20">{c}</span>
                        <div className="h-2 flex-1 rounded-full bg-ivory">
                          <div className="h-2 rounded-full bg-sage" style={{ width: `${(pred.probabilities?.[i] ?? 0) * 100}%` }} />
                        </div>
                        <span className="w-12 text-right">{((pred.probabilities?.[i] ?? 0) * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-sm font-light text-ink/80">{pred.message}</p>
              )}
              <p className="mt-4 text-xs font-light text-ink/50">
                Experimental research software. Not a medical diagnosis and not a substitute for qualified medical or
                Ayurvedic advice.
              </p>
            </div>
            <AyurgenomicsCard
              key={`${result.filename}-${pred.label ?? "none"}-${result.id ?? ""}`}
              predicted={pred.mode === "trained" ? pred.label : undefined}
              demo={Boolean(pred.warning)}
              initial={result.ayurgenomics}
            />
          </section>
        )}
      </div>
    </main>
  );
}