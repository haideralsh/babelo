import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { VoiceSplitButton } from "./VoiceSplitButton";
import { CopyIcon, CheckIcon } from "./icons";
import type { Voice } from "../hooks/useSpeechSynthesis";

export interface TranslationPanelProps {
  value: string;
  onChange?: (value: string) => void;
  placeholder: string;
  isSource?: boolean;
  readOnly?: boolean;
  language: string;
  loading?: boolean;
  availableVoices: Voice[];
  selectedVoice: SpeechSynthesisVoice | null;
  onVoiceChange: (voice: SpeechSynthesisVoice | null) => void;
  onSpeak: () => void;
  onStop: () => void;
  speaking?: boolean;
  ttsSupported?: boolean;
}

export function TranslationPanel({
  value,
  onChange,
  placeholder,
  isSource = false,
  readOnly = false,
  language: _language,
  loading: _loading = false,
  availableVoices,
  selectedVoice,
  onVoiceChange,
  onSpeak,
  onStop,
  speaking = false,
  ttsSupported = false,
}: TranslationPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const characterCount = value.length;

  return (
    <div
      className={`bg-white border border-zinc-200 flex flex-col ${
        readOnly ? "bg-zinc-50" : ""
      }`}
    >
      {/* Text Area */}
      <div className="relative flex-1">
        <Textarea
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={placeholder}
          disabled={readOnly}
          resizable={false}
          rows={8}
          className="border-0"
        />
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-zinc-200 bg-zinc-50/50">
        <div className="flex items-center gap-2">
          {ttsSupported && (
            <VoiceSplitButton
              voices={availableVoices}
              selectedVoice={selectedVoice}
              onVoiceChange={onVoiceChange}
              onSpeak={onSpeak}
              onStop={onStop}
              speaking={speaking}
              disabled={!value}
            />
          )}
          {!ttsSupported && (
            <span className="text-xs text-zinc-400 italic">
              Text-to-speech not available for this language
            </span>
          )}
          <button
            type="button"
            onClick={handleCopy}
            disabled={!value}
            className="h-8 w-8 p-0 inline-flex items-center justify-center text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
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
          <span className="text-xs text-zinc-500">{characterCount} / 5000</span>
        )}
      </div>
    </div>
  );
}
