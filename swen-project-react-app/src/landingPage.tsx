import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Navbar from "./components/Navbar";
import { useState, useEffect, useMemo } from "react";
import { TrailData } from "./api";
import { Granularity } from "./lib/apiTypes";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, } from "@/components/ui/select";

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

    const parkBounds: L.LatLngBoundsExpression = [
        [42.2, -75.8], 
        [45.6, -71.0], 
    ];

    const [timeRange, setTimeRange] = useState("30d");

    const getDateRange = (range: string) => {
        const endDate = new Date();
        const startDate = new Date();

        switch (range) {
            case "7d":
                startDate.setDate(endDate.getDate() - 7);
                break;
            case "30d":
                startDate.setDate(endDate.getDate() - 30);
                break;
            case "90d":
                startDate.setDate(endDate.getDate() - 90);
                break;
            case "365d":
                startDate.setFullYear(endDate.getFullYear() - 1);
                break;
            case "all":
                startDate.setFullYear(2000);
                break;
        }

        return { startDate, endDate };
    };

    useEffect(() => {
        async function fetchTrails() {
            try {
                const res = await getTrailMetadata();

                if (res.success) {
                    setTrails(await res.json); //renders pins
                    console.log("trail metadata:", res.json);
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
    async function fetchTrailUsage() {
        try {

            const { startDate, endDate } = getDateRange(timeRange);

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
        }
    }

    if (parsedTrails.length > 0) {
        fetchTrailUsage();
    }
    }, [parsedTrails, timeRange]);

    const getTrailColor = (trailId: number, days: number, p20: number, p40: number, p60: number, p80: number) => {
        const usage = trailUsage[trailId] ?? 0;
        if (!usage || days <= 0) return "gray";

        const avg = usage / days;

        if (avg <= p20) return "#3b82f6";
        if (avg <= p40) return "#22c55e";
        if (avg <= p60) return "#eab308";
        if (avg <= p80) return "#f97316";
        return "#ef4444";
    };

    const { p20, p40, p60, p80, days } = useMemo(() => {
        const { startDate, endDate } = getDateRange(timeRange);

        const days =
            (endDate.getTime() - startDate.getTime()) /
            (1000 * 60 * 60 * 24);

        const averages = parsedTrails.map(t =>
            (trailUsage[t.id] ?? 0) / (days || 1)
        );

        const sorted = [...averages].sort((a, b) => a - b);

        const percentile = (p: number) =>
            sorted[Math.floor(p * (sorted.length - 1))] ?? 0;

        return {
            days,
            p20: percentile(0.2),
            p40: percentile(0.4),
            p60: percentile(0.6),
            p80: percentile(0.8),
        };
    }, [parsedTrails, trailUsage, timeRange]);

  return (

        <div className="h-screen w-screen relative overflow-hidden">
             <Navbar/>
                <div className="absolute top-5 right-52 z-[1000]"></div>

                <div className="absolute top-20 left-4 z-[2000] pointer-events-auto">
                    <Select
                        value={timeRange}
                        onValueChange={setTimeRange}
                    >
                        <SelectTrigger className="w-40 bg-white">
                            <SelectValue />
                        </SelectTrigger>

                        <SelectContent className="z-[5000]">
                            <SelectItem value="7d">Last 7 Days</SelectItem>
                            <SelectItem value="30d">Last 30 Days</SelectItem>
                            <SelectItem value="90d">Last 90 Days</SelectItem>
                            <SelectItem value="365d">Last Year</SelectItem>
                            <SelectItem value="all">All Time</SelectItem>
                        </SelectContent>
                    </Select>
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
                            icon={createTrailIcon(getTrailColor(trail.id, days, p20, p40, p60, p80))}
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
                                            navigate(`/dashboard?trailId=${trail.id}`)
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