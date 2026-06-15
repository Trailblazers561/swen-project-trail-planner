import './App.css'
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import DashBoard from "./dashboard";
import LandingPage from "./landingPage";
import Test from './Test';
import Privileges from './userconfig';
import { Role, useAuth } from "@/Context";
import Navbar from './components/Navbar';

function App() {
    const { currentRole } = useAuth();

    return (
        <BrowserRouter>
            <Routes>
                <Route element={<><Navbar/><Outlet/></>}>
                    <Route
                        path="/"
                        element={<Navigate replace to="/home" />
                        }
                    />
                    <Route path="/home" element={<LandingPage />} />
                    <Route path="/dashboard" element={<DashBoard />} />
                    <Route path="/test" element={<Test />} />
                    <Route path="/privileges" 
                    element={(currentRole === Role.Admin || currentRole === Role.Root) ? <Privileges /> : <Navigate replace to="/login" />} 
                    />
                </Route>
                <Route path="/login" element={<LoginPage />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App
