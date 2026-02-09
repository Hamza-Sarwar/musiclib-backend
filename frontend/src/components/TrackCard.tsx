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
    e.stopPropagation();
    if (isCurrentlyPlaying) {
      pause();
    } else {
      play(track);
    }
  };

  return (
    <div
      className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 transition ${
        isActive
          ? 'bg-violet-500/10'
          : 'hover:bg-zinc-900'
      }`}
    >
      {/* Play button */}
      <button
        onClick={handlePlay}
        className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full transition ${
          isCurrentlyPlaying
            ? 'bg-violet-500 text-white'
            : 'bg-zinc-800 text-zinc-400 group-hover:bg-violet-500 group-hover:text-white'
        }`}
      >
        {isCurrentlyPlaying ? (
          <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="4" width="4" height="16" />
            <rect x="14" y="4" width="4" height="16" />
          </svg>
        ) : (
          <svg className="h-3.5 w-3.5 ml-0.5" fill="currentColor" viewBox="0 0 24 24">
            <polygon points="5,3 19,12 5,21" />
          </svg>
        )}
      </button>

      {/* Title + badges */}
      <div className="min-w-0 flex-1">
        <Link
          href={`/tracks/${track.id}`}
          className={`block truncate text-sm font-medium transition ${
            isActive ? 'text-violet-400' : 'text-white hover:text-violet-400'
          }`}
        >
          {track.title}
        </Link>
        <div className="mt-0.5 flex items-center gap-2 text-xs text-zinc-500">
          {track.artist_name && (
            <>
              <span className="text-zinc-400">{track.artist_name}</span>
              <span className="text-zinc-700">-</span>
            </>
          )}
          {track.genre_name && <span>{track.genre_name}</span>}
          {track.genre_name && track.mood_name && <span className="text-zinc-700">/</span>}
          {track.mood_name && <span>{track.mood_name}</span>}
          {track.language && track.language !== 'English' && (
            <>
              <span className="text-zinc-700">|</span>
              <span className="text-violet-400/70">{track.language}</span>
            </>
          )}
        </div>
      </div>

      {/* Duration */}
      <span className="hidden text-xs tabular-nums text-zinc-500 sm:block">
        {track.duration_display}
      </span>

      {/* BPM */}
      {track.bpm && (
        <span className="hidden w-16 text-right text-xs text-zinc-600 md:block">
          {track.bpm} bpm
        </span>
      )}

      {/* Download */}
      <a
        href={getDownloadUrl(track.id)}
        onClick={(e) => e.stopPropagation()}
        className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-zinc-600 transition hover:bg-zinc-800 hover:text-white"
        title="Download"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
        </svg>
      </a>
    </div>
  );
}
