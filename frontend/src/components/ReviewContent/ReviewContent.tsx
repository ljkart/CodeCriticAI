import React, { useEffect, useState } from "react";
import "./ReviewContent.css";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  vscDarkPlus,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import { getReviewByFilenameAndVersion } from "@/services/reviewService";

interface ReviewContentProps {
  selectedFile: string | null;
  selectedVersion: number | null;
}

interface Review {
  line_number: number;
  code: string;
  review: string;
}

interface ReviewData {
  language: string;
  original_code: string;
  refactored_code: string;
  reviews: Review[];
}

export const ReviewContent = ({
  selectedFile,
  selectedVersion,
}: ReviewContentProps) => {
  const [activeTab, setActiveTab] = useState<"review" | "refactored">("review");
  const [reviewData, setReviewData] = useState<ReviewData | null>(null);

  useEffect(() => {
    const fetchReview = async () => {
      if (!selectedFile || !selectedVersion) return;

      try {
        const response = await getReviewByFilenameAndVersion(
          selectedFile,
          Number(selectedVersion)
        );
        console.log(response);
        const data = await response;
        setReviewData(data);
      } catch (error) {
        console.error("Error fetching review:", error);
      }
    };

    fetchReview();
  }, [selectedFile, selectedVersion]);

  if (!selectedFile || !selectedVersion || !reviewData) {
    return <div className="review-panel">Select a file to view its review</div>;
  }

  return (
    <div className="review-panel">
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === "review" ? "active" : ""}`}
          onClick={() => setActiveTab("review")}
        >
          Reviews
        </button>
        <button
          className={`tab-button ${activeTab === "refactored" ? "active" : ""}`}
          onClick={() => setActiveTab("refactored")}
        >
          Refactored-Code
        </button>
      </div>

      <div className="tab-content">
        {activeTab === "review" ? (
          <div className="review-list">
            {reviewData.reviews.map((review, index) => (
              <div key={index} className="review-item">
                <div className="code-block">
                  {/* <div className="line-number">Line {review.line_number}</div> */}
                  <div className="code-content">
                    <SyntaxHighlighter
                      language={reviewData.language.toLowerCase()}
                      style={vscDarkPlus}
                    >
                      {review.code}
                    </SyntaxHighlighter>
                  </div>
                </div>
                <div className="review-comment">
                  <div className="review-text">{review.review}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="refactored-code">
            <div className="code-container">
              <SyntaxHighlighter
                language={reviewData.language.toLowerCase()}
                style={vscDarkPlus}
                showLineNumbers
              >
                {reviewData.refactored_code}
              </SyntaxHighlighter>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
export default ReviewContent;
