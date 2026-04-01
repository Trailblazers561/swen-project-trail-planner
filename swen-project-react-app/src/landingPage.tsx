import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

//React leaflet for map?

const LandingPage = () => {
  const navigate = useNavigate();

  return (

        <div>

            <h1> Test Landing Page!!! </h1>

            <Button
                variant="primary"
                onClick={() => navigate("/login")}
                >
                Login
            </Button>

          </div>
  );
};

export default LandingPage;