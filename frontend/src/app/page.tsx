'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { TrackListItem, PaginatedResponse } from '@/lib/types';
import { fetchTracks, fetchFeatured, fetchPopular } from '@/lib/api';
import TrackGrid from '@/components/TrackGrid';
import TrackFilters from '@/components/TrackFilters';
import TrackRow from '@/components/TrackRow';
import SectionHeader from '@/components/SectionHeader';
import Pagination from '@/components/Pagination';

function HomeContent() {
  const searchParams = useSearchParams();
  const [data, setData] = useState<PaginatedResponse<TrackListItem> | null>(
    null
  );
  const [featured, setFeatured] = useState<TrackListItem[]>([]);
  const [popular, setPopular] = useState<TrackListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const hasFilters =
    searchParams.get('genre') ||
    searchParams.get('mood') ||
    searchParams.get('search') ||
    searchParams.get('page');

  useEffect(() => {
    if (!hasFilters) {
      Promise.all([fetchFeatured(), fetchPopular()])
        .then(([f, p]) => {
          setFeatured(f);
          setPopular(p);
        })
        .catch(() => {});
    }
  }, [hasFilters]);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = {};
    searchParams.forEach((value, key) => {
      params[key] = value;
    });
    fetchTracks(params)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [searchParams]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      {/* Featured sections - only when no filters active */}
      {!hasFilters && featured.length > 0 && (
        <section className="mb-8">
          <SectionHeader title="New This Week" href="/?ordering=-created_at" />
          <TrackRow tracks={featured} />
        </section>
      )}

      {!hasFilters && popular.length > 0 && (
        <section className="mb-8">
          <SectionHeader
            title="Popular"
            href="/?ordering=-download_count"
          />
          <TrackRow tracks={popular} />
        </section>
      )}

      <div className="flex flex-col gap-6 lg:flex-row">
        <TrackFilters />
        <div className="flex-1">
          <div className="mb-4 flex items-center justify-between">
            <h1 className="text-lg font-semibold text-white">
              {searchParams.get('search')
                ? `Results for "${searchParams.get('search')}"`
                : 'All Tracks'}
            </h1>
            {data && (
              <span className="text-sm text-zinc-500">
                {data.count} track{data.count !== 1 ? 's' : ''}
              </span>
            )}
          </div>

          {loading ? (
            <div className="py-20 text-center text-zinc-500">
              Loading tracks...
            </div>
          ) : (
            <>
              <TrackGrid tracks={data?.results || []} />
              {data && <Pagination count={data.count} />}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-zinc-500">Loading...</div>
      }
    >
      <HomeContent />
    </Suspense>
  );
}
