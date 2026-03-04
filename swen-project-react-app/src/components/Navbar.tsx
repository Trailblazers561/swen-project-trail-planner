import { UserIcon } from "@/components/ui/usericon"
import logo from "@/assets/images/awa-logo.png"

//TODO: Update logo image to be an icon button as well, allowing it to be clicked to return to the home page.
// This will require adding a route for the home page and using the useNavigate hook from react-router-dom
// to navigate to the dashboard when the logo is clicked The homepage doesn't exist yet which is why it's not implemented.

function Navbar() {
  return (
    <nav className="sticky top-0 w-full bg-white shadow-md z-50 mb-20px">
     <div className="position-fixed top-0 left-0 w-lvw h-16 bg-[var(--color-navbar)] text-white flex items-center justify-between p-4">
         <img src={ logo } alt="Logo" className="h-10" />
         <UserIcon />
     </div>
    </nav>
  )
}
 
export default Navbar