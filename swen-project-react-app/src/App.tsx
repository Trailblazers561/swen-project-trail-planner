import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import DashBoard from "./dashboard";
import ConfirmUserPage from "./cognito/confirmUserPage";
import LandingPage from "./landingPage";
import React, { useState } from 'react';
import Test from './Test';
import { AuthProvider } from './Context';
import Privileges from './userconfig';

function App() {

  const isAuthenticated = () => {
    const accessToken = sessionStorage.getItem("accessToken");
    return !!accessToken;
  };

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={<Navigate replace to="/home" />
            }
          />
          <Route path="/home" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/confirm" element={<ConfirmUserPage />} />
          <Route path="/dashboard" 
            element={isAuthenticated() ? <DashBoard /> : <Navigate replace to="/login" />}
          />
          <Route path="/test" element={<Test />} />
          <Route path="/privileges" element={<Privileges />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App
