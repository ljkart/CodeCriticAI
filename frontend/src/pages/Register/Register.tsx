import React, { useEffect, useState } from "react";
import "./Register.css";
import { registerUser } from "@/services/authService";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordMatch, setPasswordMatch] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [formTouched, setFormTouched] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");
    setFormTouched(false);

    if (!passwordMatch) {
      setErrorMessage("password do not match");
    }

    if (!username || !password || !confirmPassword) {
      setErrorMessage("Need to fill all details");
    }

    try {
      const result = await registerUser({ username, password });
      setSuccessMessage("Registeration Successful");
    } catch (error: unknown) {
      if (typeof error === 'object' && error && 'message' in error) {
        setErrorMessage((error as { message: string }).message);
      } else {
        setErrorMessage('Registration failed');
      }
    }
  };
  useEffect(() => {
    setPasswordMatch(password === confirmPassword ? true : false);
  }, [password, confirmPassword]);

  useEffect(() => {
    console.log(formTouched);
  }, [formTouched]);
  return (
    <div className="register-container">
      <h2>Register</h2>
      <div className="register-box">
        <form onSubmit={handleRegister}>
          <input
            type="text"
            placeholder="username"
            value={username}
            onChange={(e) => {
              setFormTouched(true);
              setUsername(e.target.value);
              setErrorMessage("");
              setSuccessMessage("");
            }}
            required
          />
          <input
            id="password"
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => {
              setFormTouched(true);
              setPassword(e.target.value);
              setErrorMessage("");
              setSuccessMessage("");
            }}
            required
          />
          <input
            id="confirmPassword"
            type="password"
            placeholder="confirm password"
            value={confirmPassword}
            onChange={(e) => {
              setFormTouched(true);
              setConfirmPassword(e.target.value);
              setErrorMessage("");
              setSuccessMessage("");
            }}
            required
          />
          {!passwordMatch && (
            <p className="error-msg">Password doesn't match</p>
          )}
          <button type="submit">Register</button>
        </form>
        {errorMessage && !formTouched ? (
          <p className="error-msg">{errorMessage}</p>
        ) : successMessage && !formTouched ? (
          <p className="success-msg">
            {successMessage}{" "}
            <a href="/login" className="login-link">
              Login
            </a>
          </p>
        ) : (
          <p>
            Already have an account?{" "}
            <a href="/login" className="login-link">
              Login
            </a>
          </p>
        )}
      </div>
    </div>
  );
};

export default Register;
