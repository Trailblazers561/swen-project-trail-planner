import React, { useState, useEffect } from 'react';
import { TrailData } from '../../api';
import './Modal.css';
import { Button } from '../templates/button';
import DeviceLogTable from "../tables/DeviceLogTable";
import { EllipsisVertical } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuGroup, DropdownMenuItem, DropdownMenuSeparator } from "../templates/dropdown-menu"


interface Device {
  id: number;
  notes?: string;
  date_manufactured?: number;
  date_retired?: number;
  current_trail_id?: number;
  battery?: number;
  firmware_version?: string;
  is_blocked?: boolean;
  is_retired?: boolean;
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

enum DeviceAction {
  CREATE_DEVICE,
  SETUP_DEVICE,
  VIEW_LOGS,
  ASSOCIATE_TRAIL,
  EDIT_INFORMATION,
  ARCHIVE_DEVICE,
  BLOCK_DEVICE,
  UNARCHIVE_DEVICE,
  UNBLOCK_DEVICE,
}

interface ActionsDropdownProps {
  currentAction: DeviceAction;
  device: Device | null;
  setCurrentAction: (action: DeviceAction) => void;
}

function ActionsDropdown({currentAction, device, setCurrentAction}: ActionsDropdownProps) {
  const actionList: DeviceAction[] = [];
  if (currentAction !== DeviceAction.VIEW_LOGS && device && device.current_trail_id !== 0)
    actionList.push(DeviceAction.VIEW_LOGS);
  if (currentAction !== DeviceAction.ASSOCIATE_TRAIL)
    actionList.push(DeviceAction.ASSOCIATE_TRAIL);
  if (currentAction !== DeviceAction.EDIT_INFORMATION)
    actionList.push(DeviceAction.EDIT_INFORMATION);
  if (currentAction !== DeviceAction.ARCHIVE_DEVICE)
    actionList.push(DeviceAction.ARCHIVE_DEVICE);
  if (currentAction !== DeviceAction.BLOCK_DEVICE)
    actionList.push(DeviceAction.BLOCK_DEVICE);

  return (
    <div className="w-full items-start mb-5">
      <div className="flex gap-2 text-xl items-center">
      <DropdownMenu>
          <DropdownMenuTrigger asChild>
              <Button className="bg-white " size="icon" id="user-icon-button">
                  <EllipsisVertical />
              </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="z-1000 font-bold translate-x-[calc(50%-18px)]">
            {actionList.includes(DeviceAction.VIEW_LOGS) && (
              <DropdownMenuItem onClick={() => {setCurrentAction(DeviceAction.VIEW_LOGS)}}>View Logs</DropdownMenuItem>
            )}
            {actionList.includes(DeviceAction.ASSOCIATE_TRAIL) && (
              <DropdownMenuItem onClick={() => {setCurrentAction(DeviceAction.ASSOCIATE_TRAIL)}}>Associate Trail</DropdownMenuItem>
            )}
            {actionList.includes(DeviceAction.EDIT_INFORMATION) && (
              <DropdownMenuItem onClick={() => {setCurrentAction(DeviceAction.EDIT_INFORMATION)}}>Update Device Info</DropdownMenuItem>
            )}
            {actionList.includes(DeviceAction.ARCHIVE_DEVICE) && (
              <DropdownMenuItem className="text-logout!" onClick={() => {setCurrentAction(DeviceAction.ARCHIVE_DEVICE)}}>Archive</DropdownMenuItem>
            )}
            {actionList.includes(DeviceAction.BLOCK_DEVICE) && (
              <DropdownMenuItem className="text-logout!" onClick={() => {setCurrentAction(DeviceAction.BLOCK_DEVICE)}}>Block</DropdownMenuItem>
            )}
          </DropdownMenuContent>
      </DropdownMenu>
      Actions
      </div>
    </div>
  );
}

interface DeviceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
  deviceId: number;
}

