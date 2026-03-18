import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signIn } from "./authService";
import React from "react";
import {Button} from "@/components/ui/button";
import { useAuth } from "../AuthContext";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { setUser } = useAuth();

  const handleSignIn = async (e) => {
    e.preventDefault();
    try {
      const session = await signIn(email, password);
      console.log("Sign in successful", session);
      setUser({ username: email }); // Update user context with username, email as placeholder
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
      <img className="logo" alt="Logo" src="AWA-logo.png" />
      <h4>Sign in to your account</h4>
      <form onSubmit={handleSignIn}>
        <div>
          <input
            className="inputText"
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
            className="inputText"
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
        </div>
        <Button variant="primary" type="submit" id="signInButton">Sign In</Button>
      </form>
    </div>
  );
};

export default LoginPage;