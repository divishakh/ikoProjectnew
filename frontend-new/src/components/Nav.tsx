import { Link } from "react-router-dom";
import { useAuth } from "../authContext";

export default function Nav({ onMenu }: { onMenu: () => void }) {
  const { email, signOut } = useAuth();
  return (
    <header className="fixed left-0 top-0 z-30 flex w-full items-center justify-between px-6 py-5 md:px-10">
      <Link to="/" className="text-xl font-light lowercase tracking-tight">
        prakriti ai
      </Link>
      <div className="flex items-center gap-6">
        <nav className="hidden gap-8 text-sm font-light md:flex">
          <Link to="/analyze" className="hover:opacity-60">Analyze</Link>
          <Link to="/history" className="hover:opacity-60">History</Link>
          <Link to="/ayurveda" className="hover:opacity-60">Ayurveda</Link>
        </nav>
        {email ? (
          <>
            <span className="hidden max-w-[10rem] truncate text-xs font-light md:inline">{email}</span>
            <button onClick={() => void signOut()} className="text-sm font-light hover:opacity-60">
              Log out
            </button>
          </>
        ) : (
          <Link to="/login" className="text-sm font-light hover:opacity-60">
            Log in
          </Link>
        )}
        <button
          onClick={onMenu}
          aria-label="Open menu"
          className="flex h-10 w-10 items-center justify-center gap-1 rounded-full bg-white shadow-sm transition-transform hover:scale-110 active:scale-90"
        >
          <span className="h-1.5 w-1.5 rounded-full bg-ink" />
          <span className="h-1.5 w-1.5 rounded-full bg-ink" />
        </button>
      </div>
    </header>
  );
}