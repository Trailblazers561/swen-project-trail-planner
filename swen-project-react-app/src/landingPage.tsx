import { useNavigate } from "react-router-dom";
import { Button } from "@/components/templates/button";
import { MapContainer, TileLayer, Marker, Popup, ZoomControl, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";
import "leaflet/dist/leaflet.css";
import { useState, useEffect, useMemo } from "react";
import { LoaderCircle } from "lucide-react";
import { TrailData } from "./api";
import moment from "moment-timezone";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/templates/select";
import { useDate, DatePreset } from "@/DateContext.tsx"
import { DatePickerWithRange } from "./components/templates/daterangepicker.tsx";
import { DateRange } from "node_modules/react-day-picker/dist/esm/types/shared";

const LandingPage = () => {

    const navigate = useNavigate();

    const [showLegend, setShowLegend] = useState(false);

    const [displayedUsage, setDisplayedUsage] = useState<Record<number, number>>({});

    const [zoom, setZoom] = useState(8);

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

    const { getTrailMetadata, getHeatmapData } = TrailData();

    const [trails, setTrails] = useState<any[]>([]);
    const [trailUsage] = useState<Record<number, number>>({});
    const [loadingUsage, setLoadingUsage] = useState(false);

    const parkBounds: L.LatLngBoundsExpression = [
        [42.2, -75.8],
        [45.6, -71.0],
    ];

    
    const { startDate, endDate, datePreset, setStartDate, setEndDate, setDatePreset } = useDate();
    const [range, setRange] = useState<DateRange | undefined>({ from: startDate ?? undefined, to: endDate ?? undefined })

    const handleStartDateChange = (startDate: Date | null) => {
        setStartDate(startDate);
    };

    const handleEndDateChange = (endDate: Date | null) => {
        setEndDate(endDate);
    };

    const handleDateRangeChange = (range: DateRange | undefined) => {
        const timezoneRange: DateRange = {from: undefined, to: undefined};
        if (range?.from) {
            const userISO = moment(range.from).tz(Intl.DateTimeFormat().resolvedOptions().timeZone).format("YYYY-MM-DD");
            const newYorkOffset = moment(range.from).tz("America/New_York").format("Z");
            timezoneRange.from = new Date(`${userISO}T00:00:00${newYorkOffset}`);
        }
        if (range?.to) {
            const userISO = moment(range.to).tz(Intl.DateTimeFormat().resolvedOptions().timeZone).format("YYYY-MM-DD");
            const newYorkOffset = moment(range.to).tz("America/New_York").format("Z");
            timezoneRange.to = new Date(`${userISO}T23:00:00${newYorkOffset}`);
        }

        setRange(range);
        setStartDate(timezoneRange?.from ?? null);
        setEndDate(timezoneRange?.to ?? null);
        handleStartDateChange(timezoneRange?.from ?? null);
        handleEndDateChange(timezoneRange?.to ?? null);
    }

    useEffect(() => {
        async function fetchTrails() {
            try {
                const res = await getTrailMetadata();
                if (res.success) {
                    const trailData = await res.json;
                    setTrails(trailData);
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

                const response = await getHeatmapData(trailIds, startDate, endDate);
                if (!response.success) return;

                const data = await response.json;

                setDisplayedUsage(data);

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


    const getTrailColor = (trailId: number) => {

        if (loadingUsage) {
            const existingUsage = trailUsage[trailId];
            if (!existingUsage) {
                return "gray";
            }
        }

        const intensity = displayedUsage[trailId];

        if (intensity === undefined || intensity === null) return "gray";

        switch (true) {
            case intensity <= .2:
                return "#3b82f6";

            case intensity <= .4:
                return "#22c55e";

            case intensity <= .6:
                return "#eab308";

            case intensity <= .8:
                return "#f97316";

            default:
                return "#ef4444";
        }
    };

    const getUsageLabel = (value: number | null | undefined) => {
        if (value == null) return "No Data";
        if (value <= 0.2) return "Low";
        if (value <= 0.4) return "Moderate";
        if (value <= 0.6) return "Busy";
        if (value <= 0.8) return "Very Busy";
        return "Extremely Busy";
    };

    function ZoomWatcher({ setZoom }: { setZoom: (zoom: number) => void }) {
        useMapEvents({
            zoomend: (event) => {
                setZoom(event.target.getZoom());
            },
        });

        return null;
    }

    function HeatmapLayer({ trails, heatmapData }: { trails: any[]; heatmapData: Record<number, number> }) {
        const map = useMap();

        useEffect(() => {
            const heatPoints = trails.filter((trail) => heatmapData[trail.id] != null)
                .map((trail) => [
                    trail.latitude,
                    trail.longitude,
                    heatmapData[trail.id] as number,
                ]);

            const heatLayer = (L as any).heatLayer(heatPoints, {
                radius: 40,
                blur: 30,
                maxZoom: 8,
                max: 1.0,
                gradient: {
                    0.2: "#3b82f6",
                    0.4: "#22c55e",
                    0.6: "#eab308",
                    0.8: "#f97316",
                    1.0: "#ef4444",
                },
            });
            heatLayer.addTo(map);
            return () => {
                map.removeLayer(heatLayer);
            };
        }, [map, trails, heatmapData]);
        return null;
    }


    return (

        <div className="h-screen w-screen relative overflow-hidden">

            <div className="absolute top-20 left-4 z-9999 pointer-events-auto">
                <div className="bg-white rounded-lg  shadow-lg p-4 border min-w-[420px]">

                    <div className="font-semibold mb-3 text-center">
                        Time Frame
                    </div>

                    <div className="flex justify-center">
                        <Select
                            value={datePreset}
                            onValueChange={(value) => setDatePreset(value as DatePreset)}
                        >
                            <SelectContent className="z-10000" />
                            <SelectTrigger className="w-48 bg-white">
                                <SelectValue />
                            </SelectTrigger>

                            <SelectContent className="z-10000" position="popper" side="bottom" sideOffset={4}>
                                <SelectItem value="day">Yesterday</SelectItem>
                                <SelectItem value="week">Last Week</SelectItem>
                                <SelectItem value="fortnight">Last 2 Weeks</SelectItem>
                                <SelectItem value="month">Last Month</SelectItem>
                                <SelectItem value="custom">Custom</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    {datePreset === DatePreset.Custom && (
                        <div className="flex justify-center gap-2 mt-2">
                            <DatePickerWithRange value={range} onChange={handleDateRangeChange} />
                        </div>
                    )}

                    <hr className="my-3" />

                    <button
                        className="w-full text-left font-semibold text-sm"
                        onClick={() => setShowLegend(!showLegend)}
                    >
                        Trail Usage Legend {showLegend ? "▼" : "▶"}
                    </button>

                    {showLegend && (
                        <div className="grid grid-cols-2 gap-x-4 gap-y-2 mt-3 text-xs">
                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded"
                                    style={{ background: "#3b82f6" }}
                                />
                                <span>0–19 hikers/day</span>
                            </div>

                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded"
                                    style={{ background: "#22c55e" }}
                                />
                                <span>20–34 hikers/day</span>
                            </div>

                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded"
                                    style={{ background: "#eab308" }}
                                />
                                <span>35–49 hikers/day</span>
                            </div>

                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded"
                                    style={{ background: "#f97316" }}
                                />
                                <span>50–74 hikers/day</span>
                            </div>

                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded"
                                    style={{ background: "#ef4444" }}
                                />
                                <span>75+ hikers/day</span>
                            </div>

                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded bg-gray-400" />
                                <span>No Data</span>
                            </div>
                        </div>
                    )}

                </div>
            </div>
            {loadingUsage && (
                <div className="absolute inset-0 z-9998 flex items-center justify-center pointer-events-none bg-black/20">
                    <LoaderCircle
                        size={80}
                        strokeWidth={2}
                        className="animate-spin text-navbar"
                    />
                </div>
            )}
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

                <ZoomWatcher setZoom={setZoom} />

                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png"
                />

                <HeatmapLayer trails={parsedTrails} heatmapData={displayedUsage} />

                <ZoomControl position="bottomright" />

                {zoom >= 9 && parsedTrails.map((trail) => (
                    <Marker
                        key={trail.id}
                        position={[trail.latitude, trail.longitude]}
                        icon={createTrailIcon(getTrailColor(trail.id))}
                    >
                        <Popup>
                            <div
                                onClick={(e) => e.stopPropagation()}
                                className="space-y-2"
                            >
                                <div>
                                    <strong>{trail.name}</strong>{" "}
                                    <span className="text-gray-500 ml-2">(ID: {trail.id})</span>
                                    <br />
                                    {trail.notes}
                                    <div>
                                        <strong>Trail Usage:</strong>{" "}
                                        {getUsageLabel(displayedUsage[trail.id])}
                                    </div>
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