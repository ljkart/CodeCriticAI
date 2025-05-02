import { useEffect, useRef, useState, Suspense, lazy } from "react";
import Toast from "@/components/Toast/Toast";
import { logoutUser } from "@/services/authService";
import Navbar from "@/components/Navbar/Navbar";
import SidePanel from "@/components/SidePanel/SidePanel";
import ReviewProgress from "@/components/ReviewProgress/ReviewProgress";
import {
  getFileHistories,
  removeReviewByFilenameVersion,
} from "@/services/reviewService";
import "./Dashboard.css";
import ErrorBoundary from "@/components/ErrorBoundary/ErrorBoundary";

interface ReviewFile {
  filename: string;
  versions: {
    id: number;
    version: number;
    created_at: string;
  }[];
}
interface ReviewHistoryItem {
  id: number;
  filename: string;
  version: number;
  created_at: string;
}

// Lazy load large components
const ReviewContentLazy = lazy(() => import("@/components/ReviewContent/ReviewContent"));
const SidePanelLazy = lazy(() => import("@/components/SidePanel/SidePanel"));
const BottomPanelLazy = lazy(() => import("@/components/BottomPanel/BottomPanel"));

/**
 * Main dashboard page for managing and viewing code reviews.
 */
const Dashboard = () => {
  const [activeTab] = useState<"reviews" | "refactor">("reviews");
  const [historyVisible, setHistoryVisible] = useState(true);
  const [filePath, setFilePath] = useState("");
  const [files, setFiles] = useState<ReviewFile[]>([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [username, setUsername] = useState<string>("");
  const [isProcessingReview, setIsProcessingReview] = useState(false);
  const [toastData, setToastData] = useState<ToastDataMessage>();
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleVersionRemove = async (filename: string, version: number) => {
    try {
      const data = await removeReviewByFilenameVersion(filename, version);
      setToastData({
        message: `Review (${data.filename}-v${String(version).padStart(
          3,
          "0"
        )}) Sucessfully Removed\n`,
        type: "success",
      });
      fetchFiles();
    } catch (error: any) {
      const err = error.response?.data?.error || "Unknown error";
      setToastData({
        message: `Failed to remove review : ${err}`,
        type: "error",
      });
    }
  };
  const handleLogout = async () => {
    await logoutUser();
    window.location.href = "/login";
  };

  const toggleHistory = () => {
    setHistoryVisible(!historyVisible);
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUsername(parsedUser.name || "");
      } catch (error) {
        setUsername("");
      }
    }
  }, []);

  // Fetch initial data
  const fetchFiles = async (fileToBeSelectedData: FileData | null = null) => {
    try {
      const data: ReviewHistoryItem[] = await getFileHistories();
      // Group by filename
      const groupedFiles = data.reduce(
        (acc: { [key: string]: ReviewHistoryItem[] }, item) => {
          if (!acc[item.filename]) {
            acc[item.filename] = [];
          }
          acc[item.filename].push(item);
          return acc;
        },
        {}
      );

      // Convert to array and sort versions
      const filesArray = Object.entries(groupedFiles).map(
        ([filename, versions]) => ({
          filename,
          versions: versions.sort((a, b) => b.version - a.version), // Sort versions descending
        })
      );

      setFiles(filesArray);

      // Set initial selection (either from param or first file)
      if (filesArray.length > 0) {
        const firstFile = filesArray[0];
        if (fileToBeSelectedData) {
          setSelectedFile(fileToBeSelectedData.filename);
          setSelectedVersion(fileToBeSelectedData.version);
        } else {
          setSelectedFile(firstFile.filename);
          if (firstFile.versions.length > 0) {
            setSelectedVersion(firstFile.versions[0].version);
          }
        }
      } else {
        setSelectedFile("");
        setSelectedVersion(null);
      }
    } catch {
      // Error fetching files
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div>
      {isProcessingReview && <ReviewProgress />}
      {toastData?.message && (
        <Toast
          toastData={toastData}
          onClose={() => setToastData({ message: "", type: "" })}
        />
      )}
      <div className="dashboard">
        <Navbar
          username={username}
          toggleHistory={toggleHistory}
          historyVisible={historyVisible}
          handleLogout={handleLogout}
        />
        <ErrorBoundary>
          <div className="content">
            <div className={`side-panel ${historyVisible ? "" : "hidden"}`}>
              <Suspense fallback={<div>Loading...</div>}>
                <SidePanelLazy
                  isVisible={historyVisible}
                  files={files}
                  selectedFile={selectedFile}
                  selectedVersion={selectedVersion}
                  handleVersionRemove={handleVersionRemove}
                  onFileSelect={(file: string, version: number) => {
                    setSelectedFile(file);
                    setSelectedVersion(version);
                  }}
                />
              </Suspense>
            </div>
            <div className="main-panel">
              <div className="main-scroll">
                <div className="review-content">
                  {activeTab === "reviews" && (
                    <Suspense fallback={<div>Loading review...</div>}>
                      <ReviewContentLazy
                        selectedFile={selectedFile}
                        selectedVersion={selectedVersion}
                      />
                    </Suspense>
                  )}
                </div>
              </div>
              <Suspense fallback={<div>Loading bottom panel...</div>}>
                <BottomPanelLazy
                  filePath={filePath}
                  setFilePath={setFilePath}
                  onReviewFinished={(fileData: FileData) => fetchFiles(fileData)}
                  setIsProcessingReview={setIsProcessingReview}
                  isProcessingReview={isProcessingReview}
                  setToastData={setToastData}
                />
              </Suspense>
            </div>
          </div>
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default Dashboard;
