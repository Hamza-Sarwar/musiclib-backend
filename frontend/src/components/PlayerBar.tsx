'use client';

import { usePlayer } from '@/contexts/PlayerContext';
import { formatDuration } from '@/lib/utils';
import { getDownloadUrl } from '@/lib/api';

export default function PlayerBar() {
  const {
    currentTrack,
    isPlaying,
    progress,
    currentTime,
    duration,
    volume,
    togglePlay,
    seek,
    setVolume,
  } = usePlayer();

  if (!currentTrack) return null;

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    seek(pct * duration);
  };

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 border-t border-zinc-800 bg-zinc-950/95 backdrop-blur-md">
      <div
        className="h-1 cursor-pointer bg-zinc-800"
        onClick={handleProgressClick}
      >
        <div
          className="h-full bg-primary-500 transition-[width] duration-100"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4">
        {/* Play/Pause */}
        <button
          onClick={togglePlay}
          className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-primary-600 text-white transition hover:bg-primary-500"
        >
          {isPlaying ? (
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <polygon points="5,3 19,12 5,21" />
            </svg>
          )}
        </button>

        {/* Track Info */}
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-white">
            {currentTrack.title}
          </p>
          <p className="text-xs text-zinc-400">
            {currentTrack.genre_name}
            {currentTrack.mood_name && ` / ${currentTrack.mood_name}`}
          </p>
        </div>

        {/* Time */}
        <span className="hidden text-xs text-zinc-500 sm:block">
          {formatDuration(Math.floor(currentTime))} /{' '}
          {formatDuration(Math.floor(duration))}
        </span>

        {/* Volume */}
        <div className="hidden items-center gap-2 sm:flex">
          <svg
            className="h-4 w-4 text-zinc-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path d="M11 5L6 9H2v6h4l5 4V5z" />
            {volume > 0 && (
              <path d="M15.54 8.46a5 5 0 010 7.07" />
            )}
          </svg>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="h-1 w-20 cursor-pointer accent-primary-500"
          />
        </div>

        {/* Download */}
        <a
          href={getDownloadUrl(currentTrack.id)}
          className="flex h-8 w-8 items-center justify-center rounded text-zinc-400 transition hover:text-white"
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
