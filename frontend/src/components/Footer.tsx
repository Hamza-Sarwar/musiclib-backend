export default function Footer() {
  return (
    <footer className="border-t border-zinc-800 bg-zinc-950 pb-24">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-zinc-500">
            &copy; {new Date().getFullYear()} MusicLib. Free AI-generated background music.
          </p>
          <div className="flex gap-6 text-sm text-zinc-500">
            <a href="#" className="transition hover:text-white">
              About
            </a>
            <a href="#" className="transition hover:text-white">
              License
            </a>
            <a href="#" className="transition hover:text-white">
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
