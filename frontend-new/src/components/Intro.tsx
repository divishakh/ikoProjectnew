import { motion } from "framer-motion";

const WORD = "PRAKRITI AI".split("");

export default function Intro({ onEnter }: { onEnter: () => void }) {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-8 bg-blush px-6 text-center"
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h1 className="font-display text-6xl tracking-tight md:text-8xl">
        {WORD.map((c, i) => (
          <motion.span
            key={i}
            className="inline-block"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.07, duration: 0.5 }}
          >
            {c === " " ? "\u00A0" : c}
          </motion.span>
        ))}
      </h1>
      <motion.p
        className="max-w-md text-sm font-light text-ink/70"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4 }}
      >
        Pulse analysis through the lens of Ayurveda, read by signal processing and machine learning.
      </motion.p>
      <motion.button
        onClick={onEnter}
        className="rounded-full bg-ink px-8 py-3 text-sm font-medium text-ivory transition-transform hover:scale-105 active:scale-95"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.7 }}
      >
        Enter ↘
      </motion.button>
    </motion.div>
  );
}