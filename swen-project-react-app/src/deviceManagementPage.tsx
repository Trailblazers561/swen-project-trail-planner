import { useState, useEffect } from "react";
import { TrailData } from "./api";
import DeviceDataTable from "./components/tables/DeviceDataTable";
import { Granularity } from "./lib/apiTypes";

interface Device {
    name: string;
    id: number;
    trailName: string;
    weeklyCount: number;
    firmware_version: string;
    batteryStatus: number;
    lastUpdated: string | null;
}

// turn getDeviceMetadata into a dictionary

// the last call in is a timestamp, we need to convert it to a date


const DeviceManagementPage = () => {
    const [loading, setLoading] = useState(true);
    const [devices, setDevices] = useState<Device[]>([]);
    const [trails, setTrails] = useState<{ id: number; name: string }[]>([]);

    const { getDeviceMetadata, getTrailLogs, getTrailMetadata } = TrailData();



    const loadDevices = async () => {
        try {
            setLoading(true);

            const metadataResponse = await getDeviceMetadata();

            if (!metadataResponse.success) {
                setDevices([]);
                return;
            }

            const metadata = await metadataResponse.json;
            console.log("Devices:", metadata);

            
            const trailMetadataResponse = await getTrailMetadata();

            let trails:{ id: number; name: string }[] = [];
            const getTrailName = (trailId: number) => {
                const trail = trails.find(t => t.id === trailId);
                return trail ? trail.name : `Trail ${trailId}`;
                };
            if (trailMetadataResponse.success) {
                const trailData = await trailMetadataResponse.json;
                setTrails(trailData);
                trails = trailData;
            }
            
            const trailIds = metadata.map((d: any) => d.id);

            const today = new Date();
            const oneWeekAgo = new Date();
            oneWeekAgo.setDate(today.getDate() - 7);

            const logsResponse = await getTrailLogs(
                trailIds,
                oneWeekAgo,
                today,
                Granularity.Day
            );

            if (!logsResponse.success) {
                setDevices([]);
                return;
            }

            const logs = await logsResponse.json;

            const trailInformation = new Map<
                number,
                { count: number; battery: number; lastUpdated: number }
            >();

            logs.forEach((log: any) => {
                const trailId = log.trail_id;

                const current =
                    trailInformation.get(trailId) || {
                        count: 0,
                        battery: 0,
                        lastUpdated: 0,
                    };

                current.count += log.count;

                if (log.start > current.lastUpdated) {
                    current.battery = log.battery;
                }

                current.lastUpdated = Math.max(
                    current.lastUpdated,
                    log.start
                );

                trailInformation.set(trailId, current);
            });
            
            const devices: Device[] = metadata.map((device: any) => {
                const info = trailInformation.get(device.current_trail_id);

                return {
                    name: device.name,
                    id: device.current_trail_id,
                    trailName: getTrailName(device.current_trail_id),
                    weeklyCount: info ? info.count : 0,
                    firmware_version: device.firmware_version,
                    batteryStatus: device ? device.battery : 0,
                    lastUpdated: device
                    ? new Date(device.lastUpdated * 1000).toLocaleDateString("en-US")
                    : null,
                };
            });
            
            setDevices(devices);
        } catch (error) {
            console.error("Error loading devices:", error);
        } finally {
        setLoading(false);
        }
    };

    useEffect(() => {
        loadDevices();
    }, []);


    return (
        <div className="flex flex-col">
            <div className="w-full bg-[var(--color-button-secondary)]">
                <div className="font-semibold text-2xl p-2 ml-2 text-left"> Device Management </div>
            </div>

            <div className="p-4">
                {loading ? (
                    <div>Loading...</div>
                ) : devices.length === 0 ? (
                    <div>No devices found</div>
                ) : (
                    <div className="pt-4 m-4">
                        <DeviceDataTable data={devices} loading={false} />
                    </div>
                )}
            </div>
        </div>
    );
}


export default DeviceManagementPage;