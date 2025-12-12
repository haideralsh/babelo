import { useState, useEffect, useRef } from "react";
import { LanguageSelector, type Language } from "./components/LanguageSelector";
import { useSpeechSynthesis } from "./hooks/useSpeechSynthesis";
import { Button } from "./components/ui/button";
import { TranslationPanel } from "./components/TranslationPanel";
import { type HistoryItemData } from "./components/HistoryItem";
import { HistorySidebar } from "./components/HistorySidebar";
import { getRecentLanguages, addRecentLanguage } from "./utils/languageStorage";
import {
  API_BASE_URL,
  DEBOUNCE_DELAY,
  LS_SOURCE_LANGS_KEY,
  LS_TARGET_LANGS_KEY,
} from "./utils/constants";
import {
  Alert,
  AlertTitle,
  AlertDescription,
  AlertActions,
} from "./components/ui/alert";
import {
  LanguagesIcon,
  ArrowRightLeftIcon,
  ClockIcon,
} from "./components/icons";

export function TranslatorApp() {
  const [inputText, setInputText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [languages, setLanguages] = useState<Language[]>([]);
  const [sourceLanguage, setSourceLanguageState] = useState("");
  const [targetLanguage, setTargetLanguageState] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<HistoryItemData[]>([]);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [isSwapRotating, setIsSwapRotating] = useState(false);
  const [showHistorySidebar, setShowHistorySidebar] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const { speak, stop, speaking, getVoicesForLanguage, isLanguageSupported } =
    useSpeechSynthesis();

  // Track which panel is currently speaking
  const [speakingPanel, setSpeakingPanel] = useState<
    "source" | "target" | null
  >(null);

  // Reset speakingPanel when speech stops
  useEffect(() => {
    if (!speaking) {
      setSpeakingPanel(null);
    }
  }, [speaking]);

  const [sourceVoice, setSourceVoiceState] =
    useState<SpeechSynthesisVoice | null>(null);
  const [targetVoice, setTargetVoiceState] =
    useState<SpeechSynthesisVoice | null>(null);

  const sourceVoices = getVoicesForLanguage(sourceLanguage);
  const targetVoices = getVoicesForLanguage(targetLanguage);
  const sourceTtsSupported = isLanguageSupported(sourceLanguage);
  const targetTtsSupported = isLanguageSupported(targetLanguage);

  // Helper functions for voice preference API
  const saveVoicePreference = async (langCode: string, voiceName: string) => {
    try {
      await fetch(`${API_BASE_URL}/preferences/voice_preference:${langCode}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value: voiceName }),
      });
    } catch (err) {
      console.error("Error saving voice preference:", err);
    }
  };

  const loadVoicePreference = async (
    langCode: string
  ): Promise<string | null> => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/preferences/voice_preference:${langCode}`
      );
      if (response.ok) {
        const data = await response.json();
        return data.value;
      }
    } catch (err) {
      // Preference not found or error - will use default voice
    }
    return null;
  };

  // Wrapper setters that save voice preference to database
  const setSourceVoice = (voice: SpeechSynthesisVoice | null) => {
    setSourceVoiceState(voice);
    if (voice && sourceLanguage) {
      saveVoicePreference(sourceLanguage, voice.name);
    }
  };

  const setTargetVoice = (voice: SpeechSynthesisVoice | null) => {
    setTargetVoiceState(voice);
    if (voice && targetLanguage) {
      saveVoicePreference(targetLanguage, voice.name);
    }
  };

  // Load saved voice preference when source language changes
  useEffect(() => {
    if (sourceVoices.length === 0 || !sourceLanguage) return;

    const loadSavedVoice = async () => {
      const savedVoiceName = await loadVoicePreference(sourceLanguage);
      if (savedVoiceName) {
        const savedVoice = sourceVoices.find(
          (v) => v.voice.name === savedVoiceName
        );
        if (savedVoice) {
          setSourceVoiceState(savedVoice.voice);
          return;
        }
      }

      if (
        !sourceVoice ||
        !sourceVoices.some((v) => v.voice.name === sourceVoice.name)
      ) {
        setSourceVoiceState(sourceVoices[0].voice);
      }
    };

    loadSavedVoice();
  }, [sourceLanguage, sourceVoices]);

  // Load saved voice preference when target language changes
  useEffect(() => {
    if (targetVoices.length === 0 || !targetLanguage) return;

    const loadSavedVoice = async () => {
      const savedVoiceName = await loadVoicePreference(targetLanguage);
      if (savedVoiceName) {
        const savedVoice = targetVoices.find(
          (v) => v.voice.name === savedVoiceName
        );
        if (savedVoice) {
          setTargetVoiceState(savedVoice.voice);
          return;
        }
      }
      if (
        !targetVoice ||
        !targetVoices.some((v) => v.voice.name === targetVoice.name)
      ) {
        setTargetVoiceState(targetVoices[0].voice);
      }
    };

    loadSavedVoice();
  }, [targetLanguage, targetVoices]);

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

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      if (!response.ok) return;
      const data = await response.json();
      // Map API response to HistoryItemData format
      const items: HistoryItemData[] = data.items.map(
        (item: {
          id: string;
          source_text: string;
          translated_text: string;
          source_lang: string;
          target_lang: string;
          timestamp: string;
        }) => ({
          id: item.id,
          sourceText: item.source_text,
          translatedText: item.translated_text,
          sourceLang: item.source_lang,
          targetLang: item.target_lang,
          timestamp: item.timestamp,
        })
      );
      setHistory(items);
    } catch (err) {
      console.error("Error fetching history:", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleTranslate = async () => {
    if (!inputText.trim() || !translatedText.trim()) return;

    try {
      await fetch(`${API_BASE_URL}/history`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          source_text: inputText,
          translated_text: translatedText,
          source_lang: sourceLanguage,
          target_lang: targetLanguage,
        }),
      });
      // Refresh the history list
      await fetchHistory();
    } catch (err) {
      console.error("Error saving history:", err);
    }
  };

  const handleClearHistory = async () => {
    try {
      await fetch(`${API_BASE_URL}/history`, {
        method: "DELETE",
      });
      setHistory([]);
    } catch (err) {
      console.error("Error clearing history:", err);
    }
  };

  const handleDeleteHistoryItem = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/history/${id}`, {
        method: "DELETE",
      });
      setHistory(history.filter((item) => item.id !== id));
    } catch (err) {
      console.error("Error deleting history item:", err);
    }
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
    <div className="flex h-screen bg-zinc-50 overflow-hidden">
      <main className="flex-1 min-w-0 h-full overflow-y-auto">
        <div className="max-w-5xl mx-auto px-4 py-8 md:py-12 pb-24">
          <header className="flex items-center gap-3 mb-8">
            <div className="p-2 bg-blue-500/10 rounded-xl">
              <LanguagesIcon className="w-6 h-6 text-blue-600" />
            </div>
            <h1 className="text-2xl font-semibold text-zinc-900">
              Bab Translator
            </h1>
          </header>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

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
              onClick={() => {
                setIsSwapRotating((r) => !r);
                handleSwapLanguages();
              }}
              disabled={loading}
              className="rounded-full p-2 text-zinc-500 hover:text-blue-500 hover:bg-blue-500/20 transition-colors shrink-0 mt-5 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Swap languages"
            >
              <ArrowRightLeftIcon
                className={`w-5 h-5 transition-transform duration-300 ${
                  isSwapRotating ? "rotate-180" : ""
                }`}
              />
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
              availableVoices={sourceVoices}
              selectedVoice={sourceVoice}
              onVoiceChange={setSourceVoice}
              onSpeak={() => {
                setSpeakingPanel("source");
                speak(inputText, sourceVoice ?? undefined);
              }}
              onStop={stop}
              speaking={speakingPanel === "source"}
              ttsSupported={sourceTtsSupported}
            />

            <TranslationPanel
              value={translatedText}
              placeholder="Translation will appear here..."
              readOnly
              language={getLanguageName(targetLanguage)}
              loading={loading}
              availableVoices={targetVoices}
              selectedVoice={targetVoice}
              onVoiceChange={setTargetVoice}
              onSpeak={() => {
                setSpeakingPanel("target");
                speak(translatedText, targetVoice ?? undefined);
              }}
              onStop={stop}
              speaking={speakingPanel === "target"}
              ttsSupported={targetTtsSupported}
            />
          </div>

          <div className="flex justify-center">
            <button
              type="button"
              onClick={handleTranslate}
              disabled={!inputText.trim() || !translatedText.trim()}
              className="px-8 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Save to History
            </button>
          </div>

          <div
            className={`fixed bottom-6 right-6 transition-all duration-300 transform ${
              showHistorySidebar
                ? "translate-x-20 opacity-0 pointer-events-none"
                : "translate-x-0 opacity-100"
            }`}
          >
            <button
              type="button"
              onClick={() => setShowHistorySidebar(true)}
              className="flex items-center gap-2 px-4 py-3 bg-zinc-900 text-white rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
            >
              <ClockIcon className="w-5 h-5" />
              <span className="font-medium">History</span>
              {history.length > 0 && (
                <span className="flex items-center justify-center min-w-5 h-5 px-1.5 bg-blue-500 text-white text-xs font-semibold rounded-full">
                  {history.length}
                </span>
              )}
            </button>
          </div>

          <Alert
            open={showClearConfirm}
            onClose={() => setShowClearConfirm(false)}
          >
            <AlertTitle>Clear all history?</AlertTitle>
            <AlertDescription>
              This will permanently delete all your translation history. This
              action cannot be undone.
            </AlertDescription>
            <AlertActions>
              <Button plain onClick={() => setShowClearConfirm(false)}>
                Cancel
              </Button>
              <Button
                color="red"
                onClick={() => {
                  handleClearHistory();
                  setShowClearConfirm(false);
                }}
              >
                Clear All
              </Button>
            </AlertActions>
          </Alert>
        </div>
      </main>

      <HistorySidebar
        open={showHistorySidebar}
        onClose={() => setShowHistorySidebar(false)}
        history={history}
        onHistoryItemClick={handleHistoryItemClick}
        onDeleteHistoryItem={handleDeleteHistoryItem}
        onClearAll={() => setShowClearConfirm(true)}
        getLanguageName={getLanguageName}
      />
    </div>
  );
}
