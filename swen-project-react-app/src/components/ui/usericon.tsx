import { Button } from "@/components/ui/button"
import { User, LogOut, LogIn } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuGroup, DropdownMenuItem, DropdownMenuSeparator } from "./dropdown-menu"
import { useNavigate } from "react-router-dom";
import { Role, useAuth } from "@/Context";

export function UserIcon() {
    const { currentRole, clearAuth } = useAuth();
    const navigate = useNavigate();
    const handleLogout = () => {
        clearAuth();
        navigate("/login");
    };
    const handleManageUsers = () => {
        navigate("/privileges");
    };

    return (
        <div className="z-3000">
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button className="bg-(--color-navbar)" size="icon" id="user-icon-button">
                        <User />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="z-1000">
                    <DropdownMenuGroup id="user-icon-group">
                        {(currentRole === Role.Admin || currentRole === Role.Root) && (
                            <DropdownMenuItem data-testid="manage-users" onClick={handleManageUsers} >
                                Manage Users
                            </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={handleLogout} data-testid="login-logout">
                            {(currentRole === null) ? (
                                <div className="font-bold rounded-md px-2 py-1 flex items-center gap-2">
                                    Login/Register
                                    <LogIn />
                                </div>
                            ) : (
                                <div className="text-(--color-logout) font-bold rounded-md px-2 py-1 flex items-center gap-2">
                                    Logout
                                    <LogOut />
                                </div>
                            )}
                        </DropdownMenuItem>
                    </DropdownMenuGroup>
                </DropdownMenuContent>
            </DropdownMenu>
        </div>
    )
}
