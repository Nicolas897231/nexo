"use client";

import type { ReactNode } from "react";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

type ThemeMode = "light" | "dark";
type Accent = "blue" | "ocean" | "night";

type ThemeState = {
  mode: ThemeMode;
  accent: Accent;
  compact: boolean;
  setMode: (mode: ThemeMode) => void;
  setAccent: (accent: Accent) => void;
  setCompact: (compact: boolean) => void;
};

const ThemeContext = createContext<ThemeState | null>(null);

const STORAGE_KEY = "nexovia.visual-preferences";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>("light");
  const [accent, setAccentState] = useState<Accent>("blue");
  const [compact, setCompactState] = useState(false);

  useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw) as Partial<Pick<ThemeState, "mode" | "accent" | "compact">>;
      if (parsed.mode === "dark" || parsed.mode === "light") setModeState(parsed.mode);
      if (parsed.accent === "blue" || parsed.accent === "ocean" || parsed.accent === "night") {
        setAccentState(parsed.accent);
      }
      if (typeof parsed.compact === "boolean") setCompactState(parsed.compact);
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = mode;
    document.documentElement.dataset.accent = accent;
    document.documentElement.dataset.compact = compact ? "true" : "false";
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, accent, compact }));
  }, [accent, compact, mode]);

  const value = useMemo<ThemeState>(
    () => ({
      mode,
      accent,
      compact,
      setMode: setModeState,
      setAccent: setAccentState,
      setCompact: setCompactState,
    }),
    [accent, compact, mode],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const value = useContext(ThemeContext);
  if (!value) throw new Error("useTheme must be used inside ThemeProvider");
  return value;
}
