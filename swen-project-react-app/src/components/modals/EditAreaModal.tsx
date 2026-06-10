import React, { useState, useEffect } from 'react';
import { TrailData } from '../../api';
import './Modal.css';
import { Button } from '../templates/button';

interface Trail {
  id: number;
  name: string;
}

interface Area {
  name: string;
  trail_ids: number[];
}

interface EditAreaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
  availableTrails: Trail[];
  areas: Area[];
  isCreateMode?: boolean;
}

const EditAreaModal: React.FC<EditAreaModalProps> = ({
  isOpen,
  onClose,
  onUpdate,
  availableTrails = [],
  areas = [],
  isCreateMode = false
}) => {
  const [selectedAreaName, setSelectedAreaName] = useState<string>('');
  const [newAreaName, setNewAreaName] = useState<string>('');
  const [selectedTrailIds, setSelectedTrailIds] = useState<number[]>([]);
  const [deleting, setDeleting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const { createArea, updateArea, deleteArea  } = TrailData();
  const trailIdToArea: Record<number, string> = {};

  areas.forEach(area => {
    area.trail_ids.forEach(id => {
      trailIdToArea[id] = area.name;
    });
  });

  useEffect(() => {
    if (isOpen) {
      setSelectedAreaName('');
      setNewAreaName('');
      setSelectedTrailIds([]);
      setError(null);
      setSuccess(null);
    }
  }, [isOpen, isCreateMode]);

  useEffect(() => {
    if (selectedAreaName && !isCreateMode) {
      const area = areas.find(a => a.name === selectedAreaName);
      if (area) {
        setNewAreaName(area.name);
        setSelectedTrailIds([...area.trail_ids]);
      }
    }
  }, [selectedAreaName, areas, isCreateMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isCreateMode) {
      if (!newAreaName || newAreaName.trim() === '') {
        setError('Area name is required');
        return;
      }
      if (selectedTrailIds.length === 0) {
        setError('Please select at least one trail');
        return;
      }
    } else {
      if (!selectedAreaName) {
        setError('Please select an area to edit');
        return;
      }
      if (!newAreaName || newAreaName.trim() === '') {
        setError('Area name is required');
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const areaNameToUse = newAreaName.trim();
      const oldAreaName = isCreateMode ? undefined : selectedAreaName;
      const isRenaming = oldAreaName && oldAreaName !== areaNameToUse;

      if (isCreateMode) {
        createArea(areaNameToUse, selectedTrailIds);
      } else {
        if (isRenaming && oldAreaName) {
          updateArea(oldAreaName, areaNameToUse, selectedTrailIds);
        }
        else {
          updateArea(areaNameToUse, undefined, selectedTrailIds);
        }
      }

      setSuccess(isCreateMode ? 'Area created successfully!' : 'Area updated successfully!');
      setTimeout(() => {
        onUpdate();
        onClose();
        setSuccess(null);
      }, 1500);
    } catch (err) {
      setError(isCreateMode ? 'An error occurred while creating the area' : 'An error occurred while updating the area');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrailToggle = (trailId: number) => {
    setSelectedTrailIds(prev =>
      prev.includes(trailId)
        ? prev.filter(id => id !== trailId)
        : [...prev, trailId]
    );
  };

  const handleDelete = async () => {
    if (!selectedAreaName) {
      setError('Please select an area');
      return;
    }

    setDeleting(true);
    setError(null);

    try {
      const response = await deleteArea(selectedAreaName);

      if (response.success) {
        setSuccess('Area deleted successfully!');
        setTimeout(() => {
          onUpdate();
          onClose();
          setShowDeleteConfirm(false);
          setSuccess(null);
        }, 1500);
      } else {
        const errorData = await response.json;
        setError(errorData.error || 'Failed to delete area');
      }
    } catch (err) {
      setError('An error occurred while deleting the area');
      console.error(err);
    } finally {
      setDeleting(false);
    }
  };

  // Filter out invalid areas
  const availableAreas = areas.filter(a =>
    a &&
    a.name
  );
  const validTrails = availableTrails.filter(t => t && t.name && t.name.trim().length > 0);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="edit-area-modal">
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
        <div className="modal-header bg-[var(--color-navbar)]">
          <div className="font-primary text-white font-semibold">{isCreateMode ? 'Create New Area' : 'Edit Area'}</div>
          <button className="modal-close" onClick={onClose} data-testid="modal-close">×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {!isCreateMode && (
              <div className="form-group">
                <label htmlFor="area-select">Select Area:</label>
                <select
                  id="area-select"
                  value={selectedAreaName}
                  onChange={(e) => setSelectedAreaName(e.target.value)}
                  required
                >
                  <option value="">Select an area</option>
                  {availableAreas.map((area) => (
                    <option key={area.name} value={area.name}>
                      {area.name} ({area.trail_ids.length} {area.trail_ids.length === 1 ? "trail" : "trails"})
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div className="form-group">
              <label htmlFor="area-name">Area Name: <span style={{ color: 'red' }}>*</span></label>
              <input
                id="area-name"
                type="text"
                value={newAreaName}
                onChange={(e) => setNewAreaName(e.target.value)}
                required
                placeholder="Enter area name"
                disabled={!isCreateMode && !selectedAreaName}
                autoComplete="off"
              />
            </div>
            <div className="form-group">
              <label>Select Trails: <span style={{ color: 'red' }}>*</span></label>
              <div style={{
                maxHeight: '300px',
                overflowY: 'auto',
                border: '1px solid #ccc',
                borderRadius: '4px',
                padding: '0'
              }}>
                {validTrails.map((trail, index) => {
                  const isChecked = selectedTrailIds.includes(trail.id);
                  const isEven = index % 2 === 0;
                  return (
                    <div
                      key={trail.id}
                      style={{
                        padding: '12px 10px',
                        borderBottom: index < validTrails.length - 1 ? '1px solid #e0e0e0' : 'none',
                        backgroundColor: isEven ? '#f9f9f9' : '#ffffff',
                      }}
                    >
                      <div style={{
                        fontWeight: '500',
                        marginBottom: '8px',
                        color: '#333'
                      }}>
                        {trail.name}
                      </div>
                      <label
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          cursor: (!isCreateMode && !selectedAreaName) ? 'not-allowed' : 'pointer',
                          margin: 0,
                          userSelect: 'none'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            e.stopPropagation();
                            if (isCreateMode || selectedAreaName) {
                              handleTrailToggle(trail.id);
                            }
                          }}
                          onClick={(e) => e.stopPropagation()}
                          disabled={!isCreateMode && !selectedAreaName}
                          style={{
                            marginRight: '8px',
                            cursor: (!isCreateMode && !selectedAreaName) ? 'not-allowed' : 'pointer',
                            width: '18px',
                            height: '18px',
                            flexShrink: 0,
                            verticalAlign: 'middle'
                          }}
                          data-testid={"checkbox " + trail.name}
                        />
                        <span style={{ fontSize: '0.9em', color: '#666' }}>
                          {isChecked ? 'In area' : 'Not in area'}
                        </span>
                      </label>
                        <span style={{ fontSize: '0.9em', color: '#444'}}>
                            Currently in: {trailIdToArea[trail.id] ?? "No Area"}
                          </span>
                    </div>
                  );
                })}
              </div>
            </div>
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </div>
          <div className="modal-footer">
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
              <div>
                {!isCreateMode && selectedAreaName !== "" && (
                  <button
                    type="button"
                    onClick={() => setShowDeleteConfirm(true)}
                    disabled={loading || deleting}
                    className="delete-button font-medium h-9 flex items-center"
                    data-testid="delete-button"
                  >
                    Delete Area
                  </button>
                )}
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <Button variant="primary" disabled={loading} data-testid="confirm-button">
                  {loading ? 'Saving...' : (isCreateMode ? 'Create Area' : 'Update Area')}
                </Button>
              </div>
            </div>
          </div>
        </form>
        {showDeleteConfirm && (
          <div className="modal-overlay" style={{ zIndex: 1001 }} onClick={() => setShowDeleteConfirm(false)}>
            <div className="modal-content" style={{ maxWidth: '400px' }} onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Confirm Delete</h2>
                <button className="modal-close" onClick={() => setShowDeleteConfirm(false)}>×</button>
              </div>
              <div className="modal-body">
                <p style={{ marginBottom: '15px', color: '#333' }}>
                  <strong style={{ color: '#dc3545' }}>Warning:</strong> This action cannot be undone.
                </p>
                <p style={{ marginBottom: '15px', color: '#333' }}>
                  Deleting this area will permanently remove:
                </p>
                <ul style={{ marginLeft: '20px', marginBottom: '15px', color: '#333' }}>
                  <li>The area from the database</li>
                </ul>
                <p style={{ fontWeight: 'bold', color: '#dc3545', fontSize: '16px' }}>
                  Are you sure you want to delete "{selectedAreaName}"?
                </p>
                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
              </div>
              <div className="flex justify-between modal-footer">
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
                  {deleting ? 'Deleting...' : 'Yes, Delete Area'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EditAreaModal;