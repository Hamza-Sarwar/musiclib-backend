'use client';

import Link from 'next/link';
import SearchBar from './SearchBar';
import UserMenu from './UserMenu';

export default function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
        <Link
          href="/"
          className="flex-shrink-0 text-xl font-bold text-white"
        >
          <span className="text-primary-500">Music</span>Lib
        </Link>
        <div className="flex-1">
          <SearchBar />
        </div>
        <nav className="hidden items-center gap-4 sm:flex">
          <Link
            href="/"
            className="text-sm text-zinc-400 transition hover:text-white"
          >
            Browse
          </Link>
        </nav>
        <UserMenu />
      </div>
    </header>
  );
}
