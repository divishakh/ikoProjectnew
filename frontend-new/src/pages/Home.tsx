import { motion } from "framer-motion";
import { Link } from "react-router-dom";

const PULSE =
  "M0 100 L120 100 L150 96 L175 70 L200 96 L260 100 L300 100 L315 108 L335 20 L360 170 L380 100 L440 100 L470 92 L510 62 L550 92 L600 100 L720 100 L750 96 L775 70 L800 96 L860 100 L900 100 L915 108 L935 20 L960 170 L980 100 L1040 100 L1070 92 L1110 62 L1150 92 L1200 100";

const STEPS = [0, 1, 2, 3, 4, 5, 6];

function Scene() {
  return (
    <svg
      className="absolute inset-0 h-full w-full"
      viewBox="0 0 1600 900"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="wall" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#f5d8dd" />
          <stop offset="1" stopColor="#e8c0cd" />
        </linearGradient>
        <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#dcd0e8" />
          <stop offset="1" stopColor="#c4b3da" />
        </linearGradient>
        <linearGradient id="step" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f7e4e4" />
          <stop offset="1" stopColor="#e6c6cb" />
        </linearGradient>
        <radialGradient id="pearl" cx="0.35" cy="0.3" r="0.85">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset="0.6" stopColor="#efe4f4" />
          <stop offset="1" stopColor="#c8b5e0" />
        </radialGradient>
      </defs>

      <rect width="1600" height="900" fill="url(#wall)" />
      <path d="M110 660 V320 A160 160 0 0 1 430 320 V660 Z" fill="#d6c3e8" />
      <path d="M110 560 Q270 470 430 540 V660 H110 Z" fill="#b99bd8" opacity="0.8" />
      <rect x="1190" y="110" width="170" height="300" fill="#d3e5f6" />
      <rect x="1050" y="260" width="120" height="260" fill="#f9ecee" opacity="0.7" />
      <rect y="660" width="1600" height="240" fill="url(#water)" />
      <ellipse cx="800" cy="780" rx="420" ry="14" fill="#ffffff" opacity="0.25" />
      <ellipse cx="900" cy="830" rx="300" ry="10" fill="#ffffff" opacity="0.2" />

      {STEPS.map((i) => (
        <rect key={i} x={540 + i * 36} y={640 - i * 34} width={520 - i * 72} height="34" fill="url(#step)" />
      ))}

      <ellipse cx="1340" cy="650" rx="140" ry="78" fill="#d9b9b6" />
      <ellipse cx="1310" cy="625" rx="90" ry="40" fill="#e8cfcb" opacity="0.7" />

      <motion.circle
        cx="1010"
        cy="330"
        r="72"
        fill="url(#pearl)"
        animate={{ cy: [330, 315, 330] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      />
    </svg>
  );
}

export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 text-center">
      <Scene />

      <svg viewBox="0 0 1200 200" className="pointer-events-none absolute left-0 top-1/2 w-full -translate-y-1/2 opacity-30" fill="none">
        <motion.path
          d={PULSE}
          stroke="#26232b"
          strokeWidth="1.5"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear", repeatDelay: 0.6 }}
        />
      </svg>

      <motion.div
        className="relative z-10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <p className="mb-6 text-[11px] font-light uppercase tracking-[0.3em] text-ink/70">
          Pulse analysis, through Ayurveda
        </p>
        <h1 className="leading-[0.95]">
          <span className="block font-display text-7xl italic md:text-9xl">Reading the</span>
          <span className="block text-6xl font-light tracking-tighter md:text-8xl">pulse</span>
        </h1>
        <Link
          to="/analyze"
          className="mt-10 inline-block rounded-full bg-white px-6 py-2.5 text-sm font-medium shadow-sm transition-transform hover:scale-105 active:scale-95"
        >
          Start analysis ↘
        </Link>
      </motion.div>

      <div className="absolute bottom-6 left-6 right-6 z-10 flex items-center justify-between md:left-10 md:right-10">
        <div className="flex items-center gap-3">
          <Link to="/technology" aria-label="Technology" className="flex h-10 w-10 items-center justify-center gap-0.5 rounded-full bg-white transition-transform hover:scale-110 active:scale-90">
            <span className="h-3 w-0.5 bg-ink" />
            <span className="h-4 w-0.5 bg-ink" />
            <span className="h-2 w-0.5 bg-ink" />
          </Link>
          <Link to="/technology" className="rounded-full border border-white px-5 py-2 text-xs text-white transition-colors hover:bg-white hover:text-ink">
            How it works
          </Link>
        </div>
        <Link to="/ayurveda" aria-label="Ayurveda" className="flex h-10 w-10 items-center justify-center rounded-full bg-white transition-transform hover:scale-110 active:scale-90">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#26232b" strokeWidth="1.5">
            <circle cx="12" cy="12" r="9" />
            <ellipse cx="12" cy="12" rx="4" ry="9" />
            <path d="M3 12h18" />
          </svg>
        </Link>
        <span className="text-xs text-white">©2026</span>
      </div>
    </main>
  );
}