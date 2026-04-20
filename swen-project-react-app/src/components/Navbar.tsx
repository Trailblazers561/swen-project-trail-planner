import { UserIcon } from "@/components/ui/usericon"
import logo from "@/assets/images/awa-logo.png"
import { Role, useAuth } from "@/Context";
import { Link } from "react-router-dom";

function Navbar() {
    const { email, currentRole } = useAuth();
    return (
        <nav className="sticky top-0 w-full bg-white shadow-md z-50 mb-20px z-[1000]" id="navbar">
            <div className="top-0 left-0 w-lvw h-18 bg-[var(--color-navbar)] text-white flex items-center justify-between p-4">
                <Link to="/home">
                    <img src={logo} alt="Logo" className="h-full max-h-16 object-contain" />
                </Link>
                <div className="profile-info text-right justify-end flex items-center gap-2">
                    {currentRole !== null ? (
                        <div className="grid grid-rows-2 grid-cols-1">
                            <div>
                                <span>{email}</span>
                            </div>
                            <div>
                                <div>{Role[currentRole]}</div>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-rows-1">
                            <div>Guest</div>
                        </div>
                    )}
                    <UserIcon />
                </div>
            </div>
        </nav>
    )
}

export default Navbar