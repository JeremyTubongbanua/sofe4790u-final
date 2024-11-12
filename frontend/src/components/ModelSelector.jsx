export default function ModelSelector({ models = [], value, onChange }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className="border p-2 mb-4 w-full">
      {models.length > 0 ? (
        models.map((model) => <option key={model} value={model}>{model}</option>)
      ) : (
        <option value="">No models available</option>
      )}
    </select>
  );
}
