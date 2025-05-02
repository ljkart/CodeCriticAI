// components/Toast.tsx
import React, { useEffect } from "react";
import "./Toast.css";

interface ToastDataMessage {
  message: string;
  type: string;
}
interface ToastProps {
  toastData: ToastDataMessage;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ toastData, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000); // Hide after 3 seconds
    return () => clearTimeout(timer);
  }, [onClose]);

  useEffect(() => {
    console.log(toastData);
    const dd = document.getElementsByClassName("toast");
    console.log(dd);
  }, [toastData]);

  return <div className={`toast ${toastData.type} `}>{toastData.message}</div>;
};

export default Toast;
