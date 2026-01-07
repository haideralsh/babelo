import { useState } from "react";
import { Button } from "./ui/button";
import { LanguagesIcon, DownloadIcon } from "./icons";

const API_BASE_URL = "http://localhost:8000";

interface OnboardingScreenProps {
  onComplete: () => void;
}

type DownloadState = "idle" | "downloading" | "complete" | "error";

export function OnboardingScreen({ onComplete }: OnboardingScreenProps) {
  const [downloadState, setDownloadState] = useState<DownloadState>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleDownload = async () => {
    setDownloadState("downloading");
    setErrorMessage("");

    try {
      const response = await fetch(`${API_BASE_URL}/model/download`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Download failed");
      }

      onComplete();
    } catch (err) {
      setDownloadState("error");
      setErrorMessage(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full text-center">
        {/* Logo and Title */}
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

        {/* Download Section */}
        <div className="bg-card border border-border rounded-xl p-6">
          {downloadState === "idle" && (
            <>
              <div className="flex items-center justify-center gap-2 text-muted-foreground mb-4">
                <DownloadIcon className="w-5 h-5" />
                <span className="text-sm font-medium">
                  Translation Model Required
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-6">
                Download the AI model (~1 GB) to enable offline translations.
              </p>
              <Button onClick={handleDownload} color="teal" className="w-full">
                <DownloadIcon className="w-5 h-5 mr-2" />
                Download Model
              </Button>
            </>
          )}

          {downloadState === "downloading" && (
            <>
              <div className="flex items-center justify-center gap-2 text-muted-foreground mb-4">
                <DownloadIcon className="w-5 h-5" />
                <span className="text-sm font-medium">
                  Translation Model Required
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-6">
                Download the AI model (~1 GB) to enable offline translations.
              </p>
              <Button disabled color="teal" className="w-full">
                <DownloadIcon className="w-5 h-5 mr-2 animate-pulse" />
                Downloading...
              </Button>
            </>
          )}

          {downloadState === "error" && (
            <>
              <div className="flex items-center justify-center gap-2 text-red-500 mb-4">
                <span className="text-sm font-medium">Download Failed</span>
              </div>
              <p className="text-sm text-muted-foreground mb-2">
                {errorMessage}
              </p>
              <p className="text-sm text-muted-foreground mb-6">
                Please check your connection and try again.
              </p>
              <Button onClick={handleDownload} color="teal" className="w-full">
                <DownloadIcon className="w-5 h-5 mr-2" />
                Retry Download
              </Button>
            </>
          )}
        </div>

        {/* Footer Note */}
        <p className="text-xs text-muted-foreground mt-6">
          The model is stored locally and only needs to be downloaded once.
        </p>
      </div>
    </div>
  );
}
