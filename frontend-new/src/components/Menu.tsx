import { AnimatePresence, motion } from "framer-motion";
import { Link, useLocation } from "react-router-dom";

const ITEMS = [
  { n: "01", label: "Home", to: "/" },
  { n: "02", label: "Analyze", to: "/analyze" },
  { n: "03", label: "History", to: "/history" },
  { n: "04", label: "Ayurveda", to: "/ayurveda" },
  { n: "05", label: "Technology", to: "/technology" },
  { n: "06", label: "Assistant", to: "/assistant" },
];

export default function Menu({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { pathname } = useLocation();
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-40 flex flex-col justify-center bg-ivory px-8 md:px-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          <button
            onClick={onClose}
            aria-label="Close menu"
            className="absolute right-6 top-6 flex h-12 w-12 items-center justify-center rounded-full bg-ink text-xl text-ivory transition-transform hover:scale-110 active:scale-90"
          >
            ×
          </button>
          <nav className="flex flex-col">
            {ITEMS.map((it, i) => {
              const current = pathname === it.to;
              return (
                <motion.div
                  key={it.to}
                  initial={{ opacity: 0, y: 24 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.05 * i + 0.1 }}
                >
                  <Link
                    to={it.to}
                    onClick={onClose}
                    className={`flex items-baseline gap-4 font-display text-5xl leading-tight transition-colors md:text-7xl ${
                      current ? "text-ink/30" : "text-ink hover:text-sage"
                    }`}
                  >
                    <span className="font-sans text-xs tracking-widest">{it.n}</span>
                    {it.label}
                  </Link>
                </motion.div>
              );
            })}
          </nav>
        </motion.div>
      )}
    </AnimatePresence>
  );
}