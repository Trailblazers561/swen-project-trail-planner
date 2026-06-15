import { useState, useEffect } from "react";
import { TrailData } from "./api";
import DeviceDataTable from "./components/tables/DeviceDataTable";

interface Device {
    name: number;
    current_trail_id: string;
    weekly_count: number;
    firmware: string;
    batteryStatus: number;
    lastUpdated: string | null;
}

// turn getDeviceMetadata into a dictionary

// the last call in is a timestamp, we need to convert it to a date

const DeviceManagementPage = () => {
    const [devices, setDevices] = useState<Array<Device>>([]);

    const { getDeviceMetadata } = TrailData();

    const loadDevices = async () => {
        try {
            const response = await getDeviceMetadata();

            if (response.success) {
                const data: Device[] = await response.json;

                console.log("Devices:", data);

                setDevices(data);
            }
        } catch (error) {
            console.error("Error loading users:", error);
        }
    };

    useEffect(() => {loadDevices();}, []);

    return (
        <div className="flex flex-col">

            <div className="w-full bg-[var(--color-button-secondary)]">
                <div className="font-semibold text-2xl p-2 ml-2 text-left"> Device Management </div>
            </div>

            <div className="p-4">
                {devices.length === 0 ? (
                    <div>Loading...</div>
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