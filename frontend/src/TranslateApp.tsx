import { useState, useEffect, useRef, useMemo } from "react";
import { LanguageSelector, type Language } from "./components/LanguageSelector";
import { useSpeechSynthesis } from "./hooks/useSpeechSynthesis";
import { SourcePanel } from "./components/SourcePanel";
import { TargetPanel } from "./components/TargetPanel";
import { type SavedTranslationData } from "./components/SavedTranslationItem";
import { getRecentLanguages, addRecentLanguage } from "./utils/languageStorage";
import { SavedSidebar, type SavedSidebarRef } from "./components/SavedSidebar";
import {
  ModelSelector,
  getSavedModelId,
  type ModelInfo,
  type ModelStatus,
} from "./components/ModelSelector";
import {
  API_BASE_URL,
  DEBOUNCE_DELAY,
  LS_SOURCE_LANGS_KEY,
  LS_TARGET_LANGS_KEY,
  LS_SELECTED_MODEL_KEY,
  DEFAULT_MODEL_ID,
} from "./utils/constants";
import {
  LanguagesIcon,
  ArrowRightLeftIcon,
  StarFilledIcon,
  CpuIcon,
} from "./components/icons";

export function TranslatorApp() {
  const [inputText, setInputText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [languages, setLanguages] = useState<Language[]>([]);
  const [sourceLanguage, setSourceLanguageState] = useState("");
  const [targetLanguage, setTargetLanguageState] = useState("");
  const [_loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isSwapRotating, setIsSwapRotating] = useState(false);
  const [showSavedSidebar, setShowSavedSidebar] = useState(false);
  const [isStarred, setIsStarred] = useState(false);
  const [starredItemId, setStarredItemId] = useState<string | null>(null);
  const [selectedModelId, setSelectedModelId] = useState(getSavedModelId());
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const savedSidebarRef = useRef<SavedSidebarRef>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const starCheckControllerRef = useRef<AbortController | null>(null);
  const loadedSourceVoiceLangsRef = useRef<Set<string>>(new Set());
  const loadedTargetVoiceLangsRef = useRef<Set<string>>(new Set());
  const sourceTextareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus the source textarea on mount
  useEffect(() => {
    sourceTextareaRef.current?.focus();
  }, []);

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

  // Fetch model status
  useEffect(() => {
    const fetchModelStatus = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/model/status?model_id=${selectedModelId}`
        );
        if (response.ok) {
          const data = await response.json();
          setModelStatus(data);
        }
      } catch (err) {
        console.error("Error fetching model status:", err);
      }
    };

    fetchModelStatus();
  }, [selectedModelId]);

  // Fetch languages for selected model
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/languages?model_id=${selectedModelId}`
        );
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
  }, [selectedModelId]);

  // Clear translation when model changes
  useEffect(() => {
    setTranslatedText("");
    setError("");
  }, [selectedModelId]);

  useEffect(() => {
    if (!inputText.trim()) {
      setTranslatedText("");
      setError("");
      return;
    }

    if (!sourceLanguage || !targetLanguage) {
      return;
    }

    // Don't translate if model is not downloaded
    if (!modelStatus?.is_downloaded) {
      return;
    }

    const timeoutId = setTimeout(async () => {
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
            model_id: selectedModelId,
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
  }, [inputText, sourceLanguage, targetLanguage, selectedModelId, modelStatus?.is_downloaded]);

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
        const response = await fetch(`${API_BASE_URL}/saved/check?${params}`, {
          signal: starCheckControllerRef.current?.signal,
        });

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

  const handleSaveTranslation = async () => {
    if (!inputText.trim() || !translatedText.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/saved`, {
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
      savedSidebarRef.current?.refreshSaved();
    } catch (err) {
      console.error("Error saving translation:", err);
    }
  };

  const handleUnsaveTranslation = async () => {
    if (!starredItemId) return;

    try {
      await fetch(`${API_BASE_URL}/saved/${starredItemId}`, {
        method: "DELETE",
      });
      setIsStarred(false);
      setStarredItemId(null);
      savedSidebarRef.current?.refreshSaved();
    } catch (err) {
      console.error("Error unsaving translation:", err);
    }
  };

  const handleSavedItemClick = (item: SavedTranslationData) => {
    setSourceLanguage(item.sourceLang);
    setTargetLanguage(item.targetLang);
    setInputText(item.sourceText);
    setTranslatedText(item.translatedText);
  };

  const handleModelChange = (modelId: string) => {
    setSelectedModelId(modelId);
    localStorage.setItem(LS_SELECTED_MODEL_KEY, modelId);
    // Fetch new model status
    fetch(`${API_BASE_URL}/model/status?model_id=${modelId}`)
      .then((res) => res.json())
      .then((data) => setModelStatus(data))
      .catch(console.error);
  };

  const getLanguageName = (code: string) => {
    return languages.find((l) => l.code === code)?.name || code;
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      <main className="flex-1 min-w-0 h-full overflow-y-auto">
        <div className="max-w-5xl mx-auto px-4 py-8 md:py-12 pb-24">
          <header className="flex items-center justify-between gap-3 mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-sky-3">
                <LanguagesIcon className="w-6 h-6 text-sky-11" />
              </div>
              <h1 className="text-2xl font-semibold text-zinc-900">
                Bab Translator
              </h1>
            </div>
            <button
              type="button"
              onClick={() => setShowModelSelector(!showModelSelector)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 rounded-lg transition-colors"
            >
              <CpuIcon className="w-4 h-4" />
              <span className="hidden sm:inline">
                {selectedModelId === "nllb" ? "NLLB-200" : "TranslateGemma"}
              </span>
            </button>
          </header>

          {showModelSelector && (
            <div className="mb-6 p-4 bg-zinc-50 rounded-lg border border-zinc-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-zinc-700">
                  Select Translation Model
                </h3>
                <button
                  type="button"
                  onClick={() => setShowModelSelector(false)}
                  className="text-zinc-500 hover:text-zinc-700"
                >
                  &times;
                </button>
              </div>
              <ModelSelector
                selectedModelId={selectedModelId}
                onModelChange={handleModelChange}
                onDownloadComplete={() => {
                  // Refresh model status
                  fetch(`${API_BASE_URL}/model/status?model_id=${selectedModelId}`)
                    .then((res) => res.json())
                    .then((data) => setModelStatus(data))
                    .catch(console.error);
                }}
              />
            </div>
          )}

          {!modelStatus?.is_downloaded && (
            <div className="mb-4 p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg">
              <p className="font-medium">Model not downloaded</p>
              <p className="text-sm mt-1">
                Click the model selector above to download{" "}
                {selectedModelId === "nllb" ? "NLLB-200" : "TranslateGemma"}{" "}
                before translating.
              </p>
            </div>
          )}

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

          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <SourcePanel
              ref={sourceTextareaRef}
              value={inputText}
              onChange={setInputText}
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
              placeholder="Translation"
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
              onSave={handleSaveTranslation}
              onUnsave={handleUnsaveTranslation}
              saveDisabled={!inputText.trim() || !translatedText.trim()}
              isStarred={isStarred}
            />
          </div>

          <div
            className={`flex justify-center transition-all duration-300 ${
              showSavedSidebar ? "opacity-0 pointer-events-none" : "opacity-100"
            }`}
          >
            <button
              type="button"
              onClick={() => setShowSavedSidebar(true)}
              className="flex flex-col items-center gap-1.5 group"
            >
              <div className="w-14 h-14 rounded-full bg-white border border-zinc-300 flex items-center justify-center transition-all duration-200">
                <StarFilledIcon className="w-5 h-5 text-zinc-400 transition-colors" />
              </div>
              <span className="text-sm text-zinc-500 transition-colors">
                Saved
              </span>
            </button>
          </div>
        </div>
      </main>

      <SavedSidebar
        ref={savedSidebarRef}
        open={showSavedSidebar}
        onClose={() => setShowSavedSidebar(false)}
        onSavedItemClick={handleSavedItemClick}
        getLanguageName={getLanguageName}
      />
    </div>
  );
}
