import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { signIn } from "./authService";
import React from "react";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionExpired = searchParams.get("reason") === "session_expired";

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      const session = await signIn(email, password);
      console.log("Sign in successful", session);
      if (session && typeof session.AccessToken !== "undefined") {
        sessionStorage.setItem("accessToken", session.AccessToken);
        if (sessionStorage.getItem("accessToken")) {
          window.location.href = "/dashboard";
        } else {
          console.error("Session token was not set properly.");
        }
      } else {
        console.error("SignIn session or AccessToken is undefined.");
      }
    } catch (error) {
      alert(`Sign in failed: ${error}`);
    }
  };

  return (
    <div className="loginForm">
      <img className="logo" alt="TrailCount" src="trailcount-logo-primary.svg" />
      <p className="sponsor-line">Sponsored by: Adirondack Wilderness Advocates</p>
      {sessionExpired && (
        <div className="session-expired-banner">
          Your session has expired. Please sign in again.
        </div>
      )}
      <h4>Sign in to your account</h4>
      <form onSubmit={handleSignIn}>
        <div>
          <input
            className="inputText input-glass"
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
        </div>
        <div>
          <input
            className="inputText input-glass"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
        </div>
        <button className="button-3d" type="submit">Sign In</button>
      </form>
    </div>
  );
};

export default LoginPage;