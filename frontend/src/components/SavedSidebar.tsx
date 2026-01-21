import {
  useState,
  useEffect,
  useCallback,
  forwardRef,
  useImperativeHandle,
} from "react";
import { StarFilledIcon, TrashIcon, XIcon } from "./icons";
import {
  SavedTranslationItem,
  type SavedTranslationData,
} from "./SavedTranslationItem";
import { Button } from "./ui/button";
import { Alert, AlertTitle, AlertDescription, AlertActions } from "./ui/alert";
import { API_BASE_URL } from "../utils/constants";

interface SavedSidebarProps {
  open: boolean;
  onClose: () => void;
  onSavedItemClick: (item: SavedTranslationData) => void;
  getLanguageName: (code: string) => string;
}

export interface SavedSidebarRef {
  refreshSaved: () => void;
}

export const SavedSidebar = forwardRef<SavedSidebarRef, SavedSidebarProps>(
  function SavedSidebar(
    { open, onClose, onSavedItemClick, getLanguageName },
    ref
  ) {
    const [savedTranslations, setSavedTranslations] = useState<
      SavedTranslationData[]
    >([]);
    const [loading, setLoading] = useState(false);
    const [showClearConfirm, setShowClearConfirm] = useState(false);
    const [hasFetched, setHasFetched] = useState(false);

    const fetchSavedTranslations = useCallback(async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/saved`);
        if (!response.ok) return;
        const data = await response.json();
        const items: SavedTranslationData[] = data.items.map(
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
        setSavedTranslations(items);
      } catch (err) {
        console.error("Error fetching saved translations:", err);
      } finally {
        setLoading(false);
        setHasFetched(true);
      }
    }, []);

    useImperativeHandle(
      ref,
      () => ({
        refreshSaved: fetchSavedTranslations,
      }),
      [fetchSavedTranslations]
    );

    useEffect(() => {
      if (open && !hasFetched) {
        fetchSavedTranslations();
      }
    }, [open, hasFetched, fetchSavedTranslations]);

    const handleClearSaved = async () => {
      try {
        await fetch(`${API_BASE_URL}/saved`, {
          method: "DELETE",
        });
        setSavedTranslations([]);
      } catch (err) {
        console.error("Error clearing saved translations:", err);
      }
    };

    const handleDeleteSavedItem = async (id: string) => {
      try {
        await fetch(`${API_BASE_URL}/saved/${id}`, {
          method: "DELETE",
        });
        setSavedTranslations(
          savedTranslations.filter((item) => item.id !== id)
        );
      } catch (err) {
        console.error("Error deleting saved translation:", err);
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
                <div className="flex h-10 w-10 items-center justify-center bg-amber-500/10">
                  <StarFilledIcon className="h-5 w-5 text-amber-500" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-zinc-900">
                    Saved Translations
                  </h2>
                  <p className="text-sm text-zinc-500">
                    {loading
                      ? "Loading..."
                      : `${savedTranslations.length} translation${
                          savedTranslations.length !== 1 ? "s" : ""
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

            {savedTranslations.length > 0 && (
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
                  <p className="font-medium">Loading saved translations...</p>
                </div>
              ) : savedTranslations.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center text-zinc-500">
                  <div className="bg-zinc-100 p-4 mb-4">
                    <StarFilledIcon className="h-8 w-8 opacity-50" />
                  </div>
                  <p className="font-medium">No saved translations yet</p>
                  <p className="text-sm mt-1">
                    Star a translation to save it here
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {savedTranslations.map((item) => (
                    <SavedTranslationItem
                      key={item.id}
                      item={item}
                      getLanguageName={getLanguageName}
                      onClick={() => {
                        onSavedItemClick(item);
                      }}
                      onDelete={() => handleDeleteSavedItem(item.id)}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <Alert
          open={showClearConfirm}
          onClose={() => setShowClearConfirm(false)}
        >
          <AlertTitle>Clear all saved translations?</AlertTitle>
          <AlertDescription>
            This will permanently delete all your saved translations. This
            action cannot be undone.
          </AlertDescription>
          <AlertActions>
            <Button plain onClick={() => setShowClearConfirm(false)}>
              Cancel
            </Button>
            <Button
              color="red"
              onClick={() => {
                handleClearSaved();
                setShowClearConfirm(false);
              }}
            >
              Clear All
            </Button>
          </AlertActions>
        </Alert>
      </>
    );
  }
);
