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
        const response = await fetch(`${API_BASE_URL}/model/status`);

        if (!response.ok) {
          setAppState("onboarding");
          return;
        }

        const data = await response.json();
        if (data.is_downloaded) {
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

  return <TranslatorApp />;
}

export default App;
