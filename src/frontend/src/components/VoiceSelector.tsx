import { Select } from "./ui/select";
import type { Voice } from "../hooks/useSpeechSynthesis";

interface VoiceSelectorProps {
  voices: Voice[];
  selectedVoice: SpeechSynthesisVoice | null;
  onVoiceChange: (voice: SpeechSynthesisVoice | null) => void;
  disabled?: boolean;
}

export function VoiceSelector({
  voices,
  selectedVoice,
  onVoiceChange,
  disabled = false,
}: VoiceSelectorProps) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const voiceName = e.target.value;
    if (!voiceName) {
      onVoiceChange(null);
      return;
    }
    const voice = voices.find((v) => v.voice.name === voiceName);
    onVoiceChange(voice?.voice ?? null);
  };

  return (
    <Select
      value={selectedVoice?.name ?? ""}
      onChange={handleChange}
      disabled={disabled || voices.length === 0}
    >
      {voices.length === 0 ? (
        <option value="">No voices available</option>
      ) : (
        <>
          {voices.map((v) => (
            <option key={v.voice.name} value={v.voice.name}>
              {v.name}
            </option>
          ))}
        </>
      )}
    </Select>
  );
}
