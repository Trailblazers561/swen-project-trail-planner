//https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javascriptv3/example_code/cognito-identity-provider/scenarios/cognito-developer-guide-react-example/frontend-client

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signIn, signUp } from "./authService";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const navigate = useNavigate();

  const handleSignIn = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    try {
      const session = await signIn(email, password);
      console.log("Sign in successful", session);
      if (session && typeof session.AccessToken !== "undefined") {
        sessionStorage.setItem("accessToken", session.AccessToken);
        if (sessionStorage.getItem("accessToken")) {
          //Refreshes session token (dont replace with navigate)
          window.location.href = "/home";
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

  const handleSignUp = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    try {
      await signUp(email, password);
      navigate("/confirm", { state: { email } });
    } catch (error) {
      alert(`Sign up failed: ${error}`);
    }
  };

  return (
    <div className="loginForm">
      <img className="logo" alt="Logo" src="AWA-logo.png" />
      <h4>
        {isSignUp ? "Sign up to create an account" : "Sign in to your account"}
      </h4>
      <form onSubmit={isSignUp ? handleSignUp : handleSignIn}>
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
        {isSignUp && (
          <div>
            <input
              className="inputText input-glass"
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm Password"
              required
            />
          </div>
        )}
        <button className="button-3d" type="submit">{isSignUp ? "Sign Up" : "Sign In"}</button>
      </form>
      <button className="button-3d" type="button" onClick={() => setIsSignUp(!isSignUp)}>
        {isSignUp
          ? "Already have an account? Sign In"
          : "Need an account? Sign Up"}
      </button>
    </div>
  );
};

export default LoginPage;