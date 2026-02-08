'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { User, AuthTokens } from '@/lib/types';
import {
  login as apiLogin,
  register as apiRegister,
  refreshToken,
  fetchMe,
} from '@/lib/api';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const saveTokens = (tokens: AuthTokens) => {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    setToken(tokens.access);
  };

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setUser(null);
  };

  const loadUser = useCallback(async (accessToken: string) => {
    try {
      const userData = await fetchMe(accessToken);
      setUser(userData);
      setToken(accessToken);
    } catch {
      // Token expired, try refresh
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { access } = await refreshToken(refresh);
          localStorage.setItem('access_token', access);
          const userData = await fetchMe(access);
          setUser(userData);
          setToken(access);
        } catch {
          clearTokens();
        }
      } else {
        clearTokens();
      }
    }
  }, []);

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      loadUser(accessToken).finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [loadUser]);

  const login = async (username: string, password: string) => {
    const tokens = await apiLogin(username, password);
    saveTokens(tokens);
    await loadUser(tokens.access);
  };

  const register = async (
    username: string,
    email: string,
    password: string
  ) => {
    const tokens = await apiRegister(username, email, password);
    saveTokens(tokens);
    await loadUser(tokens.access);
  };

  const logout = () => {
    clearTokens();
  };

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
