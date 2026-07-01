import { Role, useAuth } from "@/Context";
import { Link } from "react-router-dom";
import "./Bottombar.css";
import { useMediaQuery } from "react-responsive";

type DeviceType = {
children: React.ReactNode;
}

const Desktop = ({children}: DeviceType) => {
const isDesktop = useMediaQuery({ minWidth: 500 })
return isDesktop ? children : null
}
const Mobile = ({children}: DeviceType) => {
const isMobile = useMediaQuery({maxWidth: 499})
return isMobile ? children: null
}

function Bottombar() {
    const { username, currentRole } = useAuth();
    return (
        <Mobile>
            <nav className="fixed bottom-0 w-full bg-white shadow-md z-50 mb-20px z-[1000]" id="navbar">
                <div className="bottom-0 h-24 bg-navbar text-white flex items-center justify-between p-2">
                    <div className="flex items-center gap-2 w-full">  
                        <Link className="color-blue" to="/home">Home</Link>
                        <Link to="/dashboard">Dashboard</Link>
                        {(currentRole === Role.Manager || currentRole === Role.Admin || currentRole === Role.Root) && <Link to="/devices">Device Management</Link>}
                        {(currentRole === Role.Admin || currentRole === Role.Root) && <Link to="/privileges">Privileges</Link>}
                    </div>
                </div>
            </nav>
        </Mobile>
    )
}

export default Bottombar