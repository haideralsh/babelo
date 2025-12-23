import {
  useState,
  useEffect,
  useCallback,
  forwardRef,
  useImperativeHandle,
} from "react";
import { ClockIcon, TrashIcon, XIcon } from "./icons";
import { HistoryItem, type HistoryItemData } from "./HistoryItem";
import { Button } from "./ui/button";
import { Alert, AlertTitle, AlertDescription, AlertActions } from "./ui/alert";
import { API_BASE_URL } from "../utils/constants";

interface HistorySidebarProps {
  open: boolean;
  onClose: () => void;
  onHistoryItemClick: (item: HistoryItemData) => void;
  getLanguageName: (code: string) => string;
}

export interface HistorySidebarRef {
  refreshHistory: () => void;
}

export const HistorySidebar = forwardRef<
  HistorySidebarRef,
  HistorySidebarProps
>(function HistorySidebar(
  { open, onClose, onHistoryItemClick, getLanguageName },
  ref
) {
  const [history, setHistory] = useState<HistoryItemData[]>([]);
  const [loading, setLoading] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [hasFetched, setHasFetched] = useState(false);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/history`);
      if (!response.ok) return;
      const data = await response.json();
      // Map API response to HistoryItemData format
      const items: HistoryItemData[] = data.items.map(
        (item: {
          id: string;
          source_text: string;
          translated_text: string;
          source_lang: string;
          target_lang: string;
          timestamp: string;
        }) => ({
          id: item.id,
          sourceText: item.source_text,
          translatedText: item.translated_text,
          sourceLang: item.source_lang,
          targetLang: item.target_lang,
          timestamp: item.timestamp,
        })
      );
      setHistory(items);
    } catch (err) {
      console.error("Error fetching history:", err);
    } finally {
      setLoading(false);
      setHasFetched(true);
    }
  }, []);

  useImperativeHandle(
    ref,
    () => ({
      refreshHistory: fetchHistory,
    }),
    [fetchHistory]
  );

  useEffect(() => {
    if (open && !hasFetched) {
      fetchHistory();
    }
  }, [open, hasFetched, fetchHistory]);

  const handleClearHistory = async () => {
    try {
      await fetch(`${API_BASE_URL}/history`, {
        method: "DELETE",
      });
      setHistory([]);
    } catch (err) {
      console.error("Error clearing history:", err);
    }
  };

  const handleDeleteHistoryItem = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/history/${id}`, {
        method: "DELETE",
      });
      setHistory(history.filter((item) => item.id !== id));
    } catch (err) {
      console.error("Error deleting history item:", err);
    }
  };

  return (
    <>
      <div
        className={`${
          open ? "w-120 border-l" : "w-0"
        } bg-white border-zinc-200 transition-[width] duration-300 ease-in-out overflow-hidden shrink-0 h-screen sticky top-0`}
      >
        <div className="w-120 h-full flex flex-col">
          <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 shrink-0">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center bg-blue-500/10">
                <ClockIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-zinc-900">History</h2>
                <p className="text-sm text-zinc-500">
                  {loading
                    ? "Loading..."
                    : `${history.length} translation${
                        history.length !== 1 ? "s" : ""
                      }`}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="p-2 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 transition-colors"
            >
              <XIcon className="h-5 w-5" />
            </button>
          </div>

          {history.length > 0 && (
            <div className="flex items-center justify-end border-b border-zinc-200 px-6 py-3 shrink-0">
              <button
                type="button"
                onClick={() => setShowClearConfirm(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
              >
                <TrashIcon className="h-4 w-4" />
                Clear all
              </button>
            </div>
          )}

          <div className="flex-1 overflow-y-auto px-6 py-4">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-zinc-500">
                <p className="font-medium">Loading history...</p>
              </div>
            ) : history.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-zinc-500">
                <div className="bg-zinc-100 p-4 mb-4">
                  <ClockIcon className="h-8 w-8 opacity-50" />
                </div>
                <p className="font-medium">No history yet</p>
                <p className="text-sm mt-1">
                  Your translations will appear here
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <HistoryItem
                    key={item.id}
                    item={item}
                    getLanguageName={getLanguageName}
                    onClick={() => {
                      onHistoryItemClick(item);
                    }}
                    onDelete={() => handleDeleteHistoryItem(item.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <Alert open={showClearConfirm} onClose={() => setShowClearConfirm(false)}>
        <AlertTitle>Clear all history?</AlertTitle>
        <AlertDescription>
          This will permanently delete all your translation history. This action
          cannot be undone.
        </AlertDescription>
        <AlertActions>
          <Button plain onClick={() => setShowClearConfirm(false)}>
            Cancel
          </Button>
          <Button
            color="red"
            onClick={() => {
              handleClearHistory();
              setShowClearConfirm(false);
            }}
          >
            Clear All
          </Button>
        </AlertActions>
      </Alert>
    </>
  );
});
