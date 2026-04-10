import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, GeoJSON, ZoomControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import Navbar from "./components/Navbar";

const LandingPage = () => {
  const navigate = useNavigate();

  return (

        <div className="h-screen w-screen relative">

             <Navbar/>

                <div className="absolute top-5 right-52 z-[1000]">
                    
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
                    zoomControl={false}
                    scrollWheelZoom={true}
                    className="h-full w-full"
                    >
                        <TileLayer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            attribution="&copy; OpenStreetMap contributors"
                        />
                        <ZoomControl position="bottomright" />
                </MapContainer>
                
        </div>
  );
};

export default LandingPage;