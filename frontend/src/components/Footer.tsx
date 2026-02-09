export default function Footer() {
  return (
    <footer className="pb-20">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
          <p className="text-xs text-zinc-700">
            {new Date().getFullYear()} MusicLib. Free AI-generated music.
          </p>
          <div className="flex gap-6 text-xs text-zinc-700">
            <a href="#" className="transition hover:text-zinc-400">About</a>
            <a href="#" className="transition hover:text-zinc-400">License</a>
            <a href="#" className="transition hover:text-zinc-400">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
