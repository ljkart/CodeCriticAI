import React from "react";
import "./ReviewProgress.css";

/**
 * Overlay spinner shown while a code review is in progress.
 */
const ReviewProgress: React.FC = () => {
  return (
    <div className="progress-screen-overlay">
      <div className="progress-screen-container">
        <div className="spinner"></div>
        <p className="loading-text">Review In Progress...</p>
      </div>
    </div>
  );
};

export default ReviewProgress;
