import { useState, useEffect } from "react";
import { OnboardingScreen } from "./components/OnboardingScreen";
import { LoadingScreen } from "./components/LoadingScreen";
import { API_BASE_URL } from "./utils/constants";
import { TranslatorApp } from "./TranslateApp";

type AppState = "checking" | "onboarding" | "ready";

function App() {
  const [appState, setAppState] = useState<AppState>("checking");

  useEffect(() => {
    const checkModelStatus = async () => {
      try {
        const [gemmaResponse, nllbResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/model/status?model_id=translategemma`),
          fetch(`${API_BASE_URL}/model/status?model_id=nllb`),
        ]);

        const gemmaData = gemmaResponse.ok ? await gemmaResponse.json() : null;
        const nllbData = nllbResponse.ok ? await nllbResponse.json() : null;

        if (gemmaData?.is_downloaded || nllbData?.is_downloaded) {
          setAppState("ready");
        } else {
          setAppState("onboarding");
        }
      } catch {
        setAppState("onboarding");
      }
    };

    checkModelStatus();
  }, []);

  const handleOnboardingComplete = () => {
    setAppState("ready");
  };

  if (appState === "checking") {
    return <LoadingScreen />;
  }

  if (appState === "onboarding") {
    return <OnboardingScreen onComplete={handleOnboardingComplete} />;
  }

  return <TranslatorApp onChangeModel={() => setAppState("onboarding")} />;
}

export default App;
