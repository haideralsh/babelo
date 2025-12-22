import { LanguagesIcon } from "./icons";

export function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-500/10 dark:bg-blue-500/20 mb-4">
          <LanguagesIcon className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-pulse" />
        </div>
        <p className="text-zinc-500 dark:text-zinc-400">Loading...</p>
      </div>
    </div>
  );
}
