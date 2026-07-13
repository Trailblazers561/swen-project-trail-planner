import { UserIcon } from "@/components/templates/usericon"
import logo from "@/assets/images/awa-logo.png"
import { Role, useAuth } from "@/AuthContext";
import { Link } from "react-router-dom";
import "./Navbar.css";
import { useMediaQuery } from "react-responsive";

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

function Navbar() {
    const { username, currentRole } = useAuth();
    return (
        <nav className="sticky top-0 w-full bg-white shadow-md z-50 mb-20px z-[1000]" id="navbar">
            <div className="top-0 left-0 h-24 lg:h-18 bg-navbar text-white flex items-center justify-between p-4">
                <Desktop>
                    <Link to="/home">
                        <img src={logo} alt="Logo" className="h-full max-h-16 object-contain" />
                    </Link>
                    <div className="flex items-center gap-15 ml-auto">  
                        <Link className="color-blue" to="/home">Home</Link>
                        <Link to="/dashboard">Dashboard</Link>
                        {(currentRole === Role.Manager || currentRole === Role.Admin || currentRole === Role.Root) && <Link to="/devices">Device Management</Link>}
                        {(currentRole === Role.Admin || currentRole === Role.Root) && <Link to="/privileges">Privileges</Link>}
                        <div className="profile-info text-right justify-end flex items-center gap-2">
                            {currentRole !== null ? (
                                <div className="grid grid-rows-2 grid-cols-1">
                                    <div>
                                        <span data-testid="username">{username}</span>
                                    </div>
                                    <div>
                                        <div data-testid="user-role">{Role[currentRole]}</div>
                                    </div>
                                </div>
                            ) : (
                                <div className="grid grid-rows-1">
                                    <div data-testid="user-role">Guest</div>
                                </div>
                            )}
                            <UserIcon />
                        </div>
                    </div>
                </Desktop>
                <Mobile>
                    <Link to="/home">
                        <img src={logo} alt="Logo" className="h-full max-h-16 object-contain" />
                    </Link>
                    <div className="profile-info text-right justify-end flex items-center gap-2">
                        {currentRole !== null ? (
                            <div className="grid grid-rows-2 grid-cols-1">
                                <div>
                                    <span data-testid="username">{username}</span>
                                </div>
                                <div>
                                    <div data-testid="user-role">{Role[currentRole]}</div>
                                </div>
                            </div>
                        ) : (
                            <div className="grid grid-rows-1">
                                <div data-testid="user-role">Guest</div>
                            </div>
                        )}
                        <UserIcon />
                    </div>
                </Mobile>
            </div>
        </nav>
    )
}

export default Navbar