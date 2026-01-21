import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { LanguagesIcon, DownloadIcon, CheckIcon } from "./icons";
import { API_BASE_URL, DEFAULT_MODEL_ID, LS_SELECTED_MODEL_KEY } from "../utils/constants";

interface ModelInfo {
  model_id: string;
  repo_id: string;
  display_name: string;
  description: string;
  model_type: string;
  size_estimate: string;
  requires_auth: boolean;
}

interface ModelStatus {
  model_id: string;
  is_downloaded: boolean;
  is_loaded: boolean;
}

interface OnboardingScreenProps {
  onComplete: () => void;
}

type DownloadState = "idle" | "downloading" | "complete" | "error";

export function OnboardingScreen({ onComplete }: OnboardingScreenProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [modelStatuses, setModelStatuses] = useState<Record<string, ModelStatus>>({});
  const [selectedModelId, setSelectedModelId] = useState<string>(DEFAULT_MODEL_ID);
  const [downloadState, setDownloadState] = useState<DownloadState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/model/list`);
        if (!response.ok) throw new Error("Failed to fetch models");
        const data = await response.json();
        setModels(data.models);
        if (data.default_model_id) {
          setSelectedModelId(data.default_model_id);
        }
      } catch (err) {
        console.error("Error fetching models:", err);
      }
    };

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

    fetchModels();
    fetchStatuses();
  }, []);

  const handleDownload = async () => {
    setDownloadState("downloading");
    setErrorMessage("");

    try {
      const response = await fetch(`${API_BASE_URL}/model/download?model_id=${selectedModelId}`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Download failed");
      }

      localStorage.setItem(LS_SELECTED_MODEL_KEY, selectedModelId);
      onComplete();
    } catch (err) {
      setDownloadState("error");
      setErrorMessage(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    }
  };

  const selectedModel = models.find((m) => m.model_id === selectedModelId);
  const selectedModelStatus = modelStatuses[selectedModelId];
  const isSelectedModelDownloaded = selectedModelStatus?.is_downloaded ?? false;

  const handleContinue = () => {
    localStorage.setItem(LS_SELECTED_MODEL_KEY, selectedModelId);
    onComplete();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full text-center">
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="p-3 bg-primary/10 rounded-2xl">
            <LanguagesIcon className="w-8 h-8 text-primary" />
          </div>
        </div>

        <h1 className="text-3xl font-semibold text-foreground mb-3 text-balance">
          Local Translator
        </h1>

        <p className="text-muted-foreground text-lg mb-10 text-balance">
          Translate text privately using AI that runs entirely on your device.
          No internet required.
        </p>

        <div className="bg-card border border-border rounded-xl p-6">
          <div className="flex items-center justify-center gap-2 text-muted-foreground mb-4">
            <DownloadIcon className="w-5 h-5" />
            <span className="text-sm font-medium">
              Choose a Translation Model
            </span>
          </div>

          {models.length > 0 && downloadState !== "downloading" && (
            <div className="space-y-3 mb-6">
              {models.map((model) => {
                const status = modelStatuses[model.model_id];
                const isDownloaded = status?.is_downloaded ?? false;

                return (
                  <label
                    key={model.model_id}
                    className={`flex items-start gap-3 p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedModelId === model.model_id
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="model"
                      value={model.model_id}
                      checked={selectedModelId === model.model_id}
                      onChange={(e) => setSelectedModelId(e.target.value)}
                      className="mt-1 accent-primary"
                    />
                    <div className="flex-1 text-left">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-foreground">
                          {model.display_name}
                        </span>
                        <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                          {model.size_estimate}
                        </span>
                        {isDownloaded && (
                          <span className="text-xs text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400 px-2 py-0.5 rounded flex items-center gap-1">
                            <CheckIcon className="w-3 h-3" />
                            Downloaded
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {model.description}
                      </p>
                      {model.requires_auth && !isDownloaded && (
                        <p className="text-xs text-amber-600 dark:text-amber-500 mt-2 flex items-center gap-1">
                          <span className="inline-block w-1.5 h-1.5 rounded-full bg-amber-500" />
                          Requires HuggingFace token (HF_TOKEN)
                        </p>
                      )}
                    </div>
                    {selectedModelId === model.model_id && (
                      <CheckIcon className="w-5 h-5 text-primary mt-1" />
                    )}
                  </label>
                );
              })}
            </div>
          )}

          {models.length === 0 && downloadState !== "error" && (
            <div className="text-sm text-muted-foreground mb-6">
              Loading available models...
            </div>
          )}

          {downloadState === "idle" && isSelectedModelDownloaded && (
            <Button
              onClick={handleContinue}
              color="teal"
              className="w-full"
            >
              <CheckIcon className="w-5 h-5 mr-2" />
              Continue with {selectedModel?.display_name || "Model"}
            </Button>
          )}

          {downloadState === "idle" && !isSelectedModelDownloaded && (
            <Button
              onClick={handleDownload}
              color="teal"
              className="w-full"
              disabled={models.length === 0}
            >
              <DownloadIcon className="w-5 h-5 mr-2" />
              Download {selectedModel?.display_name || "Model"}
            </Button>
          )}

          {downloadState === "downloading" && (
            <>
              <p className="text-sm text-muted-foreground mb-4">
                Downloading {selectedModel?.display_name}...
              </p>
              <Button disabled color="teal" className="w-full">
                <DownloadIcon className="w-5 h-5 mr-2 animate-pulse" />
                Downloading...
              </Button>
            </>
          )}

          {downloadState === "error" && (
            <>
              <div className="flex items-center justify-center gap-2 text-red-500 mb-2">
                <span className="text-sm font-medium">Download Failed</span>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                {errorMessage}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Please check your connection and try again.
              </p>
              <Button onClick={handleDownload} color="teal" className="w-full">
                <DownloadIcon className="w-5 h-5 mr-2" />
                Retry Download
              </Button>
            </>
          )}
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          The model is stored locally and only needs to be downloaded once.
        </p>
      </div>
    </div>
  );
}
