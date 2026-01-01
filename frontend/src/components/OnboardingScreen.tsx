import { useState } from "react";
import { motion } from "motion/react";
import { Button } from "./ui/button";

const API_BASE_URL = "http://localhost:8000";

interface OnboardingScreenProps {
  onComplete: () => void;
}

const LanguagesIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="m5 8 6 6" />
    <path d="m4 14 6-6 2-3" />
    <path d="M2 5h12" />
    <path d="M7 2h1" />
    <path d="m22 22-5-10-5 10" />
    <path d="M14 18h6" />
  </svg>
);

const DownloadIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);

const SpinnerIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none">
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    />
  </svg>
);

type DownloadState = "idle" | "downloading" | "error";

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
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center">
      <div className="absolute inset-0  from-teal-950 via-slate-900 to-indigo-950">
        <motion.div
          className="absolute w-[600px] h-[600px] bg-teal-500/20 blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ top: "-20%", left: "-10%" }}
        />
        <motion.div
          className="absolute w-[500px] h-[500px] bg-indigo-500/20 blur-3xl"
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ bottom: "-15%", right: "-5%" }}
        />
        <motion.div
          className="absolute w-[300px] h-[300px] bg-cyan-400/10 blur-2xl"
          animate={{
            x: [0, 50, 0],
            y: [0, 80, 0],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{ top: "40%", right: "20%" }}
        />
      </div>

      <div className="relative z-10 max-w-lg mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="mb-8"
        >
          <div className="inline-flex items-center justify-center w-20 h-20 from-teal-400 to-cyan-500 shadow-lg shadow-teal-500/30 mb-6">
            <LanguagesIcon className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl font-bold text-white tracking-tight mb-3">
            Bab
          </h1>
          <p className="text-xl text-teal-200/80 font-light">
            Offline translation, powered by AI
          </p>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="text-slate-300/90 text-lg leading-relaxed mb-10"
        >
          Translate between 200+ languages directly on your device. No internet
          required after setup. Your data stays private.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          className="space-y-4"
        >
          {downloadState === "error" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-4 bg-red-500/20 border border-red-500/30 text-red-200 text-sm mb-4"
            >
              {errorMessage}
            </motion.div>
          )}

          <Button
            color="cyan"
            onClick={handleDownload}
            disabled={downloadState === "downloading"}
          >
            {downloadState === "downloading" ? (
              <>
                <SpinnerIcon className="w-5 h-5 animate-spin mr-2" />
                Downloading model...
              </>
            ) : downloadState === "error" ? (
              <>
                <DownloadIcon className="w-5 h-5 mr-2" />
                Retry download
              </>
            ) : (
              <>
                <DownloadIcon className="w-5 h-5 mr-2" />
                Download translation model
              </>
            )}
          </Button>

          <p className="text-slate-400/70 text-sm">
            ~1 GB download • One-time setup
          </p>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-16 text-slate-500 text-xs"
        >
          Powered by Meta's NLLB-200 model
        </motion.p>
      </div>
    </div>
  );
}
