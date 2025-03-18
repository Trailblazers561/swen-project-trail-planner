import Select from "react-select";
import { useState } from "react";
import PropTypes from 'prop-types';

const trailOptions = [
    { value: "All Trails", label: "All Trails" },
    { value: "Mt. Marcy", label: "Mt. Marcy" },
    { value: "Wolf Creek Mountain", label: "Wolf Creek Mountain" },
    { value: "Mt. Joe", label: "Mt. Joe" },
    { value: "Mt. America", label: "Mt. America" },
];

const TrailSelector = ({ onChange }) => {
    const [selectedTrails, setSelectedTrails] = useState([]);

    const handleChange = (selectedOptions) => {
        setSelectedTrails(selectedOptions);
        onChange(selectedOptions.map(option => option.value)); // Pass selected values to parent
    };

    return (
        <Select
            className="trail-selector"
            options={trailOptions}
            isMulti
            isSearchable
            closeMenuOnSelect={false}
            value={selectedTrails}
            onChange={handleChange}
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
    );
};
TrailSelector.propTypes = {
    onChange: PropTypes.func.isRequired,
};

export default TrailSelector;