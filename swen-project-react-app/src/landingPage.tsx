import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Navbar from "./components/Navbar";
import { useState, useEffect } from "react";
import { TrailData } from "./api";

const LandingPage = () => {

    const createTrailIcon = (color: string) =>
    L.divIcon({
        className: "",
        html: `
        <svg width="30" height="42" viewBox="0 0 24 24">
            <path fill="${color}" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
            <circle cx="12" cy="9" r="2.5" fill="white"/>
        </svg>
        `,
        iconSize: [30, 42],
        iconAnchor: [15, 42],
        popupAnchor: [1, -36],
    });

    const parkBounds: L.LatLngBoundsExpression = [
        [42.2, -76.8], 
        [45.6, -72.0], 
    ];

    const navigate = useNavigate();

    const { getTrailMetadata } = TrailData();

    const [trails, setTrails] = useState<any[]>([]);

    const parsedTrails = trails.map(trail => ({
        ...trail,
        id: Number(trail.id),
        latitude: Number(trail.latitude),
        longitude: Number(trail.longitude),
    }))
        .filter(trail =>
        Number.isFinite(trail.latitude) &&
        Number.isFinite(trail.longitude)
    );

    useEffect(() => {
    async function fetchTrails() {
        try {
            const res = await getTrailMetadata();

            if (res.success) {
                setTrails(res.json);
                console.log("trail metadata:", res);
            } else {
                console.warn("Trail metadata not available");
                setTrails([]);
            }
        } catch (err) {
            console.error("Failed to load trails:", err);
            setTrails([]);
        }
    }

    fetchTrails();
    }, []);
    
  return (

        <div className="h-screen w-screen relative overflow-hidden">
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
                    minZoom={8}
                    maxZoom={15}
                    zoomControl={false}
                    scrollWheelZoom={true}
                    className="h-full w-full"
                    maxBounds={parkBounds}
                    maxBoundsViscosity={0.9}
                    >
                        <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png"
                        />
                        <ZoomControl position="topleft" />

                    {parsedTrails.map((trail) => (
                    <Marker key={trail.id} position={[trail.latitude, trail.longitude]} icon = {createTrailIcon("red")}>
                        <Popup>
                            <div onClick={(e) => e.stopPropagation()} className="space-y-2">
                                <div>
                                <strong>{trail.name}</strong>
                                <br />
                                {trail.notes}
                                </div>

                                <Button
                                    variant="primary"
                                    size="sm"
                                    onClick={() => navigate(`/dashboard?trailId=${trail.id}`)}
                                >
                                See Trail Data
                                </Button>
                            </div>
                        </Popup>
                    </Marker>
                    ))}
                </MapContainer>
                
        </div>
  );
};

export default LandingPage;