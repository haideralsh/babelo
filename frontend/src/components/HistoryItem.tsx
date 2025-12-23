import { Badge } from "./ui/badge";
import { ArrowRightIcon, XIcon } from "./icons";

export interface HistoryItemData {
  id: string;
  sourceText: string;
  translatedText: string;
  sourceLang: string;
  targetLang: string;
  timestamp: string;
}

interface HistoryItemProps {
  item: HistoryItemData;
  getLanguageName: (code: string) => string;
  onClick: () => void;
  onDelete: () => void;
}

export function HistoryItem({
  item,
  getLanguageName,
  onClick,
  onDelete,
}: HistoryItemProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      className="group relative bg-white border border-zinc-200 p-4 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
      onClick={onClick}
    >
      {/* Delete Button */}
      <button
        type="button"
        onClick={(e: React.MouseEvent) => {
          e.stopPropagation();
          onDelete();
        }}
        className="absolute top-2 right-2 h-7 w-7 p-0 inline-flex items-center justify-center text-zinc-500 hover:text-zinc-900 hover:bg-zinc-100 opacity-0 group-hover:opacity-100 transition-opacity"
        aria-label="Delete"
      >
        <XIcon className="w-4 h-4" />
      </button>

      {/* Language Direction */}
      <div className="flex items-center gap-2 mb-2">
        <Badge color="zinc">{getLanguageName(item.sourceLang)}</Badge>
        <ArrowRightIcon className="w-3 h-3 text-zinc-400" />
        <Badge color="zinc">{getLanguageName(item.targetLang)}</Badge>
        <span className="text-xs text-zinc-500 ml-auto">
          {formatTime(item.timestamp)}
        </span>
      </div>

      {/* Text Content */}
      <div className="grid md:grid-cols-2 gap-3">
        <p className="text-sm text-zinc-900 line-clamp-2">{item.sourceText}</p>
        <p className="text-sm text-zinc-500 line-clamp-2">
          {item.translatedText}
        </p>
      </div>
    </div>
  );
}
