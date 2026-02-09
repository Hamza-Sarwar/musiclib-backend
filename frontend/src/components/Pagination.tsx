'use client';

import { useRouter, useSearchParams } from 'next/navigation';

interface PaginationProps {
  count: number;
  pageSize?: number;
}

export default function Pagination({ count, pageSize = 20 }: PaginationProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const totalPages = Math.ceil(count / pageSize);

  if (totalPages <= 1) return null;

  const goToPage = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', page.toString());
    router.push(`/?${params.toString()}`);
  };

  return (
    <div className="mt-6 flex items-center justify-center gap-3">
      <button
        onClick={() => goToPage(currentPage - 1)}
        disabled={currentPage <= 1}
        className="rounded-full bg-zinc-900 px-4 py-1.5 text-xs text-zinc-400 transition hover:bg-zinc-800 hover:text-white disabled:opacity-30 disabled:hover:bg-zinc-900 disabled:hover:text-zinc-400"
      >
        Previous
      </button>
      <span className="text-xs text-zinc-600">
        {currentPage} / {totalPages}
      </span>
      <button
        onClick={() => goToPage(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="rounded-full bg-zinc-900 px-4 py-1.5 text-xs text-zinc-400 transition hover:bg-zinc-800 hover:text-white disabled:opacity-30 disabled:hover:bg-zinc-900 disabled:hover:text-zinc-400"
      >
        Next
      </button>
    </div>
  );
}
