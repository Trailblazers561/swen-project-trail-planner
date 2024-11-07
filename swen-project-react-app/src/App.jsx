import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import ConfirmUserPage from "./cognito/confirmUserPage";

function App() {
  const [count, setCount] = useState(0)

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
                <Navigate replace to="/login" />
              )
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/confirm" element={<ConfirmUserPage />} />
          <Route
            path="/home"
            element={
              <>
              <div>
                <a href="https://vite.dev" target="_blank">
                  <img src={viteLogo} className="logo" alt="Vite logo" />
                </a>
                <a href="https://react.dev" target="_blank">
                  <img src={reactLogo} className="logo react" alt="React logo" />
                </a>
              </div>
              <h1>Vite + React</h1>
              <div className="card">
                <button onClick={() => setCount((count) => count + 1)}>
                  count is {count}
                </button>
                <p>
                  Edit <code>src/App.jsx</code> and save to test HMR
                </p>
              </div>
              <p className="read-the-docs">
                Click on the Vite and React logos to learn more
              </p>
            </>
            }
          />
        </Routes>
      </BrowserRouter>
    );
}

export default App
