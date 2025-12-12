import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { VoiceSelector } from "./VoiceSelector";
import { CopyIcon, CheckIcon, VolumeIcon, StopIcon } from "./icons";
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
      className={`bg-white rounded-xl border border-zinc-200 overflow-hidden flex flex-col ${
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
          className="border-0 rounded-none"
        />
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-zinc-200 bg-zinc-50/50">
        <div className="flex items-center gap-2">
          {ttsSupported && (
            <>
              <div className="w-40">
                <VoiceSelector
                  voices={availableVoices}
                  selectedVoice={selectedVoice}
                  onVoiceChange={onVoiceChange}
                  disabled={!value || speaking}
                />
              </div>
              <button
                type="button"
                onClick={speaking ? onStop : onSpeak}
                disabled={!value || availableVoices.length === 0}
                className={`h-8 w-8 p-0 inline-flex items-center justify-center rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${
                  speaking
                    ? "text-red-500 hover:text-red-600 hover:bg-red-50"
                    : "text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100"
                }`}
                aria-label={speaking ? "Stop" : "Listen"}
              >
                {speaking ? (
                  <StopIcon className="w-4 h-4" />
                ) : (
                  <VolumeIcon className="w-4 h-4" />
                )}
              </button>
            </>
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
            className="h-8 w-8 p-0 inline-flex items-center justify-center rounded-lg text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
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
