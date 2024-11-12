import { useEffect, useState } from "react";
import { runInference } from "../api";
import NodeSelector from "./NodeSelector";
import ModelSelector from "./ModelSelector";
import ImageSelector from "./ImageSelector";

export default function InferencePage() {
  const [form, setForm] = useState({
    node: "node0",
    imagePath: "",
    modelPath: "",
    baseModel: "mobilenet",
    classNamesPath: "images/classes.txt",
    reportPath: "models/test/inference.json",
  });
  const [models, setModels] = useState([]);
  const [imagePreview, setImagePreview] = useState("");
  const [inferenceResult, setInferenceResult] = useState(null);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleImageChange = (value) => {
    setForm({ ...form, imagePath: value });
    setImagePreview(`http://192.168.8.125:8001/image?imagePath=${value}`);
  };

  useEffect(() => {
    console.log("Updated models state:", models);
  }, [models]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        node: form.node,
        imagePath: form.imagePath,
        modelPath: form.modelPath,
        baseModel: form.baseModel,
        classNamesPath: form.classNamesPath,
        reportPath: form.reportPath,
      };
      console.log("Payload for inference:", payload);
      const response = await runInference(payload);
      console.log("Inference Response:", response.data);
      setInferenceResult(response.data);
    } catch (error) {
      console.error("Error during inference:", error);
      setInferenceResult({ error: error.response?.data || error.message });
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Run Inference</h2>
      <NodeSelector value={form.node} onChange={(value) => setForm({ ...form, node: value })} setModels={setModels} />
      <ImageSelector value={form.imagePath} onChange={handleImageChange} />
      <ModelSelector models={models} value={form.modelPath} onChange={(value) => setForm({ ...form, modelPath: value })} />
      <button onClick={handleSubmit} className="bg-blue-500 text-white p-2 rounded">Run Inference</button>

      {inferenceResult && (
        <div className="mt-6 p-4 border rounded">
          <h3 className="text-xl font-bold">Inference Result</h3>
          {inferenceResult.error ? (
            <p className="text-red-500">{inferenceResult.error}</p>
          ) : (
            <div>
              <p><strong>Predicted Class:</strong> {inferenceResult.predicted_class}</p>
              <ul className="list-disc pl-5">
                {inferenceResult.output.map(([label, confidence], index) => (
                  <li key={index}>{label}: {confidence.toFixed(2)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
