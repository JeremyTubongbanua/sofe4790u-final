import { useEffect, useState } from "react";
import { runInference } from "../api";
import NodeSelector from "./NodeSelector";
import ModelSelector from "./ModelSelector";
import ImageSelector from "./ImageSelector";

export default function InferencePage() {
  const [form, setForm] = useState({
    node: "",
    imagePath: "",
    modelName: "",
  });
  const [models, setModels] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [imagePreview, setImagePreview] = useState("");
  const [inferenceResult, setInferenceResult] = useState(null);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleImageChange = (value) => {
    setForm({ ...form, imagePath: value });
    setImagePreview(`http://192.168.8.125:8001/image?imagePath=${value}`);
  };

  const fetchNodes = async () => {
    try {
      const response = await fetch("http://192.168.8.125:8001/nodes");
      const data = await response.json();
      if (data.nodes.length > 0) {
        const defaultNode = data.nodes[0];
        const defaultModel = defaultNode.models[0] || "";
        setForm((prevForm) => ({
          ...prevForm,
          node: defaultNode.name,
          modelName: defaultModel,
        }));
        setNodes(data.nodes);
        const uniqueModels = Array.from(new Set(defaultNode.models || []));
        setModels(uniqueModels);

      }
    } catch (error) {
      console.error("Error fetching nodes:", error);
      setNodes([]);
      setModels([]);
    }
  };

  const handleNodeChange = (value) => {
    const selectedNode = nodes.find((n) => n.name === value);
    const defaultModel = selectedNode?.models[0] || "";
    setForm({ ...form, node: value, modelName: defaultModel });
    const uniqueModels = Array.from(new Set(selectedNode?.models || []));
    setModels(uniqueModels);

  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        node: form.node,
        imagePath: form.imagePath,
        modelName: form.modelName,
      };
      const response = await runInference(payload);
      setInferenceResult(response.data);
    } catch (error) {
      const errorMessage =
        typeof error.response?.data === "string"
          ? error.response.data
          : error.message || "Unknown error occurred";
      setInferenceResult({ error: errorMessage });
    }
  };

  useEffect(() => {
    fetchNodes();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Run Inference</h2>
      <NodeSelector value={form.node} onChange={handleNodeChange} nodes={nodes} setModels={setModels} />
      <ImageSelector value={form.imagePath} onChange={handleImageChange} />
      {imagePreview && (
        <div className="mt-4">
          <h3 className="text-lg font-bold">Selected Image Preview</h3>
          <img src={imagePreview} alt="Selected" className="w-64 h-64 object-contain mt-2 border rounded" />
        </div>
      )}
      <ModelSelector
        models={models}
        value={form.modelName}
        onChange={(value) => setForm({ ...form, modelName: value })}
      />

      <button onClick={handleSubmit} className="bg-blue-500 text-white p-2 rounded mt-4">Run Inference</button>

      {inferenceResult && (
        <div className="mt-6 p-4 border rounded">
          <h3 className="text-xl font-bold">Inference Result</h3>
          {inferenceResult.error ? (
            <p className="text-red-500">{JSON.stringify(inferenceResult.error)}</p>
          ) : (
            <div>
              <p><strong>Predicted Class:</strong> {inferenceResult.predicted_class}</p>
              <ul className="list-disc pl-5">
                {inferenceResult.output?.map(([label, confidence], index) => (
                  <li key={index}>{label}: {confidence.toFixed(2)}</li>
                ))}
              </ul>
              <p><strong>Timestamp:</strong> {inferenceResult.timestamp}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
