'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Genre, Mood } from '@/lib/types';
import { fetchGenres, fetchMoods, fetchLanguages, fetchArtists } from '@/lib/api';

export default function TrackFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [genres, setGenres] = useState<Genre[]>([]);
  const [moods, setMoods] = useState<Mood[]>([]);
  const [languages, setLanguages] = useState<string[]>([]);
  const [artists, setArtists] = useState<string[]>([]);

  const activeGenre = searchParams.get('genre') || '';
  const activeMood = searchParams.get('mood') || '';
  const activeLanguage = searchParams.get('language') || '';
  const activeArtist = searchParams.get('artist') || '';

  useEffect(() => {
    fetchGenres().then(setGenres).catch(() => {});
    fetchMoods().then(setMoods).catch(() => {});
    fetchLanguages().then(setLanguages).catch(() => {});
    fetchArtists().then(setArtists).catch(() => {});
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

  const hasFilters = activeGenre || activeMood || activeLanguage || activeArtist;

  return (
    <div className="space-y-3">
      {/* Language row */}
      {languages.length > 1 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium uppercase tracking-wider text-zinc-600">Language</span>
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => setFilter('language', activeLanguage === lang ? '' : lang)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                activeLanguage === lang
                  ? 'bg-emerald-500 text-white'
                  : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800 hover:text-white'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
      )}

      {/* Genre row */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium uppercase tracking-wider text-zinc-600">Genre</span>
        {genres.map((g) => (
          <button
            key={g.id}
            onClick={() => setFilter('genre', activeGenre === g.slug ? '' : g.slug)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${
              activeGenre === g.slug
                ? 'bg-violet-500 text-white'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800 hover:text-white'
            }`}
          >
            {g.name}
          </button>
        ))}
      </div>

      {/* Mood row */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium uppercase tracking-wider text-zinc-600">Mood</span>
        {moods.map((m) => (
          <button
            key={m.id}
            onClick={() => setFilter('mood', activeMood === m.slug ? '' : m.slug)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${
              activeMood === m.slug
                ? 'bg-fuchsia-500 text-white'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800 hover:text-white'
            }`}
          >
            {m.name}
          </button>
        ))}
      </div>

      {/* Artist row */}
      {artists.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium uppercase tracking-wider text-zinc-600">Artist</span>
          {artists.map((a) => (
            <button
              key={a}
              onClick={() => setFilter('artist', activeArtist === a ? '' : a)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                activeArtist === a
                  ? 'bg-amber-500 text-white'
                  : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800 hover:text-white'
              }`}
            >
              {a}
            </button>
          ))}
        </div>
      )}

      {hasFilters && (
        <button
          onClick={() => router.push('/')}
          className="text-xs text-zinc-500 transition hover:text-white"
        >
          Clear all filters
        </button>
      )}
    </div>
  );
}
