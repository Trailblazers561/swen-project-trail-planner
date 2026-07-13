import { Role, useAuth } from "@/AuthContext";
import { Link } from "react-router-dom";
import "./Bottombar.css";
import { useMediaQuery } from "react-responsive";
import home from "@/assets/images/home_icon.png";
import dashboard from "@/assets/images/dashboard_icon.png";
import device from "@/assets/images/device_icon.png";
import privileges from "@/assets/images/privileges_icon.png";

type DeviceType = {
children: React.ReactNode;
}

const Desktop = ({children}: DeviceType) => {
const isDesktop = useMediaQuery({ minWidth: 768 })
return isDesktop ? children : null
}
const Mobile = ({children}: DeviceType) => {
const isMobile = useMediaQuery({maxWidth: 768})
return isMobile ? children: null
}

function Bottombar() {
    const { username, currentRole } = useAuth();
    return (
        <Mobile>
            <nav className="fixed bottom-0 w-full bg-white shadow-md z-50 mb-20px z-[1000]" id="navbar">
                <div className="bottom-0 h-24 bg-navbar text-white flex items-center justify-between">
                    <div className="flex items-center justify-center gap-4 w-full">  
                        <Link className="color-blue max-w-3/16" to="/home">
                            <img src={home} alt="home"/>
                        </Link>
                        <Link className="max-w-3/16" to="/dashboard">
                            <img src={dashboard} alt="home"/>
                        </Link>
                        {(currentRole === Role.Manager || currentRole === Role.Admin || currentRole === Role.Root) && <Link className="max-w-3/16" to="/devices">
                            <img src={device} alt="home"/>
                        </Link>}
                        {(currentRole === Role.Admin || currentRole === Role.Root) && <Link className="max-w-3/16" to="/privileges">
                            <img src={privileges} alt="home"/>
                        </Link>}
                    </div>
                </div>
            </nav>
        </Mobile>
    )
}

export default Bottombar