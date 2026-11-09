export default function Placeholder({ title }: { title: string }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-ivory px-6 text-center">
      <h1 className="font-display text-6xl italic md:text-8xl">{title}</h1>
      <p className="mt-4 text-sm text-ink/60">Coming in a later stage.</p>
    </main>
  );
}