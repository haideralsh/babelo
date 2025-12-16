import * as Headless from "@headlessui/react";
import clsx from "clsx";
import { VolumeIcon, StopIcon } from "./icons";
import type { Voice } from "../hooks/useSpeechSynthesis";

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

  // Find the selected voice object from the voices array
  const selectedVoiceObj = voices.find(
    (v) => v.voice.name === selectedVoice?.name
  );

  const handleVoiceChange = (voice: Voice | null) => {
    onVoiceChange(voice?.voice ?? null);
  };

  return (
    <div className="relative">
      {/* Split Button Container */}
      <div
        className={`inline-flex items-stretch rounded-lg border transition-colors ${
          speaking
            ? "border-red-200 bg-red-50"
            : "border-zinc-200 bg-white hover:border-zinc-300"
        } ${isDisabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        {/* Primary Action - Speak/Stop */}
        <button
          type="button"
          onClick={speaking ? onStop : onSpeak}
          disabled={isDisabled}
          className={`h-8 px-2.5 inline-flex items-center justify-center transition-colors rounded-l-[7px] ${
            speaking
              ? "text-red-500 hover:text-red-600 hover:bg-red-100"
              : "text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100"
          } disabled:cursor-not-allowed`}
          aria-label={speaking ? "Stop" : "Listen"}
        >
          {speaking ? (
            <StopIcon className="w-4 h-4" />
          ) : (
            <VolumeIcon className="w-4 h-4" />
          )}
        </button>

        {/* Divider */}
        <div className={`w-px ${speaking ? "bg-red-200" : "bg-zinc-200"}`} />

        {/* Listbox Toggle */}
        <Headless.Listbox
          value={selectedVoiceObj ?? null}
          onChange={handleVoiceChange}
          disabled={isDisabled}
        >
          <Headless.ListboxButton
            className={clsx(
              "h-8 px-1.5 inline-flex items-center justify-center transition-colors rounded-r-[7px]",
              "focus:outline-none",
              speaking
                ? "text-red-400 hover:text-red-500 hover:bg-red-100 data-open:bg-red-100"
                : "text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 data-open:bg-zinc-100",
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
              // Anchor positioning
              "[--anchor-gap:0.25rem] [--anchor-padding:--spacing(4)]",
              // Base styles
              "isolate min-w-[180px] max-h-[240px] scroll-py-1 rounded-lg p-1 select-none",
              // Invisible border that is only visible in `forced-colors` mode for accessibility purposes
              "outline outline-transparent focus:outline-hidden",
              // Handle scrolling when menu won't fit in viewport
              "overflow-y-auto overscroll-contain",
              // Popover background
              "bg-white/75 backdrop-blur-xl",
              // Shadows
              "shadow-lg ring-1 ring-zinc-950/10",
              // Transitions
              "transition-opacity duration-100 ease-in data-closed:data-leave:opacity-0 data-transition:pointer-events-none",
              // Z-index
              "z-50"
            )}
          >
            {voices.length === 0 ? (
              <div className="px-3 py-2 text-sm text-zinc-400">
                No voices available
              </div>
            ) : (
              voices.map((voice) => (
                <Headless.ListboxOption
                  key={voice.voice.name}
                  value={voice}
                  className={clsx(
                    // Basic layout
                    "group/option grid cursor-default grid-cols-[--spacing(5)_1fr] items-baseline gap-x-2 rounded-lg py-2 pr-3 pl-2",
                    // Typography
                    "text-sm text-zinc-950",
                    // Focus
                    "outline-hidden data-focus:bg-blue-500 data-focus:text-white",
                    // Selected without focus
                    "data-selected:not-data-focus:bg-blue-50 data-selected:not-data-focus:text-blue-700"
                  )}
                >
                  <svg
                    className="relative hidden size-4 self-center stroke-current group-data-selected/option:inline"
                    viewBox="0 0 16 16"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M4 8.5l3 3L12 4"
                      strokeWidth={1.5}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <span className="col-start-2 truncate">{voice.name}</span>
                </Headless.ListboxOption>
              ))
            )}
          </Headless.ListboxOptions>
        </Headless.Listbox>
      </div>
    </div>
  );
}
