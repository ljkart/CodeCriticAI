import React from "react";
import "./FilePathInput.css";

interface FilePathInputProps {
  filePath: string;
  setFilePath: (path: string) => void;
}

export const FilePathInput = ({
  filePath,
  setFilePath,
}: FilePathInputProps) => {
  const handleBrowse = async () => {
    // This assumes you have a contextBridge-exposed method
    const selectedPath = await window.electronAPI?.selectPath(); // Custom preload API
    if (selectedPath) {
      setFilePath(selectedPath);
    }
  };

  return (
    <div className="file-path-input">
      <input
        type="text"
        value={filePath}
        onChange={(e) => setFilePath(e.target.value)}
        placeholder="/path/to/your/file"
      />
      <button type="button" onClick={handleBrowse}>
        Browse
      </button>
    </div>
  );
};
