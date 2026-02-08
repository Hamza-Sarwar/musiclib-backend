'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function UserMenu() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) return null;

  if (!user) {
    return (
      <div className="flex items-center gap-2">
        <Link
          href="/login"
          className="rounded-lg px-3 py-1.5 text-sm text-zinc-400 transition hover:text-white"
        >
          Log in
        </Link>
        <Link
          href="/register"
          className="rounded-lg bg-primary-600 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-primary-500"
        >
          Sign up
        </Link>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-zinc-400">{user.username}</span>
      <button
        onClick={logout}
        className="rounded-lg px-3 py-1.5 text-sm text-zinc-400 transition hover:text-white"
      >
        Log out
      </button>
    </div>
  );
}
