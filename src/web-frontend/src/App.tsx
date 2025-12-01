import { useState, useEffect, useRef } from "react";
import { Textarea } from "./components/ui/textarea";
import { Badge } from "./components/ui/badge";
import { LanguageSelector, type Language } from "./components/LanguageSelector";

interface HistoryItemData {
  id: string;
  sourceText: string;
  translatedText: string;
  sourceLang: string;
  targetLang: string;
  timestamp: Date;
}

const API_BASE_URL = "http://localhost:8000";
const DEBOUNCE_DELAY = 500;

// LocalStorage keys for language preferences
const LS_SOURCE_LANGS_KEY = "bab_source_languages";
const LS_TARGET_LANGS_KEY = "bab_target_languages";
const MAX_RECENT_LANGUAGES = 5;

// Helper to read recent languages from localStorage
function getRecentLanguages(key: string): string[] {
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
function addRecentLanguage(key: string, code: string): void {
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

// Icons as components
const LanguagesIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="m5 8 6 6" />
    <path d="m4 14 6-6 2-3" />
    <path d="M2 5h12" />
    <path d="M7 2h1" />
    <path d="m22 22-5-10-5 10" />
    <path d="M14 18h6" />
  </svg>
);

const ArrowRightLeftIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="m16 3 4 4-4 4" />
    <path d="M20 7H4" />
    <path d="m8 21-4-4 4-4" />
    <path d="M4 17h16" />
  </svg>
);

const ClockIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10" />
    <polyline points="12,6 12,12 16,14" />
  </svg>
);

const TrashIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 6h18" />
    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
  </svg>
);

const XIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M18 6 6 18" />
    <path d="m6 6 12 12" />
  </svg>
);

const ArrowRightIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M5 12h14" />
    <path d="m12 5 7 7-7 7" />
  </svg>
);

const CopyIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
  </svg>
);

const CheckIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="20,6 9,17 4,12" />
  </svg>
);

const VolumeIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
  </svg>
);

function TranslationPanel({
  value,
  onChange,
  placeholder,
  isSource = false,
  readOnly = false,
  language,
  loading = false,
}: {
  value: string;
  onChange?: (value: string) => void;
  placeholder: string;
  isSource?: boolean;
  readOnly?: boolean;
  language: string;
  loading?: boolean;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    if (!value) return;
    const utterance = new SpeechSynthesisUtterance(value);
    speechSynthesis.speak(utterance);
  };

  const characterCount = value.length;

  return (
    <div
      className={`bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-700 overflow-hidden flex flex-col ${
        readOnly ? "bg-zinc-50 dark:bg-zinc-800/50" : ""
      }`}
    >
      {/* Language Label */}
      <div className="px-4 py-2 border-b border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-800/50">
        <span className="text-sm font-medium text-zinc-900 dark:text-white">
          {language}
        </span>
        {loading && (
          <span className="ml-2 text-xs text-zinc-500 dark:text-zinc-400">
            translating...
          </span>
        )}
      </div>

      {/* Text Area */}
      <div className="relative flex-1">
        <Textarea
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={placeholder}
          disabled={readOnly}
          resizable={false}
          className="min-h-[180px] border-0 rounded-none bg-transparent focus:ring-0 text-base leading-relaxed"
        />
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50/50 dark:bg-zinc-800/30">
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleSpeak}
            disabled={!value}
            className="h-8 w-8 p-0 inline-flex items-center justify-center rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            aria-label="Listen"
          >
            <VolumeIcon className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={handleCopy}
            disabled={!value}
            className="h-8 w-8 p-0 inline-flex items-center justify-center rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            aria-label="Copy"
          >
            {copied ? (
              <CheckIcon className="w-4 h-4 text-blue-500" />
            ) : (
              <CopyIcon className="w-4 h-4" />
            )}
          </button>
        </div>
        {isSource && (
          <span className="text-xs text-zinc-500 dark:text-zinc-400">
            {characterCount} / 5000
          </span>
        )}
      </div>
    </div>
  );
}

