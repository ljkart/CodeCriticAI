import React, { useEffect, useState, DragEvent } from "react";
import { FilePathInput } from "../FilePathInput/FilePathInput";
import { doFileReview } from "@/services/reviewService";
import "./BottomPanel.css";

interface ToastDataMessage {
  message: string;
  type: string;
}

interface BottomPanelProps {
  filePath: string;
  setFilePath: (path: string) => void;
  onReviewFinished: (data: FileData) => void;
  setIsProcessingReview: (stat: boolean) => void;
  isProcessingReview: boolean;
  setToastData: (data: ToastDataMessage) => void;
}

const BottomPanel = ({
  filePath,
  setFilePath,
  onReviewFinished,
  setIsProcessingReview,
  isProcessingReview,
  setToastData,
}: BottomPanelProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleReview = async () => {
    if (!filePath) {
      setToastData({ message: "No file found to review", type: "error" });
      return;
    }

    setIsProcessingReview(true);
    const data = await doFileReview(filePath);
    let toastMessage = `${filePath.replace(/^.*[\\/]/, "")} already reviewed!`;
    if (data.is_new_version) {
      onReviewFinished({
        filename: data?.filename,
        version: data?.result.version,
      });
      toastMessage = `${filePath.replace(
        /^.*[\\/]/,
        ""
      )} Successfully reviewed!`;
    }
    setIsProcessingReview(false);
    setToastData({ message: toastMessage, type: "success" });
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };
  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile: File = e.dataTransfer.files[0];
    // You can use droppedFile if needed
  };

  useEffect(() => {
  }, [filePath]);

  return (
    <div>
      <div
        className={`bottom-panel ${isDragging}? 'dragging' : '' ${
          filePath ? "has-file" : ""
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <FilePathInput filePath={filePath} setFilePath={setFilePath} />
        <button onClick={handleReview} disabled={isProcessingReview}>
          {isProcessingReview ? "Reviewing..." : "Review"}
        </button>
      </div>
    </div>
  );
};

export default BottomPanel;
