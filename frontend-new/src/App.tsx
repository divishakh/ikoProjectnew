import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Route, Routes } from "react-router-dom";
import Cursor from "./components/Cursor";
import Intro from "./components/Intro";
import Menu from "./components/Menu";
import Nav from "./components/Nav";
import Analyze from "./pages/Analyze";
import Auth from "./pages/Auth";
import Home from "./pages/Home";
import Placeholder from "./pages/Placeholder";

export default function App() {
  const [entered, setEntered] = useState(false);
  const [menu, setMenu] = useState(false);

  return (
    <>
      <Cursor />
      <AnimatePresence>{!entered && <Intro onEnter={() => setEntered(true)} />}</AnimatePresence>
      {entered && (
        <>
          <Nav onMenu={() => setMenu(true)} />
          <Menu open={menu} onClose={() => setMenu(false)} />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Auth />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/history" element={<Placeholder title="History" />} />
            <Route path="/ayurveda" element={<Placeholder title="Ayurveda" />} />
            <Route path="/technology" element={<Placeholder title="Technology" />} />
            <Route path="/assistant" element={<Placeholder title="Assistant" />} />
          </Routes>
        </>
      )}
    </>
  );
}