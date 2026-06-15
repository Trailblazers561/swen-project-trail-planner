import React, { useState, useEffect } from 'react';
import { TrailData } from '../../api';
import './Modal.css';
import { Button } from '../templates/button';
import DeviceLogTable from "../tables/DeviceLogTable";
import { EllipsisVertical } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuItem } from "../templates/dropdown-menu"


interface Device {
  id: number;
  name: string;
  registration_id?: number;
  date_registered?: number;
  notes?: string;
  date_manufactured?: number;
  date_retired?: number;
  current_trail_id?: number;
  battery?: number;
  firmware_version?: string;
  is_blocked?: boolean;
  is_archived?: boolean;
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
  if (currentAction !== DeviceAction.VIEW_LOGS && device && device.current_trail_id && device.current_trail_id !== 0)
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
  const [currentAction, setCurrentAction] = useState<DeviceAction  | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { getDeviceMetadata, getDeviceLogs, getTrailMetadata, createDevice, updateRegistration, deleteRegistration, updateDeviceTrailAssociation, archiveDevice, blockDevice } = TrailData();

  const [deviceName, setDeviceName] = useState("");
  const [deviceSerial, setDeviceSerial] = useState("");
  const [selectedTrailId, setSelectedTrailId] = useState(0);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (isOpen) {
      loadData();
    } else {
      refreshVariables();
    }
  }, [isOpen]);

  const refreshVariables = async () => {
    setDevice(null);
    setDeviceLogs([]);
    setDeviceName("");
    setDeviceSerial("");
    setSelectedTrailId(0);
    setNotes("");
    setCurrentAction(null);
  }

  const loadData = async () => {
    try {
      if (deviceId !== 0) { 
        const [deviceResponse, deviceLogResponse, trailsResponse] = await Promise.all([
          getDeviceMetadata([deviceId]), getDeviceLogs([deviceId], 5), getTrailMetadata()
        ])

        if (deviceResponse.success && deviceLogResponse.success && trailsResponse.success) {
          const deviceData: Device[] = await deviceResponse.json;
          const deviceLogData = await deviceLogResponse.json;
          const trailsData = await trailsResponse.json;

          if (deviceData.length) {
            setDevice(deviceData.length ? deviceData[0] : null);
            setDeviceName(deviceData[0].name);
            setSelectedTrailId(deviceData[0].current_trail_id ?? 0);
            setNotes(deviceData[0].notes ?? "")

            if (deviceData[0]?.is_blocked) {
              setCurrentAction(DeviceAction.UNBLOCK_DEVICE);
            } else if (deviceData[0]?.is_archived) {
              setCurrentAction(DeviceAction.UNARCHIVE_DEVICE);
            } else if (!deviceData[0]?.date_registered || deviceData[0]?.date_registered === -1) {
              setCurrentAction(DeviceAction.SETUP_DEVICE);
            } else if (!deviceData[0]?.current_trail_id || deviceData[0]?.current_trail_id === 0) {
              setCurrentAction(DeviceAction.ASSOCIATE_TRAIL);
            } else {
              setCurrentAction(DeviceAction.VIEW_LOGS);
            }
          }
          setDeviceLogs(deviceLogData);
          setTrails(trailsData);
        } else {
          setCurrentAction(null);
          setError("Error loading data");
          console.error("Error loading data");
        }
      } else {
        setCurrentAction(DeviceAction.CREATE_DEVICE);
      }
    } catch (err) {
      console.error('Error loading data:', err);
    }
    setLoading(false);
  };

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!device || !device.registration_id) {
      setError('Unable to determine registration id');
      return;
    }

    setDeleting(true);
    setError(null);

    try {
      const response = await deleteRegistration(device.registration_id);

      if (response.success) {
        setSuccess('Registration deleted successfully!');
        setTimeout(() => {
          onUpdate();
          onClose();
          setShowDeleteConfirm(false);
          setSuccess(null);
        }, 1500);
      } else {
        const errorData = await response.json;
        setError(errorData.error || 'Failed to delete registration');
      }
    } catch (err) {
      setError('An error occurred while deleting the registration');
      console.error(err);
    } finally {
      setDeleting(false);
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
  
    setLoading(true);
    setError(null);
  
    try {
      if (currentAction === DeviceAction.CREATE_DEVICE) {
        if (!deviceName) {
          setError('Device name is required');
          return;
        }
        if (!deviceSerial) {
          setError('Device serial is required');
          return;
        }

        const response = await createDevice(deviceName, deviceSerial);

        if (response.success) {
          setSuccess('Device created successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to create device');
        }
      } else if (currentAction === DeviceAction.SETUP_DEVICE) {
        if (!deviceName) {
          setError('Device name is required');
          return;
        }
        if (deviceName === device?.name && !deviceSerial) {
          setError('New device name or new device serial is required');
          return;
        }
        if (!device?.registration_id) {
          setError("Device registration not found.");
          return;
        }

        const response = await updateRegistration(
          device?.registration_id,
          deviceName === device?.name ? undefined : deviceName,
          deviceSerial !== "" ? deviceSerial : undefined
        );

        if (response.success) {
          setSuccess('Device updated successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to update device');
        }
      } else if (currentAction === DeviceAction.ASSOCIATE_TRAIL) {
        if (!device?.id) {
          setError("Unable to find device id");
          return;
        }
        if (selectedTrailId === device?.current_trail_id) {
          setError('This is the current association.');
          return;
        }
        const response = await updateDeviceTrailAssociation(device?.id, selectedTrailId);

        if (response.success) {
          setSuccess('Device trail association created successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to update device trail association');
        }
      } else if (currentAction === DeviceAction.EDIT_INFORMATION) {
        setError("This feature is not yet implemented, sorry!");
      } else if (currentAction === DeviceAction.ARCHIVE_DEVICE) {
        if (!device?.id) {
          setError("Unable to find device id");
          return;
        }
        const response = await archiveDevice(device?.id, true);

        if (response.success) {
          setSuccess('Device archived successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to archive device');
        }
      } else if (currentAction === DeviceAction.BLOCK_DEVICE) {
        if (!device?.id) {
          setError("Unable to find device id");
          return;
        }
        const response = await blockDevice(device?.id, true);

        if (response.success) {
          setSuccess('Device blocked successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to block device');
        }
      } else if (currentAction === DeviceAction.UNARCHIVE_DEVICE) {
        if (!device?.id) {
          setError("Unable to find device id");
          return;
        }
        const response = await archiveDevice(device?.id, false);

        if (response.success) {
          setSuccess('Device unarchived successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to unarchive device');
        }
      } else if (currentAction === DeviceAction.UNBLOCK_DEVICE) {
        if (!device?.id) {
          setError("Unable to find device id");
          return;
        }
        const response = await blockDevice(device?.id, false);

        if (response.success) {
          setSuccess('Device unblocked successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            refreshVariables();
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to unblock device');
        }
      }

    } catch (err) {
      setError('An error occurred when submitting');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTrailName = (trailId: number) => {
    const trail = trails.find(t => t.id === trailId);
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
                {device && device?.current_trail_id && device?.current_trail_id !== 0 && (<div className="font-primary text-[#bbb] font-semibold">Current Trail: {getTrailName(device?.current_trail_id ?? 0)}</div>)}
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
                  <label htmlFor="device-name">Device Name:</label>
                  <input
                    id="device-name"
                    type="text"
                    value={deviceName}
                    onChange={(e) => setDeviceName(e.target.value)}
                    placeholder="Enter device name"
                    autoComplete="off"
                  />
                </div>
                <div className="form-group w-150">
                  <label htmlFor="device-serial">Device Serial:</label>
                  <input
                    id="device-serial"
                    type="text"
                    value={deviceSerial}
                    onChange={(e) => setDeviceSerial(e.target.value)}
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
            {currentAction === DeviceAction.ARCHIVE_DEVICE && (
              <div className="w-full flex flex-col justify-center">
                <ActionsDropdown currentAction={DeviceAction.EDIT_INFORMATION} device={device} setCurrentAction={setCurrentAction}/>
                <span className="font-bold text-xl mb-5">Are you sure you want to archive this device?</span>
                {device && device.current_trail_id && (<span className="text-lg mb-5">This will remove the association with the current trail.</span>)}
                <span className="text-lg mb-5">The device will no longer be able to upload data.</span>
              </div>
            )}
            {currentAction === DeviceAction.BLOCK_DEVICE && (
              <div className="w-full flex flex-col justify-center">
                <ActionsDropdown currentAction={DeviceAction.EDIT_INFORMATION} device={device} setCurrentAction={setCurrentAction}/>
                <span className="font-bold text-xl mb-5">Are you sure you want to block this device?</span>
                {device && device.current_trail_id && (<span className="text-lg mb-5">This will remove the association with the current trail.</span>)}
                <span className="text-lg mb-5">The device will no longer be able to upload data.</span>
                <span className="text-red-500 text-lg mb-5">Only block this device if you have lost access to the device.</span>
              </div>
            )}
            {currentAction === DeviceAction.UNARCHIVE_DEVICE && (
              <div className="w-full flex flex-col justify-center">
                <span className="font-bold text-xl mb-5">This device is currently archived.</span>
                <span className="text-lg mb-5">Unarchive this device to perform device actions.</span>
              </div>
            )}
            {currentAction === DeviceAction.UNBLOCK_DEVICE && (
              <div className="w-full flex flex-col justify-center">
                <span className="font-bold text-xl mb-5">This device is currently blocked.</span>
                <span className="text-lg mb-5">Unblock this device to perform device actions.</span>
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
          {currentAction === DeviceAction.ARCHIVE_DEVICE && (
            <div className="modal-footer">
              <Button variant="delete" disabled={loading}>
                {loading ? 'Archiving...' : 'Archive Device'}
              </Button>
            </div>
          )}
          {currentAction === DeviceAction.BLOCK_DEVICE && (
            <div className="modal-footer">
              <Button variant="delete" disabled={loading}>
                {loading ? 'Blocking...' : 'Block Device'}
              </Button>
            </div>
          )}
          {currentAction === DeviceAction.UNARCHIVE_DEVICE && (
            <div className="modal-footer">
              <Button variant="primary" disabled={loading}>
                {loading ? 'Unarchiving...' : 'Unarchive Device'}
              </Button>
            </div>
          )}
          {currentAction === DeviceAction.UNBLOCK_DEVICE && (
            <div className="modal-footer">
              <Button variant="primary" disabled={loading}>
                {loading ? 'Unblocking...' : 'Unblock Device'}
              </Button>
            </div>
          )}
        </form>

        {showDeleteConfirm && (
          <div className="modal-overlay" style={{ zIndex: 1001 }} onClick={() => setShowDeleteConfirm(false)}>
            <div className="modal-content max-w-200!" style={{ maxWidth: '400px' }} onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Confirm Delete</h2>
                <button className="modal-close" onClick={() => setShowDeleteConfirm(false)}>×</button>
              </div>
              <div className="modal-body">
                <p style={{ marginBottom: '15px', color: '#333' }}>
                  <strong style={{ color: '#dc3545' }}>Warning:</strong> This action cannot be undone.
                </p>
                <p style={{ marginBottom: '15px', color: '#333' }}>
                  Deleting this device will permanently remove:
                </p>
                <ul style={{ marginLeft: '20px', marginBottom: '15px', color: '#333' }}>
                  <li>The device and any current registration information</li>
                </ul>
                <p style={{ fontWeight: 'bold', color: '#dc3545', fontSize: '16px' }}>
                  Are you sure you want to delete "{device?.name}"?
                </p>
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
              </div>
              <div className="modal-popup-footer">
                <button type="button" onClick={() => setShowDeleteConfirm(false)} disabled={deleting || success !== null} data-testid="cancel-delete">
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="delete-button"
                  data-testid="confirm-delete"
                >
                  {deleting ? 'Deleting...' : 'Yes, Delete Device'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeviceModal;