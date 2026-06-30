import './App.css'
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import LoginPage from "./cognito/loginPage";
import DashBoard from "./dashboard";
import LandingPage from "./landingPage";
import Test from './Test';
import DeviceManagementPage from './deviceManagementPage';
import Privileges from './userconfig';
import { Role, useAuth } from "@/Context";
import Navbar from './components/Navbar';
import Bottombar from './components/Bottombar';

function App() {
    const { currentRole } = useAuth();

    return (
        <BrowserRouter>
            <Routes>
                <Route element={<><Navbar/><Outlet/><Bottombar/></>}>
                    <Route
                        path="/"
                        element={<Navigate replace to="/home" />
                        }
                    />
                    <Route path="/home" element={<LandingPage />} />
                    <Route path="/dashboard" element={<DashBoard />} />
                    <Route path="/test" element={<Test />} />
                    <Route path="/devices" 
                        element={(currentRole && currentRole >= Role.Manager) ? <DeviceManagementPage /> : <Navigate replace to="/login" />} 
                    />
                    <Route path="/privileges" 
                        element={(currentRole && currentRole >= Role.Admin) ? <Privileges /> : <Navigate replace to="/login" />} 
                    />
                </Route>
                <Route path="/login" element={<LoginPage />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App
