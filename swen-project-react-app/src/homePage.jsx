import { useNavigate } from "react-router-dom";
import { useState } from "react";
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'

function parseJwt(token) {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const jsonPayload = decodeURIComponent(
    window
      .atob(base64)
      .split("")
      .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
      .join(""),
  );
  return JSON.parse(jsonPayload);
}

const HomePage = () => {
    const [count, setCount] = useState(0)
    const navigate = useNavigate();
    const idToken = parseJwt(sessionStorage.idToken.toString());
    const accessToken = parseJwt(sessionStorage.accessToken.toString());
    console.log(
      `Amazon Cognito ID token encoded: ${sessionStorage.idToken.toString()}`,
    );
    console.log("Amazon Cognito ID token decoded: ");
    console.log(idToken);
    console.log(
      `Amazon Cognito access token encoded: ${sessionStorage.accessToken.toString()}`,
    );
    console.log("Amazon Cognito access token decoded: ");
    console.log(accessToken);
    console.log("Amazon Cognito refresh token: ");
    console.log(sessionStorage.refreshToken);
    console.log(
      "Amazon Cognito example application. Not for use in production applications.",
    );
    const handleLogout = () => {
      sessionStorage.clear();
      navigate("/login");
    };
  
    return (
      <div>
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
            <button className="button-3d" onClick={() => setCount((count) => count + 1)}>
            count is {count}
            </button>
            <button type="button" onClick={handleLogout}>
            Logout
            </button>
        </div>
      </div>
    );
  };
  
  export default HomePage;