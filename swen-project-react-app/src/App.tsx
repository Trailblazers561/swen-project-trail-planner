import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import DashBoard from "./dashboard";
import ConfirmUserPage from "./cognito/confirmUserPage";
import LandingPage from "./landingPage";
import React, { useState } from 'react';
import Test from './Test';
import AppContext from './AppContext';

function App() {
  const [role, setRole] = useState('user');

  const toggleRole = () => {
    true;
  }

  const isAuthenticated = () => {
    const accessToken = sessionStorage.getItem("accessToken");
    return !!accessToken;
  };

  return (
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
        </Routes>
      </BrowserRouter>
    );
}

export default App
