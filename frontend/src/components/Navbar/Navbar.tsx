import React, { useEffect, useRef, useState } from "react";
import "./Navbar.css";

interface NavbarProps {
  username: string;
  toggleHistory: () => void;
  historyVisible: boolean;
  handleLogout: () => void;
}

const Navbar = ({
  username,
  toggleHistory,
  historyVisible,
  handleLogout,
}: NavbarProps) => {
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownVisible(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="navbar">
      <div
        className={`nav-toggle ${historyVisible ? "rotate" : ""}`}
        onClick={toggleHistory}
        title="Toggle Side Panel"
      >
        ☰
      </div>
      <div className="user-menu" ref={dropdownRef}>
        <div
          className="user-icon"
          onClick={() => setDropdownVisible(!dropdownVisible)}
        >
          {username.slice(0, 2).toUpperCase()}
        </div>
        {dropdownVisible && (
          <div className="dropdown">
            <div className="dropdown-item">
              Logged in as: <strong>{username}</strong>
            </div>
            <div className="dropdown-item logout" onClick={handleLogout}>
              Logout
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Navbar;
