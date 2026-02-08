'use client';

import Link from 'next/link';
import { TrackListItem } from '@/lib/types';
import { usePlayer } from '@/contexts/PlayerContext';
import { getDownloadUrl } from '@/lib/api';

export default function TrackCard({ track }: { track: TrackListItem }) {
  const { play, pause, currentTrack, isPlaying } = usePlayer();
  const isActive = currentTrack?.id === track.id;
  const isCurrentlyPlaying = isActive && isPlaying;

  const handlePlay = (e: React.MouseEvent) => {
    e.preventDefault();
    if (isCurrentlyPlaying) {
      pause();
    } else {
      play(track);
    }
  };

  return (
    <div
      className={`group rounded-lg border p-4 transition ${
        isActive
          ? 'border-primary-600 bg-primary-950/30'
          : 'border-zinc-800 bg-zinc-900/50 hover:border-zinc-700'
      }`}
    >
      {/* Title + Link */}
      <Link
        href={`/tracks/${track.id}`}
        className="mb-2 block truncate text-sm font-medium text-white hover:text-primary-400"
      >
        {track.title}
      </Link>

      {/* Badges */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {track.genre_name && (
          <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
            {track.genre_name}
          </span>
        )}
        {track.mood_name && (
          <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
            {track.mood_name}
          </span>
        )}
      </div>

      {/* Meta row */}
      <div className="mb-3 flex items-center gap-3 text-xs text-zinc-500">
        <span>{track.duration_display}</span>
        {track.bpm && <span>{track.bpm} BPM</span>}
        <span className="ml-auto flex items-center gap-1">
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
          </svg>
          {track.download_count}
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={handlePlay}
          className="flex h-9 flex-1 items-center justify-center gap-2 rounded-md bg-primary-600 text-sm font-medium text-white transition hover:bg-primary-500"
        >
          {isCurrentlyPlaying ? (
            <>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="4" width="4" height="16" />
                <rect x="14" y="4" width="4" height="16" />
              </svg>
              Pause
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <polygon points="5,3 19,12 5,21" />
              </svg>
              Play
            </>
          )}
        </button>
        <a
          href={getDownloadUrl(track.id)}
          className="flex h-9 w-9 items-center justify-center rounded-md border border-zinc-700 text-zinc-400 transition hover:border-zinc-500 hover:text-white"
          title="Download"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
          </svg>
        </a>
      </div>
    </div>
  );
}
