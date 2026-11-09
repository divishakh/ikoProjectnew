import { useMemo } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const FEATURES = {
  hr: ["Heart rate", "bpm"],
  amp: ["Pulse amplitude", "a.u."],
  rise_s: ["Rise time", "s"],
  width_s: ["Pulse width", "s"],
  irregularity: ["Beat-to-beat irregularity", ""],
};

const fmt = (v, d = 2) => (typeof v === "number" ? v.toFixed(d) : "–");

function Chart({ title, data, xKey, yKey, color, xLabel, xDigits = 1, peaks = [], dots = false }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 8, right: 12, bottom: 18, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis
              type="number"
              dataKey={xKey}
              domain={["dataMin", "dataMax"]}
              tickFormatter={(v) => fmt(v, xDigits)}
              label={{ value: xLabel, position: "insideBottom", offset: -8 }}
            />
            <YAxis width={48} domain={["auto", "auto"]} tickFormatter={(v) => fmt(v, 2)} />
            <Tooltip
              formatter={(v) => fmt(v, 3)}
              labelFormatter={(v) => `${xLabel}: ${fmt(v, xDigits === 0 ? 0 : 3)}`}
            />
            {peaks.map((p) => (
              <ReferenceLine key={p} x={p} stroke="#e5484d" strokeDasharray="4 3" />
            ))}
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={color}
              dot={dots}
              strokeWidth={1.6}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Prediction({ prediction, qualityOk }) {
  if (prediction.mode !== "trained") {
    return <p className="muted">{prediction.message}</p>;
  }
  return (
    <div>
      <p>
        Most likely class: <strong>{prediction.label}</strong>
      </p>
      {prediction.classes.map((c, i) => (
        <div className="bar-row" key={c}>
          <span className="bar-label">{c}</span>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${prediction.probabilities[i] * 100}%` }} />
          </div>
          <span className="bar-value">{(prediction.probabilities[i] * 100).toFixed(1)}%</span>
        </div>
      ))}
      {!qualityOk && (
        <p className="warn">The signal quality was low, so treat this result with caution.</p>
      )}
    </div>
  );
}

export default function Results({ result }) {
  const sig = result.signal;
  const intervals = result.beat_intervals_s;

  const sigData = useMemo(
    () => sig.t.map((t, i) => ({ t, raw: sig.raw[i], filtered: sig.filtered[i] })),
    [sig],
  );
  const beatData = useMemo(
    () => (result.median_beat ? result.median_beat.t.map((t, i) => ({ t, y: result.median_beat.y[i] })) : null),
    [result.median_beat],
  );
  const intData = useMemo(() => intervals.map((s, i) => ({ n: i + 1, s })), [intervals]);
  const longCount = useMemo(() => {
    if (intervals.length < 3) return 0;
    const sorted = [...intervals].sort((a, b) => a - b);
    const med = sorted[Math.floor(sorted.length / 2)];
    return intervals.filter((v) => v > 1.5 * med).length;
  }, [intervals]);

  const rec = result.recording;
  const q = result.quality;
  const f = result.filter;

  return (
    <div className="results">
      <div className="grid">
        <div className="card">
          <h3>Recording</h3>
          <dl>
            <dt>File</dt>
            <dd>{result.filename}</dd>
            <dt>Sampling rate</dt>
            <dd>{rec.sampling_hz} Hz</dd>
            <dt>Duration</dt>
            <dd>{rec.duration_s} s</dd>
            <dt>Samples</dt>
            <dd>{rec.samples}</dd>
            <dt>Filter</dt>
            <dd>
              {f.type}, order {f.order}, {f.low_hz}–{f.high_hz} Hz, zero-phase ({f.method})
            </dd>
          </dl>
        </div>

        <div className="card">
          <h3>
            Signal quality <span className={q.ok ? "badge ok" : "badge bad"}>{q.ok ? "Good" : "Too low"}</span>
          </h3>
          <dl>
            <dt>Beats found</dt>
            <dd>{q.beats_found}</dd>
            <dt>Beats kept</dt>
            <dd>
              {q.beats_kept} ({(q.kept_fraction * 100).toFixed(1)}%)
            </dd>
            <dt>Rule</dt>
            <dd>{q.rule}</dd>
          </dl>
          {!q.ok && <p className="warn">This recording does not meet the quality rule, so results are unreliable.</p>}
        </div>

        <div className="card">
          <h3>Features (average over kept beats)</h3>
          {result.features ? (
            <dl>
              {Object.entries(result.features).map(([k, v]) => (
                <div className="row" key={k}>
                  <dt>{(FEATURES[k] || [k])[0]}</dt>
                  <dd>
                    {fmt(v, 3)} {(FEATURES[k] || ["", ""])[1]}
                  </dd>
                </div>
              ))}
            </dl>
          ) : (
            <p className="muted">Too few clean beats to compute features.</p>
          )}
        </div>

        <div className="card">
          <h3>Prediction</h3>
          <Prediction prediction={result.prediction} qualityOk={q.ok} />
        </div>
      </div>

      <Chart title="Raw signal (first 10 s)" data={sigData} xKey="t" yKey="raw" color="#8b8f98" xLabel="Time (s)" />
      <Chart
        title="Filtered signal with detected beats (first 10 s)"
        data={sigData}
        xKey="t"
        yKey="filtered"
        color="#3b6ef5"
        xLabel="Time (s)"
        peaks={sig.peaks_t}
      />
      {beatData && (
        <Chart title="Median beat shape" data={beatData} xKey="t" yKey="y" color="#1a9a6b" xLabel="Time from peak (s)" />
      )}
      {intData.length > 0 && (
        <div>
          <Chart
            title="Beat-to-beat intervals (whole recording)"
            data={intData}
            xKey="n"
            yKey="s"
            color="#b5651d"
            xLabel="Beat number"
            xDigits={0}
            dots
          />
          {longCount > 0 && (
            <p className="warn">
              {longCount} interval{longCount > 1 ? "s are" : " is"} much longer than typical. A beat may have been
              missed by the detector, which inflates the irregularity feature.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
