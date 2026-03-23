import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signIn } from "./authService";
import React from "react";
import {Button} from "@/components/ui/button";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const session = await signIn(email, password);
      console.log("Sign in successful", session);

      if (session && typeof session.AccessToken !== "undefined") {
        sessionStorage.setItem("accessToken", session.AccessToken);
        window.location.href = "/dashboard";
      } else {
        console.error("SignIn session or AccessToken is undefined.");
      }
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
        <div className="flex w-full max-w-4xl items-start">

          <div className="flex-1 px-10 pt-6">
            <h2 className="text-2xl font-semibold mb-2">Welcome Back</h2>
            <p className="text-gray-500 mb-6">Sign in to your account</p>

            <form onSubmit={handleSignIn} className="space-y-4">
              <input
                type="email"
                placeholder="Username or Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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

            <form className="space-y-4">
              <input
                type="text"
                placeholder="Username"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              <input
                type="email"
                placeholder="Email"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              <input
                type="password"
                placeholder="Password"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              <input
                type="password"
                placeholder="Confirm Password"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
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