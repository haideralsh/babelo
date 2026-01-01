import * as Headless from "@headlessui/react";
import clsx from "clsx";
import { VolumeIcon, StopIcon } from "./icons";
import type { Voice } from "../hooks/useSpeechSynthesis";
import { ListboxOption, ListboxLabel, ListboxDescription } from "./ui/listbox";

interface VoiceSplitButtonProps {
  voices: Voice[];
  selectedVoice: SpeechSynthesisVoice | null;
  onVoiceChange: (voice: SpeechSynthesisVoice | null) => void;
  onSpeak: () => void;
  onStop: () => void;
  speaking?: boolean;
  disabled?: boolean;
}

export function VoiceSplitButton({
  voices,
  selectedVoice,
  onVoiceChange,
  onSpeak,
  onStop,
  speaking = false,
  disabled = false,
}: VoiceSplitButtonProps) {
  const isDisabled = disabled || voices.length === 0;

  const selectedVoiceObj = voices.find(
    (v) => v.voice.name === selectedVoice?.name
  );

  const handleVoiceChange = (voice: Voice | null) => {
    onVoiceChange(voice?.voice ?? null);
  };

  return (
    <div className="relative">
      <div
        className={`inline-flex items-stretch transition-colors ${
          isDisabled ? "opacity-50 cursor-not-allowed" : ""
        }`}
      >
        <button
          type="button"
          onClick={speaking ? onStop : onSpeak}
          disabled={isDisabled}
          className={`h-8 px-2.5 inline-flex items-center justify-center transition-colors ${
            speaking
              ? "text-red-500 hover:text-red-600"
              : "text-zinc-600 hover:text-zinc-900"
          } disabled:cursor-not-allowed`}
          aria-label={speaking ? "Stop" : "Listen"}
        >
          {speaking ? (
            <StopIcon className="w-4 h-4" />
          ) : (
            <VolumeIcon className="w-4 h-4" />
          )}
        </button>

        <Headless.Listbox
          value={selectedVoiceObj ?? null}
          onChange={handleVoiceChange}
          disabled={isDisabled}
        >
          <Headless.ListboxButton
            className={clsx(
              "h-8 px-1.5 inline-flex items-center justify-center transition-colors",
              "focus:outline-none",
              speaking
                ? "text-red-400 hover:text-red-500"
                : "text-zinc-400 hover:text-zinc-600",
              "disabled:cursor-not-allowed"
            )}
            aria-label="Select voice"
          >
            {({ open }) => (
              <svg
                className={clsx(
                  "w-3.5 h-3.5 transition-transform",
                  open && "rotate-180"
                )}
                viewBox="0 0 16 16"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M4.22 6.22a.75.75 0 0 1 1.06 0L8 8.94l2.72-2.72a.75.75 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 7.28a.75.75 0 0 1 0-1.06Z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </Headless.ListboxButton>

          <Headless.ListboxOptions
            transition
            anchor="bottom start"
            className={clsx(
              "[--anchor-gap:0.25rem] [--anchor-padding:--spacing(4)]",
              "isolate min-w-[180px] max-h-[240px] scroll-py-1 rounded-xl p-1 select-none",
              "outline outline-transparent focus:outline-hidden",
              "overflow-y-auto overscroll-contain",
              "bg-white/75 backdrop-blur-xl",
              "shadow-lg ring-1 ring-zinc-950/10",
              "transition-opacity duration-100 ease-in data-closed:data-leave:opacity-0 data-transition:pointer-events-none",
              "z-50"
            )}
          >
            {voices.length === 0 ? (
              <div className="px-3 py-2 text-sm text-zinc-400">
                No voices available
              </div>
            ) : (
              voices.map((voice) => {
                const nameMatch = voice.name.match(/^([^(]+)/);
                const cleanName = nameMatch ? nameMatch[1].trim() : voice.name;

                return (
                  <ListboxOption key={voice.voice.name} value={voice}>
                    <ListboxLabel>{cleanName}</ListboxLabel>
                    <ListboxDescription>{voice.lang}</ListboxDescription>
                  </ListboxOption>
                );
              })
            )}
          </Headless.ListboxOptions>
        </Headless.Listbox>
      </div>
    </div>
  );
}
