import { useEffect, useState } from "react";
import { getImages } from "../api";

export default function ImageSelector({ value, onChange }) {
  const [images, setImages] = useState([]);

  useEffect(() => {
    getImages().then((res) => setImages(res.data.images));
  }, []);

  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className="border p-2 mb-4">
      {images.map((image, index) => (
        <option key={index} value={image}>{image}</option>
      ))}
    </select>
  );
}
