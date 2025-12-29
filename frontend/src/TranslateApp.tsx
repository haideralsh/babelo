import { useState, useEffect, useRef, useMemo } from "react";
import { LanguageSelector, type Language } from "./components/LanguageSelector";
import { useSpeechSynthesis } from "./hooks/useSpeechSynthesis";
import { SourcePanel } from "./components/SourcePanel";
import { TargetPanel } from "./components/TargetPanel";
import { type HistoryItemData } from "./components/HistoryItem";
import { getRecentLanguages, addRecentLanguage } from "./utils/languageStorage";
import {
  API_BASE_URL,
  DEBOUNCE_DELAY,
  LS_SOURCE_LANGS_KEY,
  LS_TARGET_LANGS_KEY,
} from "./utils/constants";
import {
  LanguagesIcon,
  ArrowRightLeftIcon,
  ClockIcon,
} from "./components/icons";
import {
  HistorySidebar,
  type HistorySidebarRef,
} from "./components/HistorySidebar";

export function TranslatorApp() {
  const [inputText, setInputText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [languages, setLanguages] = useState<Language[]>([]);
  const [sourceLanguage, setSourceLanguageState] = useState("");
  const [targetLanguage, setTargetLanguageState] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isSwapRotating, setIsSwapRotating] = useState(false);
  const [showHistorySidebar, setShowHistorySidebar] = useState(false);
  const [isStarred, setIsStarred] = useState(false);
  const [starredItemId, setStarredItemId] = useState<string | null>(null);
  const historySidebarRef = useRef<HistorySidebarRef>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const starCheckControllerRef = useRef<AbortController | null>(null);
  const loadedSourceVoiceLangsRef = useRef<Set<string>>(new Set());
  const loadedTargetVoiceLangsRef = useRef<Set<string>>(new Set());

  const { speak, stop, speaking, getVoicesForLanguage, isLanguageSupported } =
    useSpeechSynthesis();

  const [speakingPanel, setSpeakingPanel] = useState<
    "source" | "target" | null
  >(null);

  useEffect(() => {
    if (!speaking) {
      setSpeakingPanel(null);
    }
  }, [speaking]);

  const [sourceVoice, setSourceVoiceState] =
    useState<SpeechSynthesisVoice | null>(null);
  const [targetVoice, setTargetVoiceState] =
    useState<SpeechSynthesisVoice | null>(null);

  const sourceVoices = useMemo(
    () => getVoicesForLanguage(sourceLanguage),
    [getVoicesForLanguage, sourceLanguage]
  );
  const targetVoices = useMemo(
    () => getVoicesForLanguage(targetLanguage),
    [getVoicesForLanguage, targetLanguage]
  );
  const sourceTtsSupported = isLanguageSupported(sourceLanguage);
  const targetTtsSupported = isLanguageSupported(targetLanguage);

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

  useEffect(() => {
    if (sourceVoices.length === 0 || !sourceLanguage) return;

    if (loadedSourceVoiceLangsRef.current.has(sourceLanguage)) {
      if (
        !sourceVoice ||
        !sourceVoices.some((v) => v.voice.name === sourceVoice.name)
      ) {
        setSourceVoiceState(sourceVoices[0].voice);
      }
      return;
    }

    const loadSavedVoice = async () => {
      loadedSourceVoiceLangsRef.current.add(sourceLanguage);
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

  useEffect(() => {
    if (targetVoices.length === 0 || !targetLanguage) return;

    if (loadedTargetVoiceLangsRef.current.has(targetLanguage)) {
      if (
        !targetVoice ||
        !targetVoices.some((v) => v.voice.name === targetVoice.name)
      ) {
        setTargetVoiceState(targetVoices[0].voice);
      }
      return;
    }

    const loadSavedVoice = async () => {
      loadedTargetVoiceLangsRef.current.add(targetLanguage);
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

  const setSourceLanguage = (code: string) => {
    setSourceLanguageState(code);
    if (code) addRecentLanguage(LS_SOURCE_LANGS_KEY, code);
  };

  const setTargetLanguage = (code: string) => {
    setTargetLanguageState(code);
    if (code) addRecentLanguage(LS_TARGET_LANGS_KEY, code);
  };

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
          return;
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

  useEffect(() => {
    if (!inputText.trim() || !sourceLanguage || !targetLanguage) {
      setIsStarred(false);
      setStarredItemId(null);
      return;
    }

    if (starCheckControllerRef.current) {
      starCheckControllerRef.current.abort();
    }

    starCheckControllerRef.current = new AbortController();

    const checkStarred = async () => {
      try {
        const params = new URLSearchParams({
          source_text: inputText,
          source_lang: sourceLanguage,
          target_lang: targetLanguage,
        });
        const response = await fetch(
          `${API_BASE_URL}/history/check?${params}`,
          { signal: starCheckControllerRef.current?.signal }
        );

        if (response.ok) {
          const data = await response.json();
          setIsStarred(data.exists);
          setStarredItemId(data.id || null);
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }
      }
    };

    const timeoutId = setTimeout(checkStarred, 300);

    return () => {
      clearTimeout(timeoutId);
    };
  }, [inputText, sourceLanguage, targetLanguage]);

  const handleSwapLanguages = () => {
    const tempLang = sourceLanguage;
    setSourceLanguage(targetLanguage);
    setTargetLanguage(tempLang);

    const tempText = inputText;
    setInputText(translatedText);
    setTranslatedText(tempText);
  };

  const handleSaveToHistory = async () => {
    if (!inputText.trim() || !translatedText.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/history`, {
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
      const data = await response.json();
      setIsStarred(true);
      setStarredItemId(data.id);
      historySidebarRef.current?.refreshHistory();
    } catch (err) {
      console.error("Error saving history:", err);
    }
  };

  const handleUnsaveFromHistory = async () => {
    if (!starredItemId) return;

    try {
      await fetch(`${API_BASE_URL}/history/${starredItemId}`, {
        method: "DELETE",
      });
      setIsStarred(false);
      setStarredItemId(null);
      historySidebarRef.current?.refreshHistory();
    } catch (err) {
      console.error("Error unsaving from history:", err);
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
            <div className="p-2 bg-sky-3">
              <LanguagesIcon className="w-6 h-6 text-sky-11" />
            </div>
            <h1 className="text-2xl font-semibold text-zinc-900">
              Bab Translator
            </h1>
          </header>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between gap-2 mb-4">
            <LanguageSelector
              languages={languages}
              value={sourceLanguage}
              onChange={setSourceLanguage}
              label="From"
            />

            <button
              type="button"
              onClick={() => {
                setIsSwapRotating((r) => !r);
                handleSwapLanguages();
              }}
              className="p-2 text-zinc-500 rounded-full hover:text-sky-11 hover:bg-sky-4 transition-colors shrink-0 mt-5 disabled:opacity-50 disabled:cursor-not-allowed"
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
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <SourcePanel
              value={inputText}
              onChange={setInputText}
              placeholder="Enter text to translate..."
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

            <TargetPanel
              value={translatedText}
              placeholder="Translation will appear here..."
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
              onSave={handleSaveToHistory}
              onUnsave={handleUnsaveFromHistory}
              saveDisabled={!inputText.trim() || !translatedText.trim()}
              isStarred={isStarred}
            />
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
              className="flex items-center gap-2 px-4 py-3 bg-zinc-900 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200"
            >
              <ClockIcon className="w-5 h-5" />
              <span className="font-medium">History</span>
            </button>
          </div>
        </div>
      </main>

      <HistorySidebar
        ref={historySidebarRef}
        open={showHistorySidebar}
        onClose={() => setShowHistorySidebar(false)}
        onHistoryItemClick={handleHistoryItemClick}
        getLanguageName={getLanguageName}
      />
    </div>
  );
}
