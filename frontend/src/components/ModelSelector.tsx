import { LS_SELECTED_MODEL_KEY, DEFAULT_MODEL_ID } from "../utils/constants";

export interface ModelStatus {
  model_id: string;
  model_name: string;
  cache_dir: string;
  model_path: string;
  is_downloaded: boolean;
  is_loaded: boolean;
}

export function getSavedModelId(): string {
  try {
    const saved = localStorage.getItem(LS_SELECTED_MODEL_KEY);
    if (saved) return saved;
  } catch {}
  return DEFAULT_MODEL_ID;
}
