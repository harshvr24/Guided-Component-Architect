import React, { useState } from "react";
import PreviewFrame from "./PreviewFrame";
import { generateComponent } from "./api";
import { ComponentOutput } from "./types";

function App() {
  const [prompt, setPrompt] = useState("");
  const [component, setComponent] = useState<ComponentOutput | null>(null);

  const handleGenerate = async () => {
    const result = await generateComponent(prompt);
    setComponent(result);
  };

  return (
    <div style={{ padding: "40px" }}>
      <h2>Guided Component Architect</h2>

      <input
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe component..."
        style={{ width: "400px", marginRight: "10px" }}
      />

      <button onClick={handleGenerate}>Generate</button>

      <PreviewFrame component={component} />
    </div>
  );
}

export default App;