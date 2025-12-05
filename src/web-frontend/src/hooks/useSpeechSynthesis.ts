import { useState, useEffect, useCallback } from "react";

export interface Voice {
  voice: SpeechSynthesisVoice;
  name: string;
  lang: string;
}

export interface UseSpeechSynthesisResult {
  voices: Voice[];
  speaking: boolean;
  speak: (text: string, voice?: SpeechSynthesisVoice) => void;
  stop: () => void;
  getVoicesForLanguage: (langCode: string) => Voice[];
  isLanguageSupported: (langCode: string) => boolean;
}

const NLLB_TO_BCP47: Record<string, string[]> = {
  eng_Latn: ["en"],
  spa_Latn: ["es"],
  fra_Latn: ["fr"],
  deu_Latn: ["de"],
  ita_Latn: ["it"],
  por_Latn: ["pt"],
  nld_Latn: ["nl"],
  pol_Latn: ["pl"],
  rus_Cyrl: ["ru"],
  ukr_Cyrl: ["uk"],
  zho_Hans: ["zh-CN", "zh"],
  zho_Hant: ["zh-TW", "zh-HK"],
  jpn_Jpan: ["ja"],
  kor_Hang: ["ko"],
  arb_Arab: ["ar"],
  hin_Deva: ["hi"],
  ben_Beng: ["bn"],
  tur_Latn: ["tr"],
  vie_Latn: ["vi"],
  tha_Thai: ["th"],
  ind_Latn: ["id"],
  msa_Latn: ["ms"],
  swe_Latn: ["sv"],
  dan_Latn: ["da"],
  nor_Latn: ["no", "nb"],
  fin_Latn: ["fi"],
  ces_Latn: ["cs"],
  ell_Grek: ["el"],
  hun_Latn: ["hu"],
  ron_Latn: ["ro"],
  heb_Hebr: ["he"],
  cat_Latn: ["ca"],
  slk_Latn: ["sk"],
  bul_Cyrl: ["bg"],
  hrv_Latn: ["hr"],
  lit_Latn: ["lt"],
  slv_Latn: ["sl"],
  lvs_Latn: ["lv"],
  est_Latn: ["et"],
  tgl_Latn: ["tl", "fil"],
};

function nllbToBcp47(nllbCode: string): string[] {
  return NLLB_TO_BCP47[nllbCode] || [];
}

export function useSpeechSynthesis(): UseSpeechSynthesisResult {
  const [voices, setVoices] = useState<Voice[]>([]);
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    const loadVoices = () => {
      const synthVoices = speechSynthesis.getVoices();
      const mappedVoices: Voice[] = synthVoices.map((voice) => ({
        voice,
        name: voice.name,
        lang: voice.lang,
      }));
      setVoices(mappedVoices);
    };

    loadVoices();
    speechSynthesis.addEventListener("voiceschanged", loadVoices);

    return () => {
      speechSynthesis.removeEventListener("voiceschanged", loadVoices);
    };
  }, []);

  useEffect(() => {
    return () => {
      speechSynthesis.cancel();
    };
  }, []);

  const getVoicesForLanguage = useCallback(
    (nllbLangCode: string): Voice[] => {
      const bcp47Codes = nllbToBcp47(nllbLangCode);
      if (bcp47Codes.length === 0) return [];

      return voices.filter((v) => {
        const voiceLang = v.lang.toLowerCase();
        return bcp47Codes.some((code) => {
          const lowerCode = code.toLowerCase();
          return (
            voiceLang === lowerCode ||
            voiceLang.startsWith(lowerCode + "-") ||
            voiceLang.split("-")[0] === lowerCode
          );
        });
      });
    },
    [voices]
  );

  const isLanguageSupported = useCallback(
    (nllbLangCode: string): boolean => {
      return getVoicesForLanguage(nllbLangCode).length > 0;
    },
    [getVoicesForLanguage]
  );

  const speak = useCallback(
    (text: string, voice?: SpeechSynthesisVoice) => {
      if (!text) return;

      speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      if (voice) {
        utterance.voice = voice;
        utterance.lang = voice.lang;
      }

      utterance.onstart = () => setSpeaking(true);
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);

      speechSynthesis.speak(utterance);
    },
    []
  );

  const stop = useCallback(() => {
    speechSynthesis.cancel();
    setSpeaking(false);
  }, []);

  return {
    voices,
    speaking,
    speak,
    stop,
    getVoicesForLanguage,
    isLanguageSupported,
  };
}
