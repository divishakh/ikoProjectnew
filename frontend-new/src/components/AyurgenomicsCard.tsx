import { useEffect, useRef, useState } from "react";
import * as api from "../api";
import type { AyurItem, AyurProfile } from "../api";

const TYPES = ["Vata", "Pitta", "Kapha"];

const KIND: Record<AyurItem["kind"], { label: string; cls: string }> = {
  study: { label: "Study finding", cls: "bg-sage/30 text-ink" },
  classical: { label: "Classical text", cls: "bg-lilac/50 text-ink" },
  hypothesis: { label: "Hypothesis", cls: "bg-amber-100 text-amber-900" },
  note: { label: "Note", cls: "bg-ivory text-ink/70" },
};

const EFFECT: Record<string, string> = {
  pacifies: "bg-sage/30 text-ink",
  increases: "bg-amber-100 text-amber-900",
  neutral: "bg-ivory text-ink/60",
};

function Chips({ ids, profile }: { ids: string[]; profile: AyurProfile }) {
  return (
    <span className="ml-1 inline-flex flex-wrap gap-1 align-middle">
      {ids.map((id) => (
        <span
          key={id}
          title={profile.sources[id]?.citation ?? id}
          className="rounded-full bg-ivory px-2 py-0.5 text-[10px] font-medium text-ink/70"
        >
          {profile.sources[id]?.short ?? id}
        </span>
      ))}
    </span>
  );
}

function Item({ item, profile }: { item: AyurItem; profile: AyurProfile }) {
  const k = KIND[item.kind] ?? KIND.note;
  return (
    <li className="rounded-2xl bg-ivory px-4 py-3">
      <span className={`mr-2 rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide ${k.cls}`}>{k.label}</span>
      <span className="text-sm font-light">{item.text}</span>
      <Chips ids={item.sources} profile={profile} />
      {item.note && <p className="mt-1 text-xs font-light italic text-ink/60">{item.note}</p>}
    </li>
  );
}

export default function AyurgenomicsCard({ predicted, demo, initial }: { predicted?: string; demo: boolean; initial?: AyurProfile | null }) {
  const start = TYPES.find((t) => t.toLowerCase() === (predicted ?? "").toLowerCase()) ?? null;
  const [selected, setSelected] = useState<string | null>(start);
  const [cache, setCache] = useState<Record<string, AyurProfile>>(initial ? { [initial.prakriti]: initial } : {});
  const [failed, setFailed] = useState<{ prakriti: string; message: string } | null>(null);
  const requested = useRef(new Set<string>(initial ? [initial.prakriti] : []));

  useEffect(() => {
    if (!selected || requested.current.has(selected)) return;
    requested.current.add(selected);
    api
      .getAyurgenomics(selected)
      .then((p) => setCache((c) => ({ ...c, [p.prakriti]: p })))
      .catch((e) => {
        requested.current.delete(selected);
        setFailed({ prakriti: selected, message: e instanceof Error ? e.message : "Could not load the research summary." });
      });
  }, [selected]);

  const profile = selected ? cache[selected] : undefined;
  const error = failed && failed.prakriti === selected ? failed.message : null;

  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm">
      <h2 className="text-sm font-medium">Ayurgenomics: research context</h2>
      <p className="mt-1 text-xs font-light text-ink/60">
        What published studies report for each Prakriti type: biochemistry, gene expression, genetic markers, physiology,
        disease associations and the classical taste (rasa) effects.
      </p>

      <div className="mt-4 rounded-2xl bg-blush/60 px-4 py-3 text-xs font-light text-ink/80">
        {demo
          ? "The Prakriti estimate above is a demonstration output that is not better than chance. Choose the Prakriti confirmed by a practitioner or a validated questionnaire. "
          : "Choose a Prakriti to read about. "}
        These are group-level research findings, not a test of your genes and not medical advice.
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {TYPES.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setSelected(t)}
            aria-pressed={selected === t}
            className={`rounded-full px-4 py-1.5 text-sm transition ${
              selected === t ? "bg-ink text-ivory" : "bg-ivory text-ink hover:bg-lilac/40"
            }`}
          >
            {t}
            {start === t && <span className="ml-2 text-[10px] uppercase tracking-wide opacity-70">model estimate</span>}
          </button>
        ))}
      </div>

      {!selected && <p className="mt-4 text-sm font-light text-ink/70">Select Vata, Pitta or Kapha above.</p>}
      {selected && !profile && !error && <p className="mt-4 text-sm font-light text-ink/70">Loading…</p>}
      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}

      {profile && (
        <div className="mt-5">
          <p className="text-sm font-light">{profile.summary}</p>

          <div className="mt-4 flex flex-col gap-2">
            {profile.sections.map((s, i) => (
              <details key={s.id} open={i === 0} className="rounded-2xl border border-ink/10 px-4 py-3">
                <summary className="cursor-pointer text-sm font-medium">
                  {s.title} <span className="text-xs font-light text-ink/50">({s.items.length})</span>
                </summary>
                <ul className="mt-3 flex flex-col gap-2">
                  {s.items.map((it, j) => (
                    <Item key={j} item={it} profile={profile} />
                  ))}
                </ul>
              </details>
            ))}

            <details className="rounded-2xl border border-ink/10 px-4 py-3">
              <summary className="cursor-pointer text-sm font-medium">Tastes (rasa): classical effect on {profile.prakriti}</summary>
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {Object.entries(profile.tastes.items).map(([taste, v]) => (
                  <div key={taste} className="flex items-center justify-between rounded-2xl bg-ivory px-4 py-2 text-sm">
                    <span className="font-light">{taste}</span>
                    <span className={`rounded-full px-3 py-0.5 text-xs ${EFFECT[v.effect] ?? EFFECT.neutral}`}>{v.effect}</span>
                  </div>
                ))}
              </div>
              <p className="mt-3 text-xs font-light text-ink/60">
                {profile.tastes.note} <span className="font-medium">Source: {profile.sources.S5?.short}</span>
              </p>
            </details>

            <details className="rounded-2xl border border-ink/10 px-4 py-3">
              <summary className="cursor-pointer text-sm font-medium">About Ayurgenomics and Prakriti</summary>
              <ul className="mt-3 flex flex-col gap-2">
                {profile.concepts.map((c) => (
                  <li key={c.title} className="rounded-2xl bg-ivory px-4 py-3">
                    <p className="text-sm font-medium">{c.title}</p>
                    <p className="mt-1 text-sm font-light">
                      {c.text}
                      <Chips ids={c.sources} profile={profile} />
                    </p>
                  </li>
                ))}
              </ul>
            </details>

            <details className="rounded-2xl border border-ink/10 px-4 py-3">
              <summary className="cursor-pointer text-sm font-medium">Limits of this information</summary>
              <ul className="mt-3 list-disc pl-5 text-xs font-light text-ink/70">
                {profile.caveats.map((c) => (
                  <li key={c} className="mt-1">{c}</li>
                ))}
              </ul>
            </details>

            <details className="rounded-2xl border border-ink/10 px-4 py-3">
              <summary className="cursor-pointer text-sm font-medium">Sources</summary>
              <ul className="mt-3 flex flex-col gap-2 text-xs font-light text-ink/70">
                {Object.values(profile.sources).map((s) => (
                  <li key={s.short}>{s.citation}</li>
                ))}
              </ul>
            </details>
          </div>
        </div>
      )}
    </div>
  );
}
