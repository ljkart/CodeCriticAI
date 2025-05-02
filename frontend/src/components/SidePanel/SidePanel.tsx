import "./SidePanel.css";
import { FaChevronRight, FaChevronDown, FaFile, FaTrash } from "react-icons/fa";

interface Version {
  id: number;
  version: number;
  created_at: string;
}

interface ReviewFile {
  filename: string;
  versions: Version[];
}

interface SidePanelProps {
  onFileSelect: (filename: string, version: number) => void;
  isVisible: boolean;
  files: ReviewFile[];
  selectedFile: string | null;
  selectedVersion: number | null;
  handleVersionRemove: (filename: string, version: number) => void;
}

export const SidePanel = ({
  files,
  isVisible,
  selectedVersion,
  selectedFile,
  onFileSelect,
  handleVersionRemove,
}: SidePanelProps) => {
  return (
    <div className="file-history">
      <div className="file-list">
        {files.map((file) => (
          <div key={file.filename} className="file-item">
            <div
              className={`file-row ${
                selectedFile === file.filename ? "selected" : ""
              }`}
              onClick={() => {
                if (file.versions.length > 0) {
                  onFileSelect(file.filename, file.versions[0].version);
                }
              }}
            >
              {selectedFile === file.filename ? (
                <FaChevronDown className="file-icon" />
              ) : (
                <FaChevronRight className="file-icon" />
              )}
              <span className="file-name">{file.filename}</span>
            </div>

            {selectedFile === file.filename && (
              <div className="versions-list">
                {file.versions.map((version) => (
                  <div
                    key={version.id}
                    className={`version-item ${
                      selectedVersion === version.version ? "selected" : ""
                    }`}
                    onClick={() => onFileSelect(file.filename, version.version)}
                  >
                    <span className="version-number">
                      Version {version.version}
                    </span>
                    <span className="version-date">
                      {new Date(version.created_at).toLocaleDateString()}
                    </span>
                    <span
                      className="version-trash"
                      onClick={() =>
                        handleVersionRemove(file.filename, version.version)
                      }
                    >
                      <FaTrash className="file-icon" />
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SidePanel;
