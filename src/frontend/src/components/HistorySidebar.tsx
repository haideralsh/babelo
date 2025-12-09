import * as Headless from "@headlessui/react";
import { ClockIcon, TrashIcon, XIcon } from "./icons";
import { HistoryItem, type HistoryItemData } from "./HistoryItem";

interface HistorySidebarProps {
  open: boolean;
  onClose: () => void;
  history: HistoryItemData[];
  onHistoryItemClick: (item: HistoryItemData) => void;
  onDeleteHistoryItem: (id: string) => void;
  onClearAll: () => void;
  getLanguageName: (code: string) => string;
}

export function HistorySidebar({
  open,
  onClose,
  history,
  onHistoryItemClick,
  onDeleteHistoryItem,
  onClearAll,
  getLanguageName,
}: HistorySidebarProps) {
  return (
    <Headless.Dialog open={open} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <Headless.DialogBackdrop
        transition
        className="fixed inset-0 bg-zinc-950/30 backdrop-blur-sm transition duration-300 ease-out data-closed:opacity-0 dark:bg-zinc-950/60"
      />

      {/* Sidebar Panel */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full">
            <Headless.DialogPanel
              transition
              className="pointer-events-auto w-screen max-w-md transform transition duration-300 ease-out data-closed:translate-x-full"
            >
              <div className="flex h-full flex-col bg-white shadow-2xl dark:bg-zinc-900">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 dark:bg-blue-500/20">
                      <ClockIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <Headless.DialogTitle className="text-lg font-semibold text-zinc-900 dark:text-white">
                        History
                      </Headless.DialogTitle>
                      <p className="text-sm text-zinc-500 dark:text-zinc-400">
                        {history.length} translation
                        {history.length !== 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={onClose}
                    className="rounded-lg p-2 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-900 transition-colors dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
                  >
                    <XIcon className="h-5 w-5" />
                  </button>
                </div>

                {/* Actions Bar */}
                {history.length > 0 && (
                  <div className="flex items-center justify-end border-b border-zinc-200 px-6 py-3 dark:border-zinc-800">
                    <button
                      type="button"
                      onClick={onClearAll}
                      className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors dark:text-red-400 dark:hover:bg-red-900/20"
                    >
                      <TrashIcon className="h-4 w-4" />
                      Clear all
                    </button>
                  </div>
                )}

                {/* Content */}
                <div className="flex-1 overflow-y-auto px-6 py-4">
                  {history.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-zinc-500 dark:text-zinc-400">
                      <div className="rounded-full bg-zinc-100 p-4 mb-4 dark:bg-zinc-800">
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
                            onClose();
                          }}
                          onDelete={() => onDeleteHistoryItem(item.id)}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </Headless.DialogPanel>
          </div>
        </div>
      </div>
    </Headless.Dialog>
  );
}
