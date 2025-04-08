import Select from "react-select";
import { useState } from "react";
import PropTypes from 'prop-types';

const wildernessOptions = [
    { value: "All Areas", label: "All Areas" },
    { value: "Five Ponds", label: "Five Ponds" },
    { value: "High Peaks", label: "High Peaks" },
    { value: "Giant Mountain", label: "Giant Mountain" },
];

const trailData = {
    "All Areas": ["All Trails", "Mt. Marcy", "Wolf Creek Mountain", "Mt. Joe", "Mt. America", "Blueberry Trail", "Sunset Peak","Cedar Loop","Eagle Ridge", "Bear Claw Path"],
    "Five Ponds": ["All Trails", "Blueberry Trail", "Sunset Peak", "Cedar Loop"],
    "High Peaks": ["All Trails", "Mt. Marcy", "Wolf Creek Mountain", "Eagle Ridge", "Bear Claw Path"],
    "Giant Mountain": ["All Trails", "Mt. Joe", "Mt. America", "Giant Summit", "Falcon Crest"],
};

const TrailSelector = ({ onChange }) => {
    const [selectedWilderness, setSelectedWilderness] = useState("All Areas");
    const [selectedTrails, setSelectedTrails] = useState([]);

    const handleWildernessChange = (selectedOption) => {
        setSelectedWilderness(selectedOption.value);
        setSelectedTrails([]); // Reset selected trails when wilderness changes
        onChange(["All Trails"]); // Reset trails selection to All Trails
    };

    const handleTrailChange = (selectedOptions) => {
        setSelectedTrails(selectedOptions);
        onChange(selectedOptions.map(option => option.value));
    };

    const filteredTrails = trailData[selectedWilderness].map(trail => ({ value: trail, label: trail }));

    return (
        <div className="trail-filter-container" style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <Select
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
        </div>
    );
};

TrailSelector.propTypes = {
    onChange: PropTypes.func.isRequired,
};

export default TrailSelector;



