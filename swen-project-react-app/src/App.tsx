import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import HomePage from "./homePage";
import DashBoard from "./dashboard";
import ConfirmUserPage from "./cognito/confirmUserPage";
import React from 'react';

function App() {
  const isAuthenticated = () => {
    const accessToken = sessionStorage.getItem("accessToken");
    return !!accessToken;
  };

  return (
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              isAuthenticated() ? (
                <Navigate replace to="/home" />
              ) : (
                <Navigate replace to="/dashboard" />
              )
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/confirm" element={<ConfirmUserPage />} />
          <Route path="/home" 
            element={isAuthenticated() ? <HomePage /> : <Navigate replace to="/" />}
          />
          <Route path="/dashboard" element={<DashBoard />} />
        </Routes>
      </BrowserRouter>
    );
}

export default App
