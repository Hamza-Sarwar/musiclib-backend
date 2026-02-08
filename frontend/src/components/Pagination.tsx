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
    <div className="mt-8 flex items-center justify-center gap-2">
      <button
        onClick={() => goToPage(currentPage - 1)}
        disabled={currentPage <= 1}
        className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-400 transition hover:border-zinc-600 hover:text-white disabled:opacity-40 disabled:hover:border-zinc-700 disabled:hover:text-zinc-400"
      >
        Previous
      </button>
      <span className="px-3 text-sm text-zinc-500">
        Page {currentPage} of {totalPages}
      </span>
      <button
        onClick={() => goToPage(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-400 transition hover:border-zinc-600 hover:text-white disabled:opacity-40 disabled:hover:border-zinc-700 disabled:hover:text-zinc-400"
      >
        Next
      </button>
    </div>
  );
}
