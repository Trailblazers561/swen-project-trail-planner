import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Navbar from "./components/Navbar";
import { useState, useEffect, useMemo } from "react";
import { TrailData } from "./api";
import { Granularity } from "./lib/apiTypes";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

const LandingPage = () => {

    const navigate = useNavigate();

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

    const { getTrailMetadata, getTrailLogs } = TrailData();

    const [trails, setTrails] = useState<any[]>([]);
    const [trailUsage, setTrailUsage] = useState<Record<number, number>>({}); 
    const [loadingUsage, setLoadingUsage] = useState(false);

    const parkBounds: L.LatLngBoundsExpression = [
        [42.2, -75.8], 
        [45.6, -71.0], 
    ];

    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [selectedPreset, setSelectedPreset] = useState("all");

    const applyPreset = (preset: string) => {
    const end = new Date();
    const start = new Date();
    
    switch (preset) {
        case "today":
            start.setHours(0, 0, 0, 0);
            break;

        case "2weeks":
            start.setDate(end.getDate() - 14);
            break;

        case "month":
            start.setMonth(end.getMonth() - 1);
            break;

        case "all":
            start.setFullYear(2000);
            break;
    }

    setSelectedPreset(preset);
    setStartDate(start);
    setEndDate(end);
    };

    useEffect(() => {
        async function fetchTrails() {
            try {
                const res = await getTrailMetadata();
                if (res.success) {
                    const trailData = await res.json;
                    setTrails(trailData);

                    const dates = trailData
                        .map((t: any) => Number(t.date_activated))
                        .filter(Boolean);

                    if (dates.length > 0) {
                        const earliest = new Date(Math.min(...dates) * 1000);

                    setStartDate(earliest);
                    setEndDate(new Date());
                }

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

    const parsedTrails = useMemo(
        () =>
        trails
            .map(trail => ({
                ...trail,
                id: Number(trail.id),
                latitude: Number(trail.latitude),
                longitude: Number(trail.longitude),
            }))
            .filter(
                trail =>
                    Number.isFinite(trail.latitude) &&
                    Number.isFinite(trail.longitude)
            ),
        [trails]
        );

    useEffect(() => { 
    async function fetchTrailUsage() {
        try {
            setLoadingUsage(true);

            if (!startDate || !endDate) return;

            const trailIds = parsedTrails.map(t => t.id);

            if (trailIds.length === 0) return;

            const response = await getTrailLogs(
                trailIds,
                startDate,
                endDate,
                Granularity.Day
            );

            if (!response.success) return;

            const logs = await response.json;

            const usageMap: Record<number, number> = {};

            logs.forEach((log: any) => {
                if (!usageMap[log.trail_id]) {
                    usageMap[log.trail_id] = 0;
                }

                usageMap[log.trail_id] += log.count;
            });

            setTrailUsage(usageMap);

        } catch (err) {
            console.error("Failed to fetch trail usage:", err);
        } finally {
            setLoadingUsage(false);
        }
    }

    if (parsedTrails.length > 0) {
        fetchTrailUsage();
    }
    }, [parsedTrails, startDate, endDate]);


    const getTrailColor = (trailId: number, days: number) => {

        if (loadingUsage) {
            const existingUsage = trailUsage[trailId];

            if (!existingUsage) {
                return "gray";
            }
        }

        const usage = trailUsage[trailId];

        if (usage === undefined || days <= 0) return "gray";

        const avg = usage / days;

        switch (true) {
            case avg < 20:
                return "#3b82f6";

            case avg < 35:
                return "#22c55e";

            case avg < 50:
                return "#eab308";

            case avg < 75:
                return "#f97316";

            default:
                return "#ef4444";
        }
    };

    //Calculates relative business. Will be changed in the future
    const days = useMemo(() => {
        if (!startDate || !endDate) {
            return 1;
        }
        
        return Math.max(
            1,
            (endDate.getTime() - startDate.getTime()) /
            (1000 * 60 * 60 * 24)
        );
    }, [startDate, endDate]);

  return (

        <div className="h-screen w-screen relative overflow-hidden">
             <Navbar/>

                <div className="absolute top-20 left-4 z-[9999] pointer-events-auto">
                    <div className="bg-white rounded-lg  shadow-lg p-4 border min-w-[420px]">

                        <div className="font-semibold mb-3 text-center">
                            Time Frame
                        </div>

                    <div className="flex justify-center">
                        <Select
                            value={selectedPreset}
                            onValueChange={(value) => applyPreset(value)}
                        >
                        <SelectContent className="z-[10000]" />
                        <SelectTrigger className="w-48 bg-white">
                            <SelectValue/>
                        </SelectTrigger>

                        <SelectContent className="z-[10000]">
                            <SelectItem value="today">Today</SelectItem>
                            <SelectItem value="2weeks">Last 2 Weeks</SelectItem>
                            <SelectItem value="month">Last Month</SelectItem>
                            <SelectItem value="all">All Time</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex justify-center gap-2 mt-2">
                    <input
                        type="date"
                        value={
                        startDate
                        ? startDate.toISOString().split("T")[0] : ""
                        }
                        onChange={(e) => {
                            setSelectedPreset("custom");
                            setStartDate(new Date(e.target.value));
                        }}
                        className="border rounded px-2 py-1 bg-white"
                    />

                    <input
                        type="date"
                        value={
                            endDate
                            ? endDate.toISOString().split("T")[0] : ""
                        } 
                        onChange={(e) => {
                            setSelectedPreset("custom");
                            setEndDate(new Date(e.target.value));
                        }}
                        className="border rounded px-2 py-1 bg-white"
                    />
                </div>

            </div>
            </div>
                
                <MapContainer
                    center={[44.02, -73.82]} 
                    zoom={8}
                    minZoom={8}
                    maxZoom={15}
                    zoomControl={false}
                    scrollWheelZoom={true}
                    className="h-full w-full"
                    maxBounds={parkBounds}
                    maxBoundsViscosity={0.8}
                    >
                        <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png"
                        />
                        <ZoomControl position="bottomright" />

                    {parsedTrails.map((trail) => (
                        <Marker
                            key={trail.id}
                            position={[trail.latitude, trail.longitude]}
                            icon={createTrailIcon(getTrailColor(trail.id, days))}
                        >
                            <Popup>
                                <div
                                    onClick={(e) => e.stopPropagation()}
                                    className="space-y-2"
                                >
                                    <div>
                                        <strong>{trail.name}</strong>
                                        <br />
                                        {trail.notes}
                                    </div>

                                    <Button
                                        variant="primary"
                                        size="sm"
                                        onClick={() =>
                                            navigate(`/dashboard?trailName=${trail.name}`)
                                        }
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