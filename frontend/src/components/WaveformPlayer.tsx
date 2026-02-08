'use client';

import { useEffect, useRef, useState } from 'react';
import { usePlayer } from '@/contexts/PlayerContext';
import { TrackListItem } from '@/lib/types';

interface WaveformPlayerProps {
  track: TrackListItem & { waveform_data?: number[] | null; audio_url: string | null };
}

export default function WaveformPlayer({ track }: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<any>(null);
  const { currentTrack, isPlaying, currentTime, play, pause, audioRef } = usePlayer();
  const [ready, setReady] = useState(false);
  const isActive = currentTrack?.id === track.id;

  useEffect(() => {
    if (!containerRef.current) return;

    let ws: any = null;

    (async () => {
      const WaveSurfer = (await import('wavesurfer.js')).default;

      ws = WaveSurfer.create({
        container: containerRef.current!,
        waveColor: '#52525b',
        progressColor: '#6366f1',
        cursorColor: '#a5b4fc',
        cursorWidth: 2,
        height: 80,
        barWidth: 2,
        barGap: 1,
        barRadius: 2,
        normalize: true,
        interact: true,
        backend: 'WebAudio',
        peaks: track.waveform_data ? [track.waveform_data] : undefined,
        url: track.waveform_data ? undefined : (track.audio_url || undefined),
        media: undefined,
      });

      if (track.waveform_data) {
        ws.load('', [track.waveform_data], track.duration);
      }

      ws.on('ready', () => setReady(true));

      ws.on('click', (relativeX: number) => {
        // Use the player context to control playback
        const listItem: TrackListItem = {
          id: track.id,
          title: track.title,
          genre_name: (track as any).genre_name || (track as any).genre?.name || null,
          mood_name: (track as any).mood_name || (track as any).mood?.name || null,
          duration: track.duration,
          duration_display: (track as any).duration_display || '',
          bpm: (track as any).bpm || null,
          download_count: (track as any).download_count || 0,
          play_count: (track as any).play_count || 0,
          audio_url: track.audio_url,
          file_size: (track as any).file_size || 0,
          is_featured: (track as any).is_featured || false,
          created_at: (track as any).created_at || '',
        };
        play(listItem);
        const seekTo = relativeX * track.duration;
        if (audioRef.current) {
          audioRef.current.currentTime = seekTo;
        }
      });

      wavesurferRef.current = ws;
    })();

    return () => {
      ws?.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [track.id]);

  // Sync visual position with PlayerContext
  useEffect(() => {
    if (wavesurferRef.current && ready && isActive && track.duration > 0) {
      const pct = currentTime / track.duration;
      wavesurferRef.current.seekTo(Math.min(pct, 1));
    }
  }, [currentTime, isActive, ready, track.duration]);

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
      <div ref={containerRef} className="w-full" />
      {!ready && (
        <div className="flex h-20 items-center justify-center text-sm text-zinc-500">
          Loading waveform...
        </div>
      )}
    </div>
  );
}
