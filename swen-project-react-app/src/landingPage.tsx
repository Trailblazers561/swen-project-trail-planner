import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import Navbar from "./components/Navbar";

const LandingPage = () => {
  const navigate = useNavigate();

  return (

        <div className="h-screen w-screen relative">

                <div className="absolute top-6 right-6 z-[1000]">
                    <Button
                        variant="primary"
                        onClick={() => navigate("/login")}
                        >
                        Login
                    </Button>
                </div>

                <MapContainer
                    center={[44.02, -73.82]} 
                    zoom={9}
                    scrollWheelZoom={true}
                    className="h-full w-full"
                    >
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution="&copy; OpenStreetMap contributors"
                        />
                </MapContainer>
                
        </div>
  );
};

export default LandingPage;