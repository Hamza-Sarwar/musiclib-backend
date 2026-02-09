'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function UserMenu() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) return null;

  if (!user) {
    return (
      <div className="flex items-center gap-1">
        <Link
          href="/login"
          className="rounded-full px-3 py-1.5 text-xs text-zinc-500 transition hover:text-white"
        >
          Log in
        </Link>
        <Link
          href="/register"
          className="rounded-full bg-violet-600 px-4 py-1.5 text-xs font-medium text-white transition hover:bg-violet-500"
        >
          Sign up
        </Link>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-zinc-500">{user.username}</span>
      <button
        onClick={logout}
        className="rounded-full px-3 py-1.5 text-xs text-zinc-500 transition hover:text-white"
      >
        Log out
      </button>
    </div>
  );
}
