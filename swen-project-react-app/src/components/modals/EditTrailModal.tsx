import React, { useState, useEffect } from 'react';
import { TrailData } from '../../api';
import './Modal.css';
import { DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuTrigger } from '../templates/dropdown-menu';
import { Button } from '../templates/button';

interface Trail {
  id: number;
  name: string;
  notes: string;
  latitude: number;
  longitude: number;
}

interface Area {
  name: string;
  trail_ids: number[];
}

interface EditTrailModalProps {
  isOpen: boolean;
  onClose: () => void;
  trail: Trail | null;
  onUpdate: () => void;
  availableTrails?: Trail[];
  isCreateMode?: boolean;
}

const EditTrailModal: React.FC<EditTrailModalProps> = ({ isOpen, onClose, trail: propTrail, onUpdate, availableTrails = [], isCreateMode = false }) => {
  const [selectedTrailId, setSelectedTrailId] = useState<number>(0);
  const [trailName, setTrailName] = useState('');
  const [notes, setNotes] = useState('');
  const [latitude, setLatitude] = useState(0);
  const [longitude, setLongitude] = useState(0);
  const [selectedArea, setSelectedArea] = useState<string>('');
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const { getAreaMetadata, updateTrailMetadata, createTrail, retireTrail } = TrailData();

  useEffect(() => {
    if (isOpen) {
      loadAreas();
      if (isCreateMode) {
        // Create mode - reset everything
        setSelectedTrailId(0);
        setTrailName('');
        setNotes('');
        setLatitude(0);
        setLongitude(0);
        setSelectedArea('');
      } else if (propTrail) {
        // Edit mode with specific trail
        setSelectedTrailId(propTrail.id);
        setTrailName(propTrail.name);
        setNotes('');
        setLatitude(0);
        setLongitude(0);
      } else {
        // Edit mode - allow selection
        setSelectedTrailId(0);
        setTrailName('');
        setNotes('');
        setLatitude(0);
        setLongitude(0);
      }
    }
  }, [isOpen, propTrail, isCreateMode]);

  useEffect(() => {
    if (selectedTrailId > 0) {
      const selectedTrail = availableTrails.find(t => t.id === selectedTrailId);
      if (selectedTrail) {
        setTrailName(selectedTrail.name);
        setNotes(selectedTrail.notes);
        setLatitude(selectedTrail.latitude);
        setLongitude(selectedTrail.longitude);
        // Find which area this trail belongs to
        const area = areas.find((a: Area) =>
          a.trail_ids && a.trail_ids.includes(selectedTrailId)
        );
        if (area) {
          setSelectedArea(area.name);
        } else {
          setSelectedArea('');
        }
      }
    }
  }, [selectedTrailId, availableTrails, areas]);

  const loadAreas = async () => {
    try {
      const response = await getAreaMetadata();
      if (response.success) {
        const areas = await response.json;
        setAreas(areas);

        // Find which area trail belongs to
        const area = areas.find((a: Area) =>
          a.trail_ids && a.trail_ids.includes(propTrail?.id || 0)
        );
        if (area) {
          setSelectedArea(area.name);
        }
      }
    } catch (err) {
      console.error('Error loading areas:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!trailName || trailName.trim() === '') {
      setError('Trail name is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (isCreateMode) {
        // Create new trail
        const response = await createTrail(
          trailName.trim(),
          selectedArea || undefined,
          notes?.trim() || undefined,
          latitude,
          longitude,
        );

        if (response.success) {
          setSuccess('Trail created successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
            setSelectedTrailId(0);
            setTrailName('');
            setNotes('');
            setLatitude(0);
            setLongitude(0);
            setSelectedArea('');
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to create trail');
        }
      } else {
        // Update existing trail
        if (!selectedTrailId) {
          setError('Please select a trail');
          return;
        }

        const response = await updateTrailMetadata(
          selectedTrailId,
          trailName.trim() || undefined,
          selectedArea || undefined,
          notes?.trim() || undefined,
          latitude,
          longitude,
        );

        if (response.success) {
          setSuccess('Trail updated successfully!');
          setTimeout(() => {
            onUpdate();
            onClose();
            setSuccess(null);
          }, 1500);
        } else {
          const errorData = await response.json;
          setError(errorData.error || 'Failed to update trail');
        }
      }
    } catch (err) {
      setError(isCreateMode ? 'An error occurred while creating the trail' : 'An error occurred while updating the trail');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedTrailId) {
      setError('Please select a trail');
      return;
    }

    setDeleting(true);
    setError(null);

    try {
      const response = await retireTrail(selectedTrailId);

      if (response.success) {
        setSuccess('Trail retired successfully!');
        setTimeout(() => {
          onUpdate();
          onClose();
          setShowDeleteConfirm(false);
          setSuccess(null);
        }, 1500);
      } else {
        const errorData = await response.json;
        setError(errorData.error || 'Failed to retire trail');
      }
    } catch (err) {
      setError('An error occurred while retiring the trail');
      console.error(err);
    } finally {
      setDeleting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="edit-trail-modal">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header bg-[var(--color-navbar)]">
          <div className="font-primary text-white font-semibold"> {isCreateMode ? 'Create New Trail' : 'Edit Trail Information'} </div>
          <button className="modal-close" onClick={onClose} data-testid="modal-close">×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {!isCreateMode && (
              <div className="form-group">
                <label htmlFor="trail-select">Select Trail:</label>
                <select
                  id="trail-select"
                  value={selectedTrailId}
                  onChange={(e) => setSelectedTrailId(Number(e.target.value))}
                  required
                >
                  <option value={0}>Select a trail</option>
                  {availableTrails.map((trail) => (
                    <option key={trail.id} value={trail.id}>
                      {trail.name} (ID: {trail.id})
                    </option>
                  ))}
                </select>
              </div>
            )}
            {(isCreateMode || selectedTrailId > 0) && (
              <>
                <div className="form-group">
                  <label htmlFor="trail-name">Trail Name: {isCreateMode && <span style={{ color: 'red' }}>*</span>}</label>
                  <input
                    id="trail-name"
                    type="text"
                    value={trailName}
                    onChange={(e) => setTrailName(e.target.value)}
                    required
                    placeholder="Enter trail name"
                    autoComplete="off"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="notes">Notes (optional): {isCreateMode}</label>
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
                <div className="form-group" style={{ display: "flex", gap: "16px" }}>
                  <div  style={{ flex: 1 }}>
                    <label htmlFor="latitude">Latitude{isCreateMode && <span style={{ color: 'red' }}>*</span>}</label>
                    <input
                      id="latitude"
                      type="number"
                      step="any"
                      value={latitude}
                      onChange={(e) => setLatitude(Number(e.target.value))}
                      min={-90}
                      max={90}
                      required
                      placeholder="Enter latitude"
                      autoComplete="off"
                    />
                    </div>
                    <div  style={{ flex: 1 }}>
                    <label htmlFor="longitude">Longitude{isCreateMode && <span style={{ color: 'red' }}>*</span>}</label>
                    <input
                      id="longitude"
                      type="number"
                      step="any"
                      value={longitude}
                      onChange={(e) => setLongitude(Number(e.target.value))}
                      min={-180}
                      max={180}
                      required
                      placeholder="Enter longitude"
                      autoComplete="off"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="area">Area (optional):</label>

                  {/* TODO: Implement new dropdown menu for areas once data model is updated */}
                  {/* <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="primary">Trail Options</Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                            <DropdownMenuGroup>
                            <DropdownMenuItem>Add Trail</DropdownMenuItem>
                            <DropdownMenuItem>Edit Trail Info</DropdownMenuItem>
                            </DropdownMenuGroup>
                        </DropdownMenuContent>
                        </DropdownMenu> */}
                  <select
                    id="area"
                    value={selectedArea}
                    onChange={(e) => setSelectedArea(e.target.value)}
                  >
                    <option value="">Select an area (optional)</option>
                    {areas.map((area) => (
                      <option key={area.name} value={area.name}>
                        {area.name}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </div>
          <div className="modal-footer">
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
              <div>
                {!isCreateMode && selectedTrailId > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowDeleteConfirm(true)}
                    disabled={loading || deleting}
                    className="delete-button"
                    data-testid="delete-button"
                  >
                    Retire Trail
                  </button>
                )}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <Button variant="primary" disabled={loading || deleting} data-testid="confirm-button">
                  {loading ? (isCreateMode ? 'Creating...' : 'Updating...') : (isCreateMode ? 'Create Trail' : 'Update Trail')}
                </Button>
              </div>
            </div>
          </div>
        </form>

        {showDeleteConfirm && (
          <div className="modal-overlay" style={{ zIndex: 1001 }} onClick={() => setShowDeleteConfirm(false)}>
            <div className="modal-content" style={{ maxWidth: '400px' }} onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Confirm Retire</h2>
                <button className="modal-close" onClick={() => setShowDeleteConfirm(false)}>×</button>
              </div>
              <div className="modal-body">
                <p style={{ marginBottom: '15px', color: '#333' }}>
                  <strong style={{ color: '#dc3545' }}>Warning:</strong> This action cannot be undone.
                </p>
                <p style={{ marginBottom: '15px', color: '#333' }}>
                  Retiring this trail will permanently remove:
                </p>
                <ul style={{ marginLeft: '20px', marginBottom: '15px', color: '#333' }}>
                  <li>The trail from regular trail metadata retrieval</li>
                  <li>The ability to upload logs to the trail</li>
                  <li>The trail from all areas</li>
                  <li>Devices associated with this trail will be unassociated</li>
                </ul>
                <p style={{ fontWeight: 'bold', color: '#dc3545', fontSize: '16px' }}>
                  Are you sure you want to retire "{trailName}"?
                </p>
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
              </div>
              <div className="modal-footer">
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
                  {deleting ? 'Deleting...' : 'Yes, Retire Trail'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EditTrailModal;