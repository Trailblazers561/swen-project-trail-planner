import React, { useState, useEffect, useMemo } from "react";
import Select from "react-select";
import { MultiSelectOption } from "./ui/multi-select";

interface Trail {
    id: number;
    name: string;
}

interface TrailGroup {
    name: string;
    trail_ids: number[];
}

interface TrailSelectorProps {
    onChange: (trails: string[]) => void;
    clearTrails: () => void;
    clearGraph: () => void;
    clearName: () => void;
    trailMetadata?: Trail[];
    trailGroups?: TrailGroup[];
}

const TrailSelector = ({
    onChange,
    clearGraph,
    clearName,
    clearTrails,
    trailMetadata = [],
    trailGroups = []
}: TrailSelectorProps) => {
    const [selectedWilderness, setSelectedWilderness] = useState<string>("");
    const [selectedTrails, setSelectedTrails] = useState<Array<{ value: string; label: string }>>([]);

    // Build wilderness options from trail groups (exclude empty groups)
    const wildernessOptions = useMemo(() => {
        const options: MultiSelectOption[] = [];
        trailGroups.forEach(group => {
            if (group.name &&
                group.trail_ids &&
                Array.isArray(group.trail_ids) &&
                group.trail_ids.length > 0) {
                options.push({ value: group.name, label: group.name });
            }
        });
        return options;
    }, [trailGroups]);

    // Build trail data map -  groups contain their specific trails
    const trailData = useMemo(() => {
        const data: Record<string, string[]> = {};

        // Filter out any trails with invalid names
        const validTrails = trailMetadata.filter(t => t && t.name && t.name.trim().length > 0);

        // Add trails for each group (only trails that exist in metadata)
        trailGroups.forEach(group => {
            if (group.name) {
                const groupTrails = (group.trail_ids || [])
                    .map(id => validTrails.find(t => t.id === id))
                    .filter((t): t is Trail => t !== undefined)
                    .map(t => t.name);
                data[group.name] = groupTrails;
            }
        });

        return data;
    }, [trailMetadata, trailGroups]);

    // Get filtered trails for the selected wilderness
    const filteredTrails = useMemo(() => {
        const trails = trailData[selectedWilderness] || [];
        return trails
            .filter(trail => trail && trail.trim().length > 0)
            .sort()
            .map(trail => ({
                value: trail,
                label: trail
            }));
    }, [trailData, selectedWilderness]);

    // Update selected trails when metadata changes - preserve selections if trails still exist
    useEffect(() => {
        if (trailMetadata.length > 0 && selectedTrails.length > 0) {
            const validTrailNames = new Set(
                trailMetadata
                    .filter(t => t && t.name && t.name.trim().length > 0)
                    .map(t => t.name)
            );

            const updatedTrails = selectedTrails
                .map(selected => {
                    // Keep trail if it still exists (even if name changed, we'll update it)
                    if (validTrailNames.has(selected.value)) {
                        return { value: selected.value, label: selected.value };
                    }
                    return null;
                })
                .filter((t): t is { value: string; label: string } => t !== null);

            // Only update if trails were actually removed
            if (updatedTrails.length < selectedTrails.length) {
                setSelectedTrails(updatedTrails);
                onChange(updatedTrails.map(t => t.value));
                if (updatedTrails.length === 0) {
                    clearTrails();
                    clearGraph();
                    clearName();
                }
            }
        }
    }, [trailMetadata]);

    const selectKey = useMemo(() => {
        const trailCount = trailMetadata.filter(t => t && t.name).length;
        const groupCount = trailGroups.length;
        const trailIds = trailMetadata
            .filter(t => t && t.id)
            .map(t => t.id)
            .sort()
            .join(',');
        return `trail-select-${trailCount}-${groupCount}-${trailIds}-${selectedWilderness}`;
    }, [trailMetadata, trailGroups, selectedWilderness]);

    const handleWildernessChange = (selectedOption: { value: string; label: string } | null) => {
        if (!selectedOption) return;

        const newWilderness = selectedOption.value;
        setSelectedWilderness(newWilderness);

        // Auto-select appropriate trails based on wilderness
        let autoSelectedTrails: Array<{ value: string; label: string }> = [];

        // Select all trails in the group
        const trailsForWilderness = trailData[newWilderness] || [];
        autoSelectedTrails = trailsForWilderness.map(trail => ({
            value: trail,
            label: trail,
        }));

        setSelectedTrails(autoSelectedTrails);
        onChange(autoSelectedTrails.map(option => option.value));
    };

    const handleTrailChange = (selectedOptions: readonly { value: string; label: string }[]) => {
        const options = selectedOptions as Array<{ value: string; label: string }>;
        setSelectedTrails(options);
        onChange(options.map(option => option.value));
    };

    return (
        <div className="trail-filter-container" style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <Select
                key={selectKey}
                className="trail-selector"
                options={filteredTrails}
                isMulti
                isSearchable
                closeMenuOnSelect={false}
                value={selectedTrails}
                onChange={handleTrailChange}
                placeholder="Select Trails..."
                styles={{
                    control: (base) => ({
                        ...base,
                        minWidth: "200px",
                        borderRadius: "5px",
                        backgroundColor: "#fff",
                        border: "2px solid #007bff",
                        boxShadow: "none",
                    }),
                    multiValue: (base) => ({
                        ...base,
                        backgroundColor: "#007bff",
                        color: "white",
                        borderRadius: "5px",
                        padding: "2px 5px",
                    }),
                    multiValueLabel: (base) => ({
                        ...base,
                        color: "white",
                        fontWeight: "bold",
                    }),
                    multiValueRemove: (base) => ({
                        ...base,
                        color: "white",
                        ":hover": {
                            backgroundColor: "#0056b3",
                            color: "white",
                        },
                    }),
                    menu: (base) => ({
                        ...base,
                        backgroundColor: "#fff",
                        border: "1px solid #ccc",
                    }),
                    option: (base, state) => ({
                        ...base,
                        backgroundColor: state.isSelected ? "#007bff" : "#fff",
                        color: state.isSelected ? "white" : "#333",
                        ":hover": {
                            backgroundColor: "#007bff",
                            color: "white",
                        },
                    }),
                }}
            />
            <Select
                className="wilderness-selector"
                options={wildernessOptions}
                value={wildernessOptions.find(option => option.value === selectedWilderness)}
                onChange={handleWildernessChange}
                placeholder="Select Wilderness Area..."
                styles={{
                    control: (base) => ({
                        ...base,
                        minWidth: "200px",
                        borderRadius: "5px",
                        backgroundColor: "#fff",
                        border: "2px solid #007bff",
                        boxShadow: "none",
                    }),
                    menu: (base) => ({
                        ...base,
                        backgroundColor: "#fff",
                        border: "1px solid #ccc",
                    }),
                    option: (base, state) => ({
                        ...base,
                        backgroundColor: state.isSelected ? "#007bff" : "#fff",
                        color: state.isSelected ? "white" : "#333",
                        ":hover": {
                            backgroundColor: "#007bff",
                            color: "white",
                        },
                    }),
                }}
            />
        </div>
    );
};

export default TrailSelector;