'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Genre, Mood } from '@/lib/types';
import { fetchGenres, fetchMoods } from '@/lib/api';

export default function TrackFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [genres, setGenres] = useState<Genre[]>([]);
  const [moods, setMoods] = useState<Mood[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  const activeGenre = searchParams.get('genre') || '';
  const activeMood = searchParams.get('mood') || '';

  useEffect(() => {
    fetchGenres().then(setGenres).catch(() => {});
    fetchMoods().then(setMoods).catch(() => {});
  }, []);

  const setFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.delete('page');
    router.push(`/?${params.toString()}`);
  };

  const clearAll = () => {
    router.push('/');
  };

  const hasFilters = activeGenre || activeMood;

  const filterContent = (
    <div className="space-y-6">
      {/* Genre */}
      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Genre
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {genres.map((g) => (
            <button
              key={g.id}
              onClick={() =>
                setFilter('genre', activeGenre === g.slug ? '' : g.slug)
              }
              className={`rounded-full px-3 py-1 text-xs transition ${
                activeGenre === g.slug
                  ? 'bg-primary-600 text-white'
                  : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
              }`}
            >
              {g.name}
              {g.track_count > 0 && (
                <span className="ml-1 text-zinc-500">({g.track_count})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Mood */}
      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          Mood
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {moods.map((m) => (
            <button
              key={m.id}
              onClick={() =>
                setFilter('mood', activeMood === m.slug ? '' : m.slug)
              }
              className={`rounded-full px-3 py-1 text-xs transition ${
                activeMood === m.slug
                  ? 'bg-primary-600 text-white'
                  : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
              }`}
            >
              {m.name}
              {m.track_count > 0 && (
                <span className="ml-1 text-zinc-500">({m.track_count})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {hasFilters && (
        <button
          onClick={clearAll}
          className="text-xs text-primary-400 transition hover:text-primary-300"
        >
          Clear all filters
        </button>
      )}
    </div>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="mb-4 flex items-center gap-2 rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-300 transition hover:border-zinc-600 lg:hidden"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path d="M3 4h18M3 12h18M3 20h18" />
        </svg>
        Filters
        {hasFilters && (
          <span className="rounded-full bg-primary-600 px-1.5 py-0.5 text-xs">
            Active
          </span>
        )}
      </button>

      {/* Mobile drawer */}
      {isOpen && (
        <div className="mb-4 rounded-lg border border-zinc-800 bg-zinc-900 p-4 lg:hidden">
          {filterContent}
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden w-64 flex-shrink-0 lg:block">
        <div className="sticky top-20 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h2 className="mb-4 text-sm font-semibold text-white">Filters</h2>
          {filterContent}
        </div>
      </aside>
    </>
  );
}
