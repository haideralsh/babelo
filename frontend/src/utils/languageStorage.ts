import { MAX_RECENT_LANGUAGES } from "./constants";

// Helper to read recent languages from localStorage
export function getRecentLanguages(key: string): string[] {
  try {
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (Array.isArray(parsed)) {
        return parsed.filter(
          (code): code is string => typeof code === "string"
        );
      }
    }
  } catch {
    // Ignore parse errors
  }
  return [];
}

// Helper to add a language code to the recents list (most recent first, capped at MAX_RECENT_LANGUAGES)
export function addRecentLanguage(key: string, code: string): void {
  const recents = getRecentLanguages(key);
  // Remove if already present, then prepend
  const updated = [code, ...recents.filter((c) => c !== code)].slice(
    0,
    MAX_RECENT_LANGUAGES
  );
  try {
    localStorage.setItem(key, JSON.stringify(updated));
  } catch {
    // Ignore quota errors
  }
}
