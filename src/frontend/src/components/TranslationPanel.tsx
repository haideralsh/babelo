import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { VoiceSplitButton } from "./VoiceSplitButton";
import { CopyIcon, CheckIcon, StarOutlineIcon, StarFilledIcon } from "./icons";
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
  onSave?: () => void;
  saveDisabled?: boolean;
  isStarred?: boolean;
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
  onSave,
  saveDisabled = true,
  isStarred = false,
}: TranslationPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`relative bg-white flex flex-col ${
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
        {/* Save to History Button - inside textarea area */}
        {isSource && onSave && !saveDisabled && (
          <button
            type="button"
            onClick={onSave}
            className="absolute top-2 right-2 p-1.5 text-amber-400 hover:text-amber-500 transition-colors disabled:opacity-30 disabled:cursor-not-allowed z-10"
            title="Save to History"
          >
            {isStarred ? (
              <StarFilledIcon className="w-5 h-5" />
            ) : (
              <StarOutlineIcon className="w-5 h-5" />
            )}
          </button>
        )}
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-zinc-50/50">
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
      </div>
    </div>
  );
}
