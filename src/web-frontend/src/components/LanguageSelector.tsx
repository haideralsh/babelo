import { Combobox, ComboboxOption, ComboboxLabel } from "./ui/combobox";

export interface Language {
  name: string;
  code: string;
}

interface LanguageSelectorProps {
  languages: Language[];
  value: string;
  onChange: (value: string) => void;
  label: string;
  disabled?: boolean;
}

export function LanguageSelector({
  languages,
  value,
  onChange,
  label,
  disabled,
}: LanguageSelectorProps) {
  const selectedLanguage = languages.find((l) => l.code === value) ?? null;

  return (
    <div className="flex-1">
      <span className="text-xs text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-1 block">
        {label}
      </span>
      <Combobox
        options={languages}
        value={selectedLanguage}
        onChange={(lang: Language) => {
          if (lang) onChange(lang.code);
        }}
        displayValue={(lang) => lang?.name}
        placeholder="Select language"
        disabled={disabled}
        aria-label={label}
      >
        {(language) => (
          <ComboboxOption key={language.code} value={language}>
            <ComboboxLabel>{language.name}</ComboboxLabel>
          </ComboboxOption>
        )}
      </Combobox>
    </div>
  );
}