const DeviceModal: React.FC<DeviceModalProps> = ({ isOpen, onClose, onUpdate, deviceId }) => {
  const [device, setDevice] = useState<Device | null>(null);
  const [deviceLogs, setDeviceLogs] = useState<DeviceLog[]>([]);
  const [trails, setTrails] = useState<Trail[]>([]);
  const [currentAction, setCurrentAction] = useState<DeviceAction  | null>(deviceId === 0 ? DeviceAction.CREATE_DEVICE : null);
//   const [trails, setTrails] = useState<Trail[]>([]);
//   const [selectedDevice, setSelectedDevice] = useState<number>(0);
//   const [selectedTrail, setSelectedTrail] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { getDeviceMetadata, getDeviceLogs, getTrailMetadata } = TrailData();

  const [deviceName, setDeviceName] = useState("");
  const [deviceSerial, setDeviceSerial] = useState("");
  const [selectedTrailId, setSelectedTrailId] = useState(0);
  const [notes, setNotes] = useState("");

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
      if (deviceId !== 0) { 
        const [deviceResponse, deviceLogResponse, trailsResponse] = await Promise.all([
          getDeviceMetadata([deviceId]), getDeviceLogs([deviceId], 5), getTrailMetadata()
        ])

        if (deviceResponse.success && deviceLogResponse.success) {
          const deviceData = await deviceResponse.json;
          const deviceLogData = await deviceLogResponse.json;
          const trailsData = await trailsResponse.json;

          if (deviceData.length) {
            setDevice(deviceData.length ? deviceData[0] : null);
            setDeviceName(deviceData[0].name);
            setSelectedTrailId(deviceData[0]?.current_trail_id)

            // if (deviceData[0]?.) { // Device not setup
            //   setCurrentAction(DeviceAction.SETUP_DEVICE);
            // } else if (true) { // Trail Not associated
            //   setCurrentAction(DeviceAction.ASSOCIATE_TRAIL);
            // }
          }
          setDeviceLogs(deviceLogData);
          setTrails(trailsData);
        }
      }
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

  const getTrailName = (trailId: number) => {
    const trail = trails.find(t => t.id === trailId);
    console.log("TRL", trail);
    return trail ? trail.name : `Trail ${trailId}`;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="device-modal">
      <div className="modal-content modal-content-extra-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header bg-navbar p-4!">
            <div className="flex flex-col text-left">
                <div className="font-primary text-white font-semibold text-xl">{deviceId === 0 ? "Create Device" : "Manage Device"}</div>
                {deviceId !== 0 && (<div className="font-primary text-[#bbb] font-semibold">Device ID: {deviceId}</div>)}
                {device && device?.current_trail_id !== 0 && (<div className="font-primary text-[#bbb] font-semibold">Current Trail: {getTrailName(device?.current_trail_id ?? 0)}</div>)}
            </div>
          <button className="modal-close" onClick={onClose} data-testid="modal-close">×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {currentAction === DeviceAction.CREATE_DEVICE && (
              <div className="flex flex-col items-center">
                <div className="form-group w-150">
                  <label htmlFor="device-name">Device Name: <span style={{ color: 'red' }}>*</span></label>
                  <input
                    id="device-name"
                    type="text"
                    value={deviceName}
                    onChange={(e) => setDeviceName(e.target.value)}
                    required
                    placeholder="Enter device name"
                    autoComplete="off"
                  />
                </div>
                <div className="form-group w-150">
                  <label htmlFor="device-serial">Device Serial: <span style={{ color: 'red' }}>*</span></label>
                  <input
                    id="device-serial"
                    type="text"
                    value={deviceSerial}
                    onChange={(e) => setDeviceSerial(e.target.value)}
                    required
                    placeholder="Enter device serial"
                    autoComplete="off"
                  />
                </div>
              </div>
            )}
            {currentAction === DeviceAction.SETUP_DEVICE && (
              <div className="flex flex-col items-center">
                <span className="font-bold text-xl mb-5">Please perform device setup process to associate this device.</span>
                <div className="form-group w-150">
                  <label htmlFor="device-name">Device Name: <span style={{ color: 'red' }}>*</span></label>
                  <input
                    id="device-name"
                    type="text"
                    value={deviceName}
                    onChange={(e) => setDeviceName(e.target.value)}
                    required
                    placeholder="Enter device name"
                    autoComplete="off"
                  />
                </div>
                <div className="form-group w-150">
                  <label htmlFor="device-serial">Device Serial: <span style={{ color: 'red' }}>*</span></label>
                  <input
                    id="device-serial"
                    type="text"
                    value={deviceSerial}
                    onChange={(e) => setDeviceSerial(e.target.value)}
                    required
                    placeholder="Enter device serial"
                    autoComplete="off"
                  />
                </div>
              </div>
            )}
            {currentAction === DeviceAction.VIEW_LOGS && (
              <div className="w-full flex flex-col justify-center">
                <ActionsDropdown currentAction={DeviceAction.VIEW_LOGS} device={device} setCurrentAction={setCurrentAction}/>
                <DeviceLogTable data={deviceLogs} loading={loading}/>
              </div>
            )}
            {currentAction === DeviceAction.ASSOCIATE_TRAIL && (
              <div className="w-full flex flex-col justify-center">
                <ActionsDropdown currentAction={DeviceAction.ASSOCIATE_TRAIL} device={device} setCurrentAction={setCurrentAction}/>
                <div className="form-group w-150 m-auto">
                  <label htmlFor="trail-select">Select Trail:</label>
                  <select
                    id="trail-select"
                    value={selectedTrailId}
                    onChange={(e) => setSelectedTrailId(Number(e.target.value))}
                    required
                  >
                    <option value={0}>No Trail</option>
                    {trails.map((trail) => (
                      <option key={trail.id} value={trail.id}>
                        {trail.name} (ID: {trail.id})
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}
            {currentAction === DeviceAction.EDIT_INFORMATION && (
              <div className="w-full flex flex-col justify-center">
                <ActionsDropdown currentAction={DeviceAction.EDIT_INFORMATION} device={device} setCurrentAction={setCurrentAction}/>
                <div className="form-group w-150 m-auto">
                  <label htmlFor="device-name">Device Name: <span style={{ color: 'red' }}>*</span></label>
                  <input
                    id="device-name"
                    type="text"
                    value={deviceName}
                    onChange={(e) => setDeviceName(e.target.value)}
                    required
                    placeholder="Enter device name"
                    autoComplete="off"
                  />
                </div>
                <div className="form-group w-150 m-auto">
                  <label htmlFor="notes">Notes (optional):</label>
                  <textarea
                    id="notes"
                    rows={3}
                    maxLength={150}
                    style={{resize: "none"}}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Enter notes"
                    autoComplete="off"
                  />
                </div>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </div>
          {currentAction === DeviceAction.CREATE_DEVICE && (
            <div className="modal-footer">
              <Button variant="primary" disabled={loading}>
                {loading ? 'Creating...' : 'Create Device'}
              </Button>
            </div>
          )}
          {currentAction == DeviceAction.SETUP_DEVICE && (
            <div className="modal-footer">
              <div className="flex justify-between w-full">
                <button
                  type="button"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={loading || deleting}
                  className="delete-button font-medium h-9 flex items-center"
                  data-testid="delete-button"
                >
                  Delete Device
                </button>
                <Button variant="primary" disabled={loading} data-testid="confirm-button">
                  {loading ? 'Updating...' :'Update Device'}
                </Button>
              </div>
            </div>
          )}
          {currentAction === DeviceAction.ASSOCIATE_TRAIL && (
            <div className="modal-footer">
              <Button variant="primary" disabled={loading}>
                {loading ? 'Associating...' : 'Associate Device'}
              </Button>
            </div>
          )}
          {currentAction === DeviceAction.EDIT_INFORMATION && (
            <div className="modal-footer">
              <Button variant="primary" disabled={loading}>
                {loading ? 'Updating...' : 'Update Device'}
              </Button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default DeviceModal;