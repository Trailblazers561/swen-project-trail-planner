import React, { useState, useEffect } from 'react';
import { TrailData } from '../../api';
import './Modal.css';
import { Button } from '../templates/button';
import DeviceLogTable from "../tables/DeviceLogTable";

interface Device {
  id: number;
  current_trail_id: number;
  battery?: number;
}

interface DeviceLog {
    device_id: number;
    time: number;
    battery: number;
    firmware_version: string;
    count: number;
    rssi: number;
    rsrp: number;
    rsrq: number;
}

interface Trail {
  id: number;
  name: string;
}

interface DeviceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
  deviceId: number;
}

const DeviceModal: React.FC<DeviceModalProps> = ({ isOpen, onClose, onUpdate, deviceId }) => {
  const [deviceLogs, setDeviceLogs] = useState<DeviceLog[]>([]);
//   const [trails, setTrails] = useState<Trail[]>([]);
//   const [selectedDevice, setSelectedDevice] = useState<number>(0);
//   const [selectedTrail, setSelectedTrail] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { getDeviceLogs } = TrailData();

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

//   useEffect(() => {
//     if (selectedDevice) {
//       const device = devices.find(d => d.id === selectedDevice);
//       if (device?.current_trail_id)
//         setSelectedTrail(device?.current_trail_id);
//       else
//         setSelectedTrail(0);
//     }
//   }, [selectedDevice])

  const loadData = async () => {
    try {
        const deviceLogResponse = await getDeviceLogs([deviceId], 5);
        if (deviceLogResponse.success) {
            const deviceLogData = await deviceLogResponse.json;
            setDeviceLogs(deviceLogData);
        }
    //   const [devicesResponse, trailsResponse] = await Promise.all([
    //     getDeviceMetadata(),
    //     getTrailMetadata(),
    //   ]);

    //   if (devicesResponse.success && trailsResponse.success) {
    //     const devicesData = await devicesResponse.json;
    //     const trailsData = await trailsResponse.json;

    //     setDevices(devicesData);
    //     setTrails(trailsData);
    //   }
    } catch (err) {
      console.error('Error loading data:', err);
    }
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    // e.preventDefault();
    // if (!selectedDevice) {
    //   setError("Please select a device");
    //   return;
    // }

    // const device = devices.find(d => d.id === selectedDevice);
    // if (device?.current_trail_id === selectedTrail) {
    //   if (selectedTrail)
    //     setError("Device is already associated with this trail");
    //   else
    //     setError("Device is already not associated with a trail");
    //   return;
    // }

    // setLoading(true);
    // setError(null);

    // try {
    //   const response = await updateDeviceTrailAssociation(selectedDevice, selectedTrail);

    //   if (response.success) {
    //     setSuccess('Device associated successfully!');
    //     setTimeout(() => {
    //       onUpdate();
    //       onClose();
    //       setSelectedDevice(0);
    //       setSelectedTrail(0);
    //       setSuccess(null);
    //     }, 1500);
    //   } else {
    //     const errorData = await response.json;
    //     setError(errorData.error || 'Failed to associate device');
    //   }
    // } catch (err) {
    //   setError('An error occurred while associating the device');
    //   console.error(err);
    // } finally {
    //   setLoading(false);
    // }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="associate-device-modal">
      <div className="modal-content modal-content-extra-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header bg-navbar p-4!">
            <div className="flex flex-col text-left">
                <div className="font-primary text-white font-semibold text-xl">Manage Device</div>
                <div className="font-primary text-[#bbb] font-semibold">Device ID: {deviceId}</div>
            </div>
          <button className="modal-close" onClick={onClose} data-testid="modal-close">×</button>
        </div>
        <form onSubmit={handleSubmit}>
            <div className="modal-body">
                <DeviceLogTable data={deviceLogs} loading={loading}/>
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
            </div>
          {/* <div className="modal-footer">
            <Button variant="primary" disabled={loading || !selectedDevice} data-testid="associate-device-button">
              {loading ? 'Associating...' : 'Associate Device'}
            </Button>
          </div> */}
        </form>
      </div>
    </div>
  );
};

export default DeviceModal;