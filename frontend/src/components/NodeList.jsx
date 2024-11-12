import { useEffect, useState } from "react";
import { getNodes } from "../api";

export default function NodeList() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    getNodes()
      .then((res) => {
        console.log(res.data); // { nodes: [{ name: "node0", models: ["test"] }] }
        setNodes(res.data.nodes);
      })
      .catch((error) => {
        console.error("API Error:", error);
        setNodes([]);
      });
  }, []);

  return (
    <div>
      <h2 className="text-lg font-bold">Nodes</h2>
      <ul>
        {nodes.map((node, index) => (
          <li key={index}>
            <strong>{node.name}</strong>: {node.models.join(", ")}
          </li>
        ))}
      </ul>
    </div>
  );
}
