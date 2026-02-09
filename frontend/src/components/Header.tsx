'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import SearchBar from './SearchBar';
import UserMenu from './UserMenu';

export default function Header() {
  return (
    <header className="sticky top-0 z-40 bg-zinc-950/90 backdrop-blur-lg">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4 sm:px-6">
        <Link href="/" className="flex-shrink-0 text-lg font-bold tracking-tight">
          <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            MusicLib
          </span>
        </Link>
        <div className="flex-1">
          <Suspense fallback={<div className="h-9" />}>
            <SearchBar />
          </Suspense>
        </div>
        <UserMenu />
      </div>
    </header>
  );
}
