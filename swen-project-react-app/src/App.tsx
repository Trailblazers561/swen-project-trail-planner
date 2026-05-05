import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import DashBoard from "./dashboard";
import LandingPage from "./landingPage";
import Test from './Test';
import { AuthProvider } from './Context';
import Privileges from './userconfig';
import { Role, useAuth } from "@/Context";

function App() {
    const { currentRole } = useAuth();

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
                    <Route path="/dashboard" element={<DashBoard />} />
                    <Route path="/test" element={<Test />} />
                    <Route path="/privileges" 
                    element={(currentRole === Role.Admin || currentRole === Role.Root) ? <Privileges /> : <Navigate replace to="/login" />} 
                    />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App