// History Item Component
function HistoryItem({
  item,
  getLanguageName,
  onClick,
  onDelete,
}: {
  item: HistoryItemData;
  getLanguageName: (code: string) => string;
  onClick: () => void;
  onDelete: () => void;
}) {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      className="group relative bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-700 hover:shadow-sm transition-all cursor-pointer"
      onClick={onClick}
    >
      {/* Delete Button */}
      <button
        type="button"
        onClick={(e: React.MouseEvent) => {
          e.stopPropagation();
          onDelete();
        }}
        className="absolute top-2 right-2 h-7 w-7 p-0 inline-flex items-center justify-center rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-white dark:hover:bg-zinc-700 opacity-0 group-hover:opacity-100 transition-opacity"
        aria-label="Delete"
      >
        <XIcon className="w-4 h-4" />
      </button>

      {/* Language Direction */}
      <div className="flex items-center gap-2 mb-2">
        <Badge color="zinc">{getLanguageName(item.sourceLang)}</Badge>
        <ArrowRightIcon className="w-3 h-3 text-zinc-400" />
        <Badge color="zinc">{getLanguageName(item.targetLang)}</Badge>
        <span className="text-xs text-zinc-500 dark:text-zinc-400 ml-auto">
          {formatTime(item.timestamp)}
        </span>
      </div>

      {/* Text Content */}
      <div className="grid md:grid-cols-2 gap-3">
        <p className="text-sm text-zinc-900 dark:text-white line-clamp-2">
          {item.sourceText}
        </p>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 line-clamp-2">
          {item.translatedText}
        </p>
      </div>
    </div>
  );
}

function App() {
  const [inputText, setInputText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [languages, setLanguages] = useState<Language[]>([]);
  const [sourceLanguage, setSourceLanguageState] = useState("");
  const [targetLanguage, setTargetLanguageState] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<HistoryItemData[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Wrapper setters that persist to localStorage
  const setSourceLanguage = (code: string) => {
    setSourceLanguageState(code);
    if (code) addRecentLanguage(LS_SOURCE_LANGS_KEY, code);
  };

  const setTargetLanguage = (code: string) => {
    setTargetLanguageState(code);
    if (code) addRecentLanguage(LS_TARGET_LANGS_KEY, code);
  };

  // Fetch languages on component mount
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/languages`);
        const data = await response.json();

        const languageList: Language[] = Object.entries(data.languages).map(
          ([name, code]) => ({
            name,
            code: code as string,
          })
        );

        setLanguages(languageList);

        // Set default languages: prefer stored preference, fall back to English/Spanish
        if (languageList.length > 0) {
          const storedSource = getRecentLanguages(LS_SOURCE_LANGS_KEY)[0];
          const storedTarget = getRecentLanguages(LS_TARGET_LANGS_KEY)[0];

          const validSource =
            storedSource && languageList.some((l) => l.code === storedSource);
          const validTarget =
            storedTarget && languageList.some((l) => l.code === storedTarget);

          if (validSource) {
            setSourceLanguage(storedSource);
          } else {
            const english = languageList.find((l) => l.name === "English");
            if (english) setSourceLanguage(english.code);
          }

          if (validTarget) {
            setTargetLanguage(storedTarget);
          } else {
            const spanish = languageList.find((l) => l.name === "Spanish");
            if (spanish) setTargetLanguage(spanish.code);
            else if (languageList.length > 1)
              setTargetLanguage(languageList[1].code);
          }
        }
      } catch (err) {
        setError(
          "Failed to fetch languages. Make sure the backend server is running."
        );
        console.error("Error fetching languages:", err);
      }
    };

    fetchLanguages();
  }, []);

  // Auto-translate with debounce
  useEffect(() => {
    if (!inputText.trim()) {
      setTranslatedText("");
      setError("");
      return;
    }

    if (!sourceLanguage || !targetLanguage) {
      return;
    }

    const timeoutId = setTimeout(async () => {
      // Cancel any pending request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      setLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_BASE_URL}/translate`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: inputText,
            source_language_code: sourceLanguage,
            target_language_code: targetLanguage,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Translation failed");
        }

        const data = await response.json();
        setTranslatedText(data.translated_text);
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return; // Ignore aborted requests
        }
        setError(err instanceof Error ? err.message : "Translation failed");
        console.error("Error translating:", err);
      } finally {
        setLoading(false);
      }
    }, DEBOUNCE_DELAY);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [inputText, sourceLanguage, targetLanguage]);

  const handleSwapLanguages = () => {
    const tempLang = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(tempLang);

    // Swap the text as well
    const tempText = inputText;
    setInputText(translatedText);
    setTranslatedText(tempText);
  };

  const handleTranslate = () => {
    if (!inputText.trim() || !translatedText.trim()) return;

    // Add to history
    const newHistoryItem: HistoryItemData = {
      id: Date.now().toString(),
      sourceText: inputText,
      translatedText: translatedText,
      sourceLang: sourceLanguage,
      targetLang: targetLanguage,
      timestamp: new Date(),
    };
    setHistory([newHistoryItem, ...history]);
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  const handleDeleteHistoryItem = (id: string) => {
    setHistory(history.filter((item) => item.id !== id));
  };

  const handleHistoryItemClick = (item: HistoryItemData) => {
    setSourceLanguage(item.sourceLang);
    setTargetLanguage(item.targetLang);
    setInputText(item.sourceText);
    setTranslatedText(item.translatedText);
  };

  const getLanguageName = (code: string) => {
    return languages.find((l) => l.code === code)?.name || code;
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <div className="max-w-5xl mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <header className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-blue-500/10 dark:bg-blue-500/20 rounded-xl">
            <LanguagesIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-white">
            Bab Translator
          </h1>
        </header>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Language Selection Bar */}
        <div className="flex items-center justify-between gap-4 mb-4">
          <LanguageSelector
            languages={languages}
            value={sourceLanguage}
            onChange={setSourceLanguage}
            label="From"
            disabled={loading}
          />

          <button
            type="button"
            onClick={handleSwapLanguages}
            disabled={loading}
            className="rounded-full p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors shrink-0 mt-5 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Swap languages"
          >
            <ArrowRightLeftIcon className="w-5 h-5 text-zinc-500 dark:text-zinc-400" />
          </button>

          <LanguageSelector
            languages={languages}
            value={targetLanguage}
            onChange={setTargetLanguage}
            label="To"
            disabled={loading}
          />
        </div>

        {/* Translation Panels */}
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <TranslationPanel
            value={inputText}
            onChange={setInputText}
            placeholder="Enter text to translate..."
            isSource
            language={getLanguageName(sourceLanguage)}
          />

          <TranslationPanel
            value={translatedText}
            placeholder="Translation will appear here..."
            readOnly
            language={getLanguageName(targetLanguage)}
            loading={loading}
          />
        </div>

        {/* Translate Button (Save to History) */}
        <div className="flex justify-center mb-12">
          <button
            type="button"
            onClick={handleTranslate}
            disabled={!inputText.trim() || !translatedText.trim()}
            className="px-8 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Save to History
          </button>
        </div>

        {/* History Section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ClockIcon className="w-5 h-5 text-zinc-500 dark:text-zinc-400" />
              <h2 className="text-lg font-medium text-zinc-900 dark:text-white">
                History
              </h2>
              <span className="text-sm text-zinc-500 dark:text-zinc-400">
                ({history.length})
              </span>
            </div>
            {history.length > 0 && (
              <button
                type="button"
                onClick={handleClearHistory}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition-colors"
              >
                <TrashIcon className="w-4 h-4" />
                Clear all
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div className="text-center py-12 text-zinc-500 dark:text-zinc-400">
              <ClockIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No translation history yet</p>
              <p className="text-sm">Your translations will appear here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => (
                <HistoryItem
                  key={item.id}
                  item={item}
                  getLanguageName={getLanguageName}
                  onClick={() => handleHistoryItemClick(item)}
                  onDelete={() => handleDeleteHistoryItem(item.id)}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;
