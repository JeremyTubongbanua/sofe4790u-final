import React from "react";
import TrainPage from "./components/TrainPage";
import InferencePage from "./components/InferencePage";

function App() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Model Dashboard</h1>
      <TrainPage />
      <InferencePage />
    </div>
  );
}

export default App;
