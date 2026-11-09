import { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

export default function Cursor() {
  const x = useMotionValue(-100);
  const y = useMotionValue(-100);
  const sx = useSpring(x, { stiffness: 500, damping: 40 });
  const sy = useSpring(y, { stiffness: 500, damping: 40 });
  const [hover, setHover] = useState(false);
  const [fine] = useState(() => window.matchMedia("(pointer: fine)").matches);

  useEffect(() => {
    if (!fine) return;
    const move = (e: MouseEvent) => {
      x.set(e.clientX);
      y.set(e.clientY);
      setHover(!!(e.target as HTMLElement).closest("a,button"));
    };
    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, [fine, x, y]);

  if (!fine) return null;
  return (
    <motion.div
      className="pointer-events-none fixed left-0 top-0 z-[100] rounded-full border border-ink"
      style={{ x: sx, y: sy, translateX: "-50%", translateY: "-50%" }}
      animate={{
        width: hover ? 64 : 26,
        height: hover ? 64 : 26,
        backgroundColor: hover ? "rgba(155,176,154,0.35)" : "rgba(0,0,0,0)",
      }}
      transition={{ duration: 0.2 }}
    />
  );
}