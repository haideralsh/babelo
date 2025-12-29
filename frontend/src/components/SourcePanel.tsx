import { useState } from "react";
import { Textarea } from "./ui/textarea";
import { VoiceSplitButton } from "./VoiceSplitButton";
import { CopyIcon, CheckIcon } from "./icons";
import type { Voice } from "../hooks/useSpeechSynthesis";

export interface SourcePanelProps {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  availableVoices: Voice[];
  selectedVoice: SpeechSynthesisVoice | null;
  onVoiceChange: (voice: SpeechSynthesisVoice | null) => void;
  onSpeak: () => void;
  onStop: () => void;
  speaking?: boolean;
  ttsSupported?: boolean;
}

export function SourcePanel({
  value,
  onChange,
  placeholder,
  availableVoices,
  selectedVoice,
  onVoiceChange,
  onSpeak,
  onStop,
  speaking = false,
  ttsSupported = false,
}: SourcePanelProps) {
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
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        resizable={false}
        rows={5}
        className="border-0 bg-white/75 rounded-xl ring-1 ring-zinc-950/10 pb-12"
      />
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
