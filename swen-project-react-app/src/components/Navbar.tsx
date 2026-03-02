import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

function Navbar() {
  return (
    <div className="position-fixed top-0 left-0 w-full h-16 bg-gray-800 text-white flex items-center justify-between px-4">
        <Button>nav bar</Button>
    </div>
  )
}
 
export default Navbar