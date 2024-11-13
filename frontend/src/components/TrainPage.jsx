import { useEffect, useState } from "react";
import { trainModel, getNodes } from "../api";
import NodeSelector from "./NodeSelector";

export default function TrainPage() {
  const [form, setForm] = useState({
    node: "",
    modelName: "",
    modelType: "mobilenet",
    epochs: 1,
    batchSize: 32,
    learningRate: 0.001,
  });

  const [nodes, setNodes] = useState([]);
  const [trainingStatus, setTrainingStatus] = useState("");
  const [trainingResult, setTrainingResult] = useState(null);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const fetchNodes = async () => {
    try {
      const response = await getNodes();
      const data = response.data;
      if (data?.nodes?.length > 0) {
        const defaultNode = data.nodes[0].name;
        setNodes(data.nodes);
        setForm((prevForm) => ({ ...prevForm, node: defaultNode }));
        console.log("Default node set:", defaultNode);
      }
    } catch (error) {
      console.error("Error fetching nodes:", error);
    }
  };
  

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.node) {
      setTrainingStatus("Error: Node is not set.");
      return;
    }
    if (!form.modelName) {
      setTrainingStatus("Error: Model name is required.");
      return;
    }
    setTrainingStatus("Training started...");
    try {
      console.log("Form data:", form);
      const response = await trainModel(form);
      const { model_path, output_contents, output_file, report_path } = response;
      setTrainingResult({ model_path, output_contents, output_file, report_path });
      setTrainingStatus("Training successfully completed.");
    } catch (error) {
      setTrainingStatus(`Error: ${error.response?.data || error.message}`);
      setTrainingResult(null);
    }
  };

  const handleNodeChange = (value) => {
    setForm((prevForm) => ({ ...prevForm, node: value }));
  };

  useEffect(() => {
    fetchNodes();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Train Model</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Node</label>
          <NodeSelector value={form.node} onChange={handleNodeChange} nodes={nodes} />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">New Model Name</label>
          <input
            name="modelName"
            value={form.modelName}
            onChange={handleChange}
            placeholder="Enter a new model name"
            className="border p-2 mb-4 w-full"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Model Type</label>
          <select
            name="modelType"
            value={form.modelType}
            onChange={handleChange}
            className="border p-2 mb-4 w-full"
          >
            <option value="mobilenet">MobileNet</option>
            <option value="efficientnet">EfficientNet</option>
            <option value="resnet">ResNet</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Epochs</label>
          <input
            name="epochs"
            type="number"
            value={form.epochs}
            onChange={handleChange}
            placeholder="Epochs"
            className="border p-2 mb-4 w-full"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Batch Size</label>
          <input
            name="batchSize"
            type="number"
            value={form.batchSize}
            onChange={handleChange}
            placeholder="Batch Size"
            className="border p-2 mb-4 w-full"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Learning Rate</label>
          <input
            name="learningRate"
            type="number"
            step="0.001"
            value={form.learningRate}
            onChange={handleChange}
            placeholder="Learning Rate"
            className="border p-2 mb-4 w-full"
          />
        </div>

        <button type="submit" className="bg-blue-500 text-white p-2 rounded">Start Training</button>
      </form>

      {trainingStatus && (
        <div className="mt-6 p-4 border rounded bg-gray-100">
          <h3 className="text-lg font-bold">Training Status</h3>
          <p>{trainingStatus}</p>
        </div>
      )}

      {trainingResult && (
        <div className="mt-6 p-4 border rounded bg-gray-100">
          <h3 className="text-lg font-bold">Training Result</h3>
          <p><strong>Model Path:</strong> {trainingResult.model_path}</p>
          <p><strong>Output File:</strong> {trainingResult.output_file}</p>
          <p><strong>Report Path:</strong> {trainingResult.report_path}</p>
          <pre className="whitespace-pre-wrap">{trainingResult.output_contents}</pre>
        </div>
      )}
    </div>
  );
}
