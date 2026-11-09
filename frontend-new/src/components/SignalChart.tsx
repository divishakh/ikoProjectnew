import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Props = {
  title: string;
  subtitle?: string;
  t: number[];
  y: number[];
  peaks?: number[];
  color?: string;
  syncId?: string;
  xDecimals?: number;
};

export default function SignalChart({
  title,
  subtitle,
  t,
  y,
  peaks = [],
  color = "#26232b",
  syncId,
  xDecimals = 0,
}: Props) {
  const data = t.map((x, i) => ({ t: x, v: y[i] }));
  return (
    <div className="rounded-3xl bg-white p-5 shadow-sm">
      <div className="mb-3">
        <h3 className="text-sm font-medium">{title}</h3>
        {subtitle && <p className="text-xs font-light text-ink/60">{subtitle}</p>}
      </div>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} syncId={syncId} margin={{ top: 5, right: 10, bottom: 18, left: 0 }}>
            <CartesianGrid stroke="#26232b" strokeOpacity={0.08} />
            <XAxis
              dataKey="t"
              type="number"
              domain={["dataMin", "dataMax"]}
              tick={{ fontSize: 11 }}
              tickFormatter={(v: number) => v.toFixed(xDecimals)}
              label={{ value: "Time (s)", position: "insideBottom", offset: -10, fontSize: 11 }}
            />
            <YAxis
              width={56}
              tick={{ fontSize: 11 }}
              tickFormatter={(v: number) => v.toFixed(1)}
              label={{ value: "Amplitude", angle: -90, position: "insideLeft", fontSize: 11 }}
            />
            <Tooltip
              formatter={(v) => Number(v).toFixed(3)}
              labelFormatter={(l) => `${Number(l).toFixed(2)} s`}
            />
            {peaks.map((p) => (
              <ReferenceLine key={p} x={p} stroke="#9bb09a" strokeOpacity={0.9} />
            ))}
            <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.4} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}