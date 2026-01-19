import { useState, useEffect } from "react";
import { Listbox, ListboxOption, ListboxLabel } from "./ui/listbox";
import { Button } from "./ui/button";
import { API_BASE_URL, LS_SELECTED_MODEL_KEY, DEFAULT_MODEL_ID } from "../utils/constants";
import { DownloadIcon, CheckIcon, LoaderIcon } from "./icons";

export interface ModelInfo {
  model_id: string;
  repo_id: string;
  display_name: string;
  description: string;
  model_type: string;
  size_estimate: string;
  requires_auth: boolean;
}

export interface ModelStatus {
  model_id: string;
  model_name: string;
  cache_dir: string;
  model_path: string;
  is_downloaded: boolean;
  is_loaded: boolean;
}

interface ModelSelectorProps {
  selectedModelId: string;
  onModelChange: (modelId: string) => void;
  onDownloadComplete?: () => void;
}

export function ModelSelector({
  selectedModelId,
  onModelChange,
  onDownloadComplete,
}: ModelSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [modelStatuses, setModelStatuses] = useState<Record<string, ModelStatus>>({});
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch available models
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/model/list`);
        if (!response.ok) throw new Error("Failed to fetch models");
        const data = await response.json();
        setModels(data.models);
      } catch (err) {
        console.error("Error fetching models:", err);
      }
    };

    fetchModels();
  }, []);

  // Fetch model statuses
  useEffect(() => {
    const fetchStatuses = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/model/list/status`);
        if (!response.ok) throw new Error("Failed to fetch model statuses");
        const data = await response.json();
        const statusMap: Record<string, ModelStatus> = {};
        for (const status of data.models) {
          statusMap[status.model_id] = status;
        }
        setModelStatuses(statusMap);
      } catch (err) {
        console.error("Error fetching model statuses:", err);
      }
    };

    fetchStatuses();
  }, [downloading]); // Refresh after download completes

  const handleModelSelect = (modelId: string) => {
    const status = modelStatuses[modelId];
    if (!status?.is_downloaded) {
      // Don't allow selecting a model that isn't downloaded
      return;
    }
    onModelChange(modelId);
    localStorage.setItem(LS_SELECTED_MODEL_KEY, modelId);
  };

  const handleDownload = async (modelId: string) => {
    setDownloading(modelId);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/model/download?model_id=${modelId}`,
        { method: "POST" }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Download failed");
      }

      // Refresh statuses after download
      const statusResponse = await fetch(`${API_BASE_URL}/model/list/status`);
      if (statusResponse.ok) {
        const data = await statusResponse.json();
        const statusMap: Record<string, ModelStatus> = {};
        for (const status of data.models) {
          statusMap[status.model_id] = status;
        }
        setModelStatuses(statusMap);
      }

      onDownloadComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    } finally {
      setDownloading(null);
    }
  };

  const selectedModel = models.find((m) => m.model_id === selectedModelId);
  const selectedStatus = modelStatuses[selectedModelId];

  if (models.length === 0) {
    return null; // Still loading
  }

  return (
    <div className="flex items-center gap-3">
      <Listbox
        value={selectedModel}
        onChange={(model) => model && handleModelSelect(model.model_id)}
        aria-label="Select translation model"
      >
        {models.map((model) => {
          const status = modelStatuses[model.model_id];
          const isDownloaded = status?.is_downloaded ?? false;
          const isDownloading = downloading === model.model_id;

          return (
            <ListboxOption
              key={model.model_id}
              value={model}
              disabled={!isDownloaded && !isDownloading}
            >
              <ListboxLabel>
                <span className="flex items-center gap-2">
                  {isDownloaded && (
                    <CheckIcon className="w-4 h-4 text-green-600" />
                  )}
                  {!isDownloaded && !isDownloading && (
                    <span className="w-4 h-4 rounded-full border border-zinc-300" />
                  )}
                  {isDownloading && (
                    <LoaderIcon className="w-4 h-4 text-sky-600 animate-spin" />
                  )}
                  <span>{model.display_name}</span>
                  <span className="text-xs text-zinc-500">
                    ({model.size_estimate})
                  </span>
                </span>
              </ListboxLabel>
            </ListboxOption>
          );
        })}
      </Listbox>

      {selectedModel && !selectedStatus?.is_downloaded && (
        <Button
          color="sky"
          onClick={() => handleDownload(selectedModelId)}
          disabled={downloading !== null}
        >
          {downloading === selectedModelId ? (
            <>
              <LoaderIcon className="w-4 h-4 animate-spin" />
              Downloading...
            </>
          ) : (
            <>
              <DownloadIcon className="w-4 h-4" />
              Download
            </>
          )}
        </Button>
      )}

      {error && (
        <span className="text-sm text-red-600">{error}</span>
      )}
    </div>
  );
}

// Helper to get saved model from localStorage
export function getSavedModelId(): string {
  try {
    const saved = localStorage.getItem(LS_SELECTED_MODEL_KEY);
    if (saved) return saved;
  } catch {}
  return DEFAULT_MODEL_ID;
}
