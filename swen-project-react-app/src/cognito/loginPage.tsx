import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signIn, signUp } from "./authService";
import React from "react";
import {Button} from "@/components/ui/button";

const LoginPage = () => {
  const [signInEmail, setSignInEmail] = useState("");
  const [signInPassword, setSignInPassword] = useState("");
  const [signUpDisplayName, setSignUpDisplayName] = useState("");
  const [signUpEmail, setSignUpEmail] = useState("");
  const [signUpPassword, setSignUpPassword] = useState("");
  const [signUpConfirmPassword, setSignUpConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const session = await signIn(signInEmail, signInPassword);
      console.log("Sign in successful", session);

      if (session && typeof session.AccessToken !== "undefined") {
        sessionStorage.setItem("accessToken", session.AccessToken);
        navigate("/dashboard");
      } else {
        console.error("SignIn session or AccessToken is undefined.");
      }
    } catch (error) {
      alert(`Sign in failed: ${error}`);
    }
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (signUpPassword !== signUpConfirmPassword)
        throw new Error("Entered Passwords Do Not Match");
      if (signUpPassword.length < 6)
        throw new Error("Password must be a minimum of 6 characters");
      const session = await signUp(signUpEmail, signUpPassword, signUpDisplayName);
      console.log("Sign in successful", session);
      setSignUpDisplayName("");
      setSignUpEmail("");
      setSignUpPassword("");
      setSignUpConfirmPassword("");
      alert("Sign Up Successful!!! Please verify your email then sign in. (This will be replaced later with better UI)");
    } catch (error) {
      alert(`Sign in failed: ${error}`);
    }
  };

  return (
    <div className="flex h-screen">

      <div 
        className="fixed left-0 top-0 h-screen w-1/2 bg-cover bg-center"
        style={{ backgroundImage: "url('/News-OswegatchieRiver-BearPond.jpg')" }}
      >
      <div className="absolute inset-0 bg-black/20" />
        <img
          src="/AWA-logo.png"
          alt="Logo"
          className="absolute top-8 left-1/2 w-56 md:w-64 -translate-x-1/2"
        />
      </div>

      <div className="fixed right-0 top-0 h-screen w-1/2 flex items-center justify-center">
        <div className="flex w-full max-w-4xl items-start" id="loginForm">

          <div className="flex-1 px-10 pt-6">
            <h2 className="text-2xl font-semibold mb-2">Welcome Back</h2>
            <p className="text-gray-500 mb-6">Sign in to your account</p>

            <form onSubmit={handleSignIn} className="space-y-4">
              <input
                type="email"
                placeholder="Email"
                value={signInEmail}
                onChange={(e) => setSignInEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={signInPassword}
                onChange={(e) => setSignInPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />

              <Button type="submit" variant="primary" className="w-full">
                Login
              </Button>
            </form>
          </div>

          <div className="w-px bg-gray-300 mx-4 h-124" />

          <div className="flex-1 px-10 pt-6">
            <h2 className="text-2xl font-semibold mb-2">Get Started</h2>
            <p className="text-gray-500 mb-6">Register an account</p>

            <form onSubmit={handleSignUp} className="space-y-4">
              <input
                type="text"
                placeholder="Display Name"
                value={signUpDisplayName}
                onChange={(e) => setSignUpDisplayName(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={signUpEmail}
                onChange={(e) => setSignUpEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={signUpPassword}
                onChange={(e) => setSignUpPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />
              <input
                type="password"
                placeholder="Confirm Password"
                value={signUpConfirmPassword}
                onChange={(e) => setSignUpConfirmPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />

              <Button className="w-full" variant="primary">
                Sign Up
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;