import { MAX_RECENT_LANGUAGES } from "./constants";

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
  } catch {}
  return [];
}

export function addRecentLanguage(key: string, code: string): void {
  const recents = getRecentLanguages(key);
  const updated = [code, ...recents.filter((c) => c !== code)].slice(
    0,
    MAX_RECENT_LANGUAGES
  );
  try {
    localStorage.setItem(key, JSON.stringify(updated));
  } catch {}
}
