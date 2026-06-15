import { useState } from "react";
import { TrailData } from "./api";
import TrailDataTable from "./components/tables/TrailDataTable";

interface Device {
    device_id: string;
    associated_trail: string;
    weekly_count: string;
    firmware: string;
    battery: string;
    last_call_in: string;
}



const DeviceManagementPage = () => {
    const [devices, setDevices] = useState<Device[]>([]);    
    const [DeviceListData, setDeviceListData] = useState<Array<Device>>([]);

    const { getDeviceMetadata } = TrailData()

    const loadDevices = async () => {
        try {
            const response = await getDeviceMetadata();

            if (response.success) {
                const data: Device[] = await response.json;

                console.log("Devices:", data);

                setDevices(data.map((device) => device.device_id));

                setDeviceListData(
                    data.map((device) => ({
                        device_id: device.device_id,
                        associated_trail: device.associated_trail,
                        weekly_count: device.weekly_count,
                        firmware: device.firmware,
                        battery: device.battery,
                        last_call_in: device.last_call_in,
                    }))
                );
            }
        } catch (error) {
            console.error("Error loading users:", error);
        }
    };
    
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
                        <TrailDataTable data={DeviceListData} />
                    </div>
                )}
            </div>
        </div>
    );
}


export default DeviceManagementPage;