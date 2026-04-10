import React, { useState, useEffect } from 'react';
import { TrailData } from '../api';
import './Modal.css';
import { Button } from './ui/button';

interface Device {
  id: string;
  current_trail_id: number;
  battery?: number;
}

interface Trail {
  id: number;
  name: string;
}

interface AssociateDeviceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

const AssociateDeviceModal: React.FC<AssociateDeviceModalProps> = ({ isOpen, onClose, onUpdate }) => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [trails, setTrails] = useState<Trail[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [selectedTrail, setSelectedTrail] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { getDeviceMetadata, getTrailMetadata, updateDeviceTrailAssociation } = TrailData();

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    try {
      const [devicesResponse, trailsResponse] = await Promise.all([
        getDeviceMetadata(),
        getTrailMetadata(),
      ]);

      if (devicesResponse.success && trailsResponse.success) {
        const devicesData = await devicesResponse.json;
        const trailsData = await trailsResponse.json;

        setDevices(devicesData);
        setTrails(trailsData);
      }
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDevice || !selectedTrail) {
      setError('Please select both a device and a trail');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await updateDeviceTrailAssociation(selectedDevice, selectedTrail);

      if (response.success) {
        setSuccess('Device associated successfully!');
        setTimeout(() => {
          onUpdate();
          onClose();
          setSelectedDevice('');
          setSelectedTrail(0);
          setSuccess(null);
        }, 1500);
      } else {
        const errorData = await response.json;
        setError(errorData.error || 'Failed to associate device');
      }
    } catch (err) {
      setError('An error occurred while associating the device');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // Separate devices into unpaired (trail_id = 0) and paired
  const unpairedDevices = devices.filter(d => d.current_trail_id === 0);
  const pairedDevices = devices.filter(d => d.current_trail_id !== 0);

  const getTrailName = (trailId: number) => {
    const trail = trails.find(t => t.id === trailId);
    return trail ? trail.name : `Trail ${trailId}`;
  };

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="associate-device-modal">
      <div className="modal-content modal-content-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header bg-[var(--color-navbar)]">
          <div className="font-primary text-white font-semibold">Associate Device to Trail</div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="device-sections">
              <div className="device-section">
                <h3>Needs to be Paired (trail_id = 0)</h3>
                {unpairedDevices.length === 0 ? (
                  <p className="no-devices">No unpaired devices</p>
                ) : (
                  <div className="device-list">
                    {unpairedDevices.map((device) => (
                      <div
                        key={device.id}
                        className={`device-item ${selectedDevice === device.id ? 'selected' : ''}`}
                        onClick={() => setSelectedDevice(device.id)}
                        data-testid="unpaired-device-item"
                      >
                        <div className="device-info">
                          <strong data-testid="associate-device-id">{device.id}</strong>
                          {device.battery !== undefined && (
                            <span className="battery">Battery: {device.battery}%</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="device-section">
                <h3>Already Paired</h3>
                {pairedDevices.length === 0 ? (
                  <p className="no-devices">No paired devices</p>
                ) : (
                  <div className="device-list">
                    {pairedDevices.map((device) => (
                      <div
                        key={device.id}
                        className={`device-item ${selectedDevice === device.id ? 'selected' : ''}`}
                        onClick={() => setSelectedDevice(device.id)}
                        data-testid="paired-device-item"
                      >
                        <div className="device-info">
                          <strong data-testid="associate-device-id">{device.id}</strong>
                          <span className="trail-association">
                            Currently on: {getTrailName(device.current_trail_id)}
                          </span>
                          {device.battery !== undefined && (
                            <span className="battery">Battery: {device.battery}%</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {selectedDevice && (
              <div className="form-group">
                <label htmlFor="trail-select">Select Trail:</label>
                <select
                  id="trail-select"
                  value={selectedTrail}
                  onChange={(e) => setSelectedTrail(Number(e.target.value))}
                  required
                >
                  <option value={0}>Select a trail</option>
                  {trails.map((trail) => (
                    <option key={trail.id} value={trail.id}>
                      {trail.name} (ID: {trail.id})
                    </option>
                  ))}
                </select>
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </div>
          <div className="modal-footer">
            <Button variant="primary" disabled={loading || !selectedDevice || !selectedTrail} data-testid="associate-device-button">
              {loading ? 'Associating...' : 'Associate Device'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AssociateDeviceModal;