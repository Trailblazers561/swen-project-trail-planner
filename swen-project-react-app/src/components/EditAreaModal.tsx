import React, { useState, useEffect } from 'react';
import { TrailData } from '../api';
import './Modal.css';
import { Button } from './ui/button';

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { updateTrailMetadata } = TrailData();

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

      // Create a map of trail_id to trail_name for preserving names
      const trailIdToName = new Map<number, string>();
      availableTrails.forEach(trail => {
        if (trail && trail.name) {
          trailIdToName.set(trail.id, trail.name);
        }
      });

      if (isRenaming && oldAreaName) {
        // When renaming, we need to update the area entry itself

        const oldArea = areas.find(a => a.name === oldAreaName);
        if (oldArea) {
          const oldAreaTrailIds = oldArea.trail_ids || [];

          // Step 1: Move ALL trails from old area to new area name first
          // This ensures the old area becomes empty and the new area is created
          const allTrailsToMove = oldAreaTrailIds.map(trailId => {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              return updateTrailMetadata(trailId, trailName, areaNameToUse);
            }
            return Promise.resolve();
          });

          await Promise.all(allTrailsToMove);

          // Step 2: Now handle the selection - remove trails that shouldn't be in the area
          const trailsToRemoveFromNewArea = oldAreaTrailIds.filter(id => !selectedTrailIds.includes(id));
          for (const trailId of trailsToRemoveFromNewArea) {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              // Remove from the new area (set to empty)
              await updateTrailMetadata(trailId, trailName, '');
            }
          }

          // Step 3: Add any new trails that weren't in the old area
          const trailsToAdd = selectedTrailIds.filter(id => !oldAreaTrailIds.includes(id));

          // First remove them from any other areas
          const allOtherAreaTrailIds = new Set<number>();
          areas.forEach(area => {
            if (area.name && area.name !== oldAreaName) {
              area.trail_ids.forEach(id => allOtherAreaTrailIds.add(id));
            }
          });

          for (const trailId of trailsToAdd) {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              if (allOtherAreaTrailIds.has(trailId)) {
                // Remove from current area first
                await updateTrailMetadata(trailId, trailName, '');
              }
              // Then add to new area
              await updateTrailMetadata(trailId, trailName, areaNameToUse);
            }
          }
        }
      } else {
        // Not renaming - normal create or edit without name change
        // Step 1: Remove selected trails from ALL existing areas
        const allAreaTrailIds = new Set<number>();
        areas.forEach(area => {
          if (area.name) {
            area.trail_ids.forEach(id => allAreaTrailIds.add(id));
          }
        });

        // Remove all selected trails from their current areas
        for (const trailId of selectedTrailIds) {
          if (allAreaTrailIds.has(trailId)) {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              await updateTrailMetadata(trailId, trailName, '');
            }
          }
        }

        // Step 2: Add selected trails to the new/updated areas
        const updatePromises = selectedTrailIds.map(trailId => {
          const trailName = trailIdToName.get(trailId);
          if (trailName) {
            return updateTrailMetadata(trailId, trailName, areaNameToUse);
          }
          return Promise.resolve();
        });

        await Promise.all(updatePromises);
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

  // Filter out empty areas
  const availableAreas = areas.filter(a =>
    a &&
    a.name &&
    a.trail_ids &&
    Array.isArray(a.trail_ids) &&
    a.trail_ids.length > 0
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
                      {area.name} ({area.trail_ids.length} trails)
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
                    </div>
                  );
                })}
              </div>
            </div>
            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}
          </div>
          <div className="modal-footer">
            <Button variant="primary" disabled={loading} data-testid="confirm-button">
              {loading ? 'Saving...' : (isCreateMode ? 'Create Area' : 'Update Area')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditAreaModal;