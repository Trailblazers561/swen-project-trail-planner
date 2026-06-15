import { useState, useEffect } from "react";
import { TrailData } from "./api";
import DeviceDataTable from "./components/tables/DeviceDataTable";
import { Granularity } from "./lib/apiTypes";
import DeviceModal from "./components/modals/DeviceModal";
import type { DeviceRow } from "./components/tables/DeviceDataTable";

// turn getDeviceMetadata into a dictionary

// the last call in is a timestamp, we need to convert it to a date


const DeviceManagementPage = () => {
    const [selectedDevice, setSelectedDevice] = useState<DeviceRow | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleRowClick = (device: DeviceRow) => {
        setSelectedDevice(device);
        setIsModalOpen(true);
    };

    const [loading, setLoading] = useState(true);
    const [devices, setDevices] = useState<DeviceRow[]>([]);
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
            
            const devices: DeviceRow[] = metadata.map((device: any) => {
                const info = trailInformation.get(device.current_trail_id);

                return {
                    name: device.name,
                    id: device.id,
                    trailName: device.current_trail_id ? getTrailName(device.current_trail_id) : null,
                    weeklyCount: info ? info.count : 0,   // bug, retrieve from new api endpoint
                    firmware_version: device.firmware_version,
                    batteryStatus: device ? device.battery : 0,
                    lastUpdated: device.last_updated
                    ? new Date(device.last_updated * 1000).toLocaleDateString("en-US")
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
                        <DeviceDataTable data={devices} loading={false} onRowClick={handleRowClick} />
                    </div>
                )}
            </div> 
            <DeviceModal
                isOpen={isModalOpen}
                deviceId={selectedDevice?.id ?? 0}
                onClose={() => setIsModalOpen(false)}
                onUpdate={loadDevices}
            />
        </div>
    );
}


export default DeviceManagementPage;