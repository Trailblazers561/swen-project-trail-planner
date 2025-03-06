import React, { useState, useEffect } from "react";
import TrailSelector from "./components/trailselector";
import "./styles/dashboard.css"
import Plot from "react-plotly.js"
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
    
const dashboard = ({newXData,newYData}) => {
    const {GetTrailDataBetweenDates, GetAllTrailsBetweenDates } = TrailData();
    const [xData, setXData] = useState<Date[]>([]); //
    const [yData, setYData] = useState<Number[]>([]); //

    useEffect(() => {
        setXData(newXData);
        setYData(newYData);
    }, [newXData, newYData]); // Updates xData & yData whenever newXDataor newYData changes


    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedDateEnd, setSelectedDateEnd] = useState<Date | null>(new Date());
    const [trail, setTrail] = useState<string>("All Trails");
    const [granularity, setGranularity] = useState<string | null>(null);

    const handleStartDateChange = (startDate: Date | null) => {
        setSelectedDate(startDate);
        if (startDate && selectedDateEnd) {
            getResponse(startDate, selectedDateEnd, trail);
        }
    }

    const handleEndDateChange = (endDate: Date | null) => {
        setSelectedDateEnd(endDate);
        if (selectedDate && endDate) {
            getResponse(selectedDate, endDate, trail);
        }
    }

    const handleTrailChange = (selectedTrail: string) => {
        setTrail(selectedTrail);
        console.log(selectedTrail);
        if (selectedDate && selectedDateEnd) {
            getResponse(selectedDate, selectedDateEnd, selectedTrail);
        }
    }

    const trailMap: Record<string, number> = {
        "All Trails": 0,
        "Mt. Marcy": 1,
        "Wolf Creek Mountain": 2,
        "Mt. Joe": 3,
        "Mt. America": 4
    };

    async function getResponse(startDate: Date | null, endDate: Date | null, trail: string) {
        if (!startDate || !endDate) return; 

        let response;
        try {
            if (trail[0] === "All Trails") {
                response = await GetAllTrailsBetweenDates(Math.floor(startDate.getTime() / 1000),Math.floor(endDate.getTime() / 1000)
                );
            } else {
                const trailId = trailMap[trail];
                if (!trailId) return; // Ensure the trailId is valid
                response = await GetTrailDataBetweenDates(Math.floor(startDate.getTime() / 1000),Math.floor(endDate.getTime() / 1000),trailId
                );
            }
            const responseJson = await response.json;

            let dateCounts: Record<string, number> = {};

            // Process timestamps into daily counts
            (responseJson as { timestamp: number }[]).forEach((entry) => {
                const date = new Date(entry.timestamp * 1000);
                const dateKey = date.toISOString().split("T")[0]; // Format: YYYY-MM-DD

                dateCounts[dateKey] = (dateCounts[dateKey] || 0) + 1;
            });
            const sortedDates = Object.keys(dateCounts).sort(); // Ensure chronological order
            const xData = sortedDates.map(dateStr => new Date(dateStr));
            const yData = sortedDates.map(dateStr => dateCounts[dateStr]);

            setXData(xData);
            setYData(yData);
        }catch (error) {
            console.error("Error fetching trail data:", error);
        }
    }

    const handleGranularityChange = (e: string) => {
        setGranularity(e);
    }

    return(
        <body>
            <div className="dashboard-div">
                <Plot className="graph"
                    config={ {displayModeBar: false} }
                    data={[
                    {
                        x: xData,
                        y: yData,
                        type: 'line',
                        name: 'trail',
                        mode: 'lines+markers',
                        marker: {color: 'red'},
                    },

                    ]}
                    layout={{
                        width: 1000,
                        height: 700, 
                        xaxis: { title: { text: 'Date', font: { size: 18, color: '#7f7f7f' } }, },
                        yaxis: { title: { text: 'Hikers', font: { size: 18, color: '#7f7f7f' } }, },
                        }}
                />
                <div className="filter-container">
                    <div className="filter-group">
                        <label>Start Date:</label>
                        <DatePicker
                            selected={selectedDate}
                            onChange={handleStartDateChange}
                            dateFormat="MM/dd/yyyy"
                            isClearable
                            placeholderText="Select a date"
                            className="date-picker"
                        />
                    </div>
                    <div className="filter-group">
                        <label>End Date:</label>
                        <DatePicker
                            selected={selectedDateEnd}
                            onChange={handleEndDateChange}
                            dateFormat="MM/dd/yyyy"
                            isClearable
                            placeholderText="Select a date"
                            className="date-picker"
                        />
                    </div>
                    <div className="filter-group">
                        <label>Granularity:</label>
                        <select 
                            id="granularity"
                            className="select-box"
                            onChange={(e) => handleGranularityChange(e.target.value)}
                        >
                            <option value="Hourly">Hourly</option>
                            <option value="Daily">Daily</option>
                            <option value="Monthly">Monthly</option>
                            <option value="Yearly">Yearly</option>
                        </select>
                    </div>
                    <div className="filter-group">
                        <label>Trail:</label>
                        <TrailSelector onChange={handleTrailChange}/>
                    </div>
                </div>
            </div>
        </body>
    );
}

export default dashboard;