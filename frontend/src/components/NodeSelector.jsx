import { useEffect, useState } from "react";
import { getNodes } from "../api";

export default function NodeSelector({ value, onChange, setModels }) {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    getNodes()
      .then((res) => {
        console.log("API Response for getNodes:", res.data);
        setNodes(res.data.nodes);
      })
      .catch((error) => {
        console.error("Error fetching nodes:", error);
      });
  }, []);

  const handleNodeChange = (nodeName) => {
    console.log("Selected Node:", nodeName);
    onChange(nodeName);
    const selectedNode = nodes.find((node) => node.name === nodeName);
    if (selectedNode) {
      // Use a deep copy of the models array to ensure React detects the change
      setModels([...new Set(selectedNode.models)]);
      console.log("Models for selected node (deep copy):", [...selectedNode.models]);
    } else {
      setModels([]);
      console.log("No models found for selected node.");
    }
  };

  return (
    <select value={value} onChange={(e) => handleNodeChange(e.target.value)} className="border p-2 mb-4 w-full">
      {nodes.map((node) => (
        <option key={node.name} value={node.name}>{node.name}</option>
      ))}
    </select>
  );
}
