import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
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
                <Navigate replace to="/dashboard" />
              ) : (
                <Navigate replace to="/login" />
              )
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/confirm" element={<ConfirmUserPage />} />
          <Route path="/dashboard" 
            element={isAuthenticated() ? <DashBoard /> : <Navigate replace to="/" />}
          />
        </Routes>
      </BrowserRouter>
    );
}

export default App
