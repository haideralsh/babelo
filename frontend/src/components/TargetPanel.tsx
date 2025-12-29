import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { VoiceSplitButton } from "./VoiceSplitButton";
import { CopyIcon, CheckIcon, StarOutlineIcon, StarFilledIcon } from "./icons";
import type { Voice } from "../hooks/useSpeechSynthesis";

export interface TargetPanelProps {
  value: string;
  placeholder: string;
  availableVoices: Voice[];
  selectedVoice: SpeechSynthesisVoice | null;
  onVoiceChange: (voice: SpeechSynthesisVoice | null) => void;
  onSpeak: () => void;
  onStop: () => void;
  speaking?: boolean;
  ttsSupported?: boolean;
  onSave?: () => void;
  onUnsave?: () => void;
  saveDisabled?: boolean;
  isStarred?: boolean;
}

export function TargetPanel({
  value,
  placeholder,
  availableVoices,
  selectedVoice,
  onVoiceChange,
  onSpeak,
  onStop,
  speaking = false,
  ttsSupported = false,
  onSave,
  onUnsave,
  saveDisabled = true,
  isStarred = false,
}: TargetPanelProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <Textarea
        value={value}
        placeholder={placeholder}
        disabled
        resizable={false}
        rows={5}
        className="border-0 bg-white/75 rounded-xl ring-1 ring-zinc-950/10 pb-12"
      />
      {onSave && !saveDisabled && (
        <button
          type="button"
          onClick={isStarred ? onUnsave : onSave}
          className="absolute top-2 right-2 p-1.5 transition-colors disabled:opacity-30 disabled:cursor-not-allowed z-10"
          title="Save to History"
        >
          {isStarred ? (
            <StarFilledIcon className="w-5 h-5 text-amber-400 hover:text-amber-500" />
          ) : (
            <StarOutlineIcon className="w-5 h-5 text-zinc-400 hover:text-zinc-500" />
          )}
        </button>
      )}
      <div className="absolute bottom-2 left-2 flex items-center gap-2">
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
          className="h-8 w-8 p-0 inline-flex items-center justify-center text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 rounded-md disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
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
  );
}
