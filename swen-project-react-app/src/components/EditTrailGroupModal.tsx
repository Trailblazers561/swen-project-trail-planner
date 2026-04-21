import React, { useState, useEffect } from 'react';
import { TrailData } from '../api';
import './Modal.css';
import { Button } from './ui/button';

interface Trail {
  id: number;
  name: string;
}

interface TrailGroup {
  name: string;
  trail_ids: number[];
}

interface EditTrailGroupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
  availableTrails: Trail[];
  trailGroups: TrailGroup[];
  isCreateMode?: boolean;
}

const EditTrailGroupModal: React.FC<EditTrailGroupModalProps> = ({
  isOpen,
  onClose,
  onUpdate,
  availableTrails = [],
  trailGroups = [],
  isCreateMode = false
}) => {
  const [selectedGroupName, setSelectedGroupName] = useState<string>('');
  const [newGroupName, setNewGroupName] = useState<string>('');
  const [selectedTrailIds, setSelectedTrailIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { updateTrailMetadata } = TrailData();

  useEffect(() => {
    if (isOpen) {
      setSelectedGroupName('');
      setNewGroupName('');
      setSelectedTrailIds([]);
      setError(null);
      setSuccess(null);
    }
  }, [isOpen, isCreateMode]);

  useEffect(() => {
    if (selectedGroupName && !isCreateMode) {
      const group = trailGroups.find(g => g.name === selectedGroupName);
      if (group) {
        setNewGroupName(group.name);
        setSelectedTrailIds([...group.trail_ids]);
      }
    }
  }, [selectedGroupName, trailGroups, isCreateMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isCreateMode) {
      if (!newGroupName || newGroupName.trim() === '') {
        setError('Group name is required');
        return;
      }
      if (selectedTrailIds.length === 0) {
        setError('Please select at least one trail');
        return;
      }
    } else {
      if (!selectedGroupName) {
        setError('Please select a group to edit');
        return;
      }
      if (!newGroupName || newGroupName.trim() === '') {
        setError('Group name is required');
        return;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const groupNameToUse = newGroupName.trim();
      const oldGroupName = isCreateMode ? undefined : selectedGroupName;
      const isRenaming = oldGroupName && oldGroupName !== groupNameToUse;

      // Create a map of trail_id to trail_name for preserving names
      const trailIdToName = new Map<number, string>();
      availableTrails.forEach(trail => {
        if (trail && trail.name) {
          trailIdToName.set(trail.id, trail.name);
        }
      });

      if (isRenaming && oldGroupName) {
        // When renaming, we need to update the group entry itself

        const oldGroup = trailGroups.find(g => g.name === oldGroupName);
        if (oldGroup) {
          const oldGroupTrailIds = oldGroup.trail_ids || [];

          // Step 1: Move ALL trails from old group to new group name first
          // This ensures the old group becomes empty and the new group is created
          const allTrailsToMove = oldGroupTrailIds.map(trailId => {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              return updateTrailMetadata(trailId, trailName, groupNameToUse);
            }
            return Promise.resolve();
          });

          await Promise.all(allTrailsToMove);

          // Step 2: Now handle the selection - remove trails that shouldn't be in the group
          const trailsToRemoveFromNewGroup = oldGroupTrailIds.filter(id => !selectedTrailIds.includes(id));
          for (const trailId of trailsToRemoveFromNewGroup) {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              // Remove from the new group (set to empty)
              await updateTrailMetadata(trailId, trailName, '');
            }
          }

          // Step 3: Add any new trails that weren't in the old group
          const trailsToAdd = selectedTrailIds.filter(id => !oldGroupTrailIds.includes(id));

          // First remove them from any other groups
          const allOtherGroupTrailIds = new Set<number>();
          trailGroups.forEach(group => {
            if (group.name && group.name !== oldGroupName) {
              group.trail_ids.forEach(id => allOtherGroupTrailIds.add(id));
            }
          });

          for (const trailId of trailsToAdd) {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              if (allOtherGroupTrailIds.has(trailId)) {
                // Remove from current group first
                await updateTrailMetadata(trailId, trailName, '');
              }
              // Then add to new group
              await updateTrailMetadata(trailId, trailName, groupNameToUse);
            }
          }
        }
      } else {
        // Not renaming - normal create or edit without name change
        // Step 1: Remove selected trails from ALL existing groups
        const allGroupTrailIds = new Set<number>();
        trailGroups.forEach(group => {
          if (group.name) {
            group.trail_ids.forEach(id => allGroupTrailIds.add(id));
          }
        });

        // Remove all selected trails from their current groups
        for (const trailId of selectedTrailIds) {
          if (allGroupTrailIds.has(trailId)) {
            const trailName = trailIdToName.get(trailId);
            if (trailName) {
              await updateTrailMetadata(trailId, trailName, '');
            }
          }
        }

        // Step 2: Add selected trails to the new/updated group
        const updatePromises = selectedTrailIds.map(trailId => {
          const trailName = trailIdToName.get(trailId);
          if (trailName) {
            return updateTrailMetadata(trailId, trailName, groupNameToUse);
          }
          return Promise.resolve();
        });

        await Promise.all(updatePromises);
      }

      setSuccess(isCreateMode ? 'Group created successfully!' : 'Group updated successfully!');
      setTimeout(() => {
        onUpdate();
        onClose();
        setSuccess(null);
      }, 1500);
    } catch (err) {
      setError(isCreateMode ? 'An error occurred while creating the group' : 'An error occurred while updating the group');
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

  // Filter out empty groups
  const availableGroups = trailGroups.filter(g =>
    g &&
    g.name &&
    g.trail_ids &&
    Array.isArray(g.trail_ids) &&
    g.trail_ids.length > 0
  );
  const validTrails = availableTrails.filter(t => t && t.name && t.name.trim().length > 0);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="edit-trail-group-modal">
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
        <div className="modal-header bg-[var(--color-navbar)]">
          <div className="font-primary text-white font-semibold">{isCreateMode ? 'Create New Trail Group' : 'Edit Trail Group'}</div>
          <button className="modal-close" onClick={onClose} data-testid="modal-close">×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {!isCreateMode && (
              <div className="form-group">
                <label htmlFor="group-select">Select Group:</label>
                <select
                  id="group-select"
                  value={selectedGroupName}
                  onChange={(e) => setSelectedGroupName(e.target.value)}
                  required
                >
                  <option value="">Select a group</option>
                  {availableGroups.map((group) => (
                    <option key={group.name} value={group.name}>
                      {group.name} ({group.trail_ids.length} trails)
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div className="form-group">
              <label htmlFor="group-name">Group Name: <span style={{ color: 'red' }}>*</span></label>
              <input
                id="group-name"
                type="text"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                required
                placeholder="Enter group name"
                disabled={!isCreateMode && !selectedGroupName}
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
                          cursor: (!isCreateMode && !selectedGroupName) ? 'not-allowed' : 'pointer',
                          margin: 0,
                          userSelect: 'none'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            e.stopPropagation();
                            if (isCreateMode || selectedGroupName) {
                              handleTrailToggle(trail.id);
                            }
                          }}
                          onClick={(e) => e.stopPropagation()}
                          disabled={!isCreateMode && !selectedGroupName}
                          style={{
                            marginRight: '8px',
                            cursor: (!isCreateMode && !selectedGroupName) ? 'not-allowed' : 'pointer',
                            width: '18px',
                            height: '18px',
                            flexShrink: 0,
                            verticalAlign: 'middle'
                          }}
                          data-testid={"checkbox " + trail.name}
                        />
                        <span style={{ fontSize: '0.9em', color: '#666' }}>
                          {isChecked ? 'In group' : 'Not in group'}
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
              {loading ? 'Saving...' : (isCreateMode ? 'Create Group' : 'Update Group')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditTrailGroupModal;