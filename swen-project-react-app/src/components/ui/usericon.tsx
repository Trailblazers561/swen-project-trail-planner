import { Button } from "@/components/ui/button"
import { User, LogOut } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuGroup, DropdownMenuItem, DropdownMenuSeparator } from "./dropdown-menu"
import { useNavigate } from "react-router-dom";



export function UserIcon() {

  const navigate = useNavigate();
  const handleLogout = () => {
        sessionStorage.clear();
        navigate("/login");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
          <Button className="bg-[var(--color-navbar)]" size="icon">
            <User />
          </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
          <DropdownMenuGroup>
          <DropdownMenuItem>Manage Users</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout}>
            <div className={"hover:bg-[var(--color-logout)] hover:text-white rounded-md px-2 py-1 flex items-center gap-2"}>
              Logout
              <LogOut />
            </div>
          </DropdownMenuItem>
          </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
