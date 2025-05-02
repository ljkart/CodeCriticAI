import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { loginUser, tryAutoLogin } from "../../services/authService";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [formTouched, setFormTouched] = useState(true);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setFormTouched(false);

    try {
      const result = await loginUser({ username, password });
      console.log("Login success : ", result);
      localStorage.setItem("user", JSON.stringify(result.user));
      // reroute to dashboard
      navigate("/dashboard");
    } catch (error: unknown) {
      if (typeof error === 'object' && error && 'message' in error) {
        setError((error as { message: string }).message);
      } else {
        setError('Login failed');
      }
    }
  };

  useEffect(() => {
    const autoLogin = async () => {
      const token = await tryAutoLogin();
      console.log("Attempting autologin");
      console.log(token);
      if (token) {
        navigate("/dashboard");
      }
    };
    autoLogin();
  }, [navigate]);

  return (
    <div className="login-container">
      <h2>Login</h2>
      <div className="login-box">
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="username"
            value={username}
            onChange={(e) => {
              setFormTouched(true);
              setUsername(e.target.value);
            }}
            required
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => {
              setFormTouched(true);
              setPassword(e.target.value);
            }}
            required
          />
          <button type="submit">Login</button>
        </form>
        {error && !formTouched ? (
          <p className="error-msg">{error}</p>
        ) : (
          formTouched && (
            <p>
              Not Registered yet? <a href="/register">Register</a>
            </p>
          )
        )}
      </div>
    </div>
  );
};

export default Login;
