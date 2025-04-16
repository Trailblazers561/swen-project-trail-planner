import React, { useState, useEffect } from "react";
import TrailSelector from "./components/trailselector";
import "./styles/dashboard.css"
import Plot from "react-plotly.js"
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
import { useNavigate } from "react-router-dom";
    
const dashboard = () => {
    const navigate = useNavigate();
    const handleLogout = () => {
      sessionStorage.clear();
      navigate("/login");
    };

    const { GetTrailDataBetweenDates, GetAllTrailsBetweenDates } = TrailData();


    const [graphLines, setGraphLines] = useState<Array<{
        name: string;
        x: Date[];
        y: number[];
      }>>([]);

    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedDateEnd, setSelectedDateEnd] = useState<Date | null>(new Date());
    const [trails, setTrails] = useState<string[]>([]);
    const [granularity, setGranularity] = useState<string| null>(null);
    const [granularityOptions, setGranularityOptions] = useState<string[]>([]);
    const [graphTitle, setGraphTitle] = useState<string>("No Trails Selected");

    function getDateDifference(startDate: Date, endDate: Date): number {
        const diffTime = Math.abs(endDate.getTime() - startDate.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24)); // Convert milliseconds to days
    }

    function updateGranularityOptions(startDate: Date | null, endDate: Date | null) {
        if (!startDate || !endDate) return;

        const daysDiff = getDateDifference(startDate, endDate);

        let options: string[] = [];
        if (daysDiff >= 1825) {
            options = ['Yearly', 'Monthly'];
        } else if (daysDiff >= 730) {
            options = ['Yearly', 'Monthly','Weekly','Daily'];
        } else if (daysDiff >= 60) {
            options = ['Monthly', 'Weekly', 'Daily'];
        } else if (daysDiff >= 30) {
            options = ['Weekly', 'Daily'];
        } else if (daysDiff >= 7) {
            options = ['Daily'];
        } else if (daysDiff <= 3) {
            options = ['Daily', 'Hourly'];
        } else {
            options = ['Daily'];
        }

        // Update the granularity options based on the range
        setGranularityOptions(options);
        // Set the granularity to the first option by default
        setGranularity(options[0]);
    }

    useEffect(() => {
        updateGranularityOptions(selectedDate, selectedDateEnd);
    }, [selectedDate, selectedDateEnd]);

    useEffect(() => {

        if (selectedDate && selectedDateEnd && trails.length > 0 && granularity) {
            getResponse(selectedDate, selectedDateEnd, trails, granularity);
        }
    }, [selectedDate, selectedDateEnd, trails, granularity]);
    

    function getDateRanges(startDate: Date, endDate: Date, granularity: string = 'Daily'): { start: Date, end: Date }[] {
        let ranges: { start: Date, end: Date }[] = [];
        let current: Date = startDate;
        let end: Date = endDate;
        
        while (current < end) {
            let next: Date = new Date(current);
            if (granularity === 'Hourly') {
                next.setHours(next.getHours() + 1);
            } else if (granularity === 'Daily') {
                next.setDate(next.getDate() + 1);
            } else if (granularity === 'Weekly') {
                next.setDate(next.getDate() + 7);
            } else if (granularity === 'Monthly') {
                next.setMonth(next.getMonth() + 1);
            } else if (granularity === 'Yearly') {
                next.setFullYear(next.getFullYear() + 1);
            }
        
            if (next > endDate) break;

            ranges.push({ start: new Date(current), end: new Date(next) });
            current = next;
        }
        if (current < endDate) {
            ranges.push({ start: new Date(current), end: endDate });
        }
    
        return ranges;
    }

    function countOccurrencesInRanges(ranges: { start: Date, end: Date }[], events: Date[]): Map<Date, number> {
        let occurrences = new Map<Date, number>();
        
        for (let range of ranges) {
            let count = events.filter(date => date >= range.start && date <= range.end).length;
            occurrences.set(range.start, count);
        }
        return occurrences;
    }

    async function getResponse(startDate: Date | null, endDate: Date | null, trails: string[], granularity: string = 'Daily' ) {
        if (!startDate || !endDate || !granularity || trails.length === 0) return;

        var response;
        try {
            let trailIds: number[] = [];
            for(var i = 0; i < trails.length; i++) {
                trailIds[i] = trailMap[trails[i]];
            }       
            response = await GetTrailDataBetweenDates(Math.floor(startDate.getTime() / 1000),Math.floor(endDate.getTime() / 1000),trailIds
            );
            
            const responseJson = await response.json;
           
            let ranges = getDateRanges(startDate, endDate, granularity)
            let events: Map<number, Date[]> = new Map<number, Date[]>();

            // look through response and create a map of trail id to an array of dates
            (responseJson as { id: number; timestamp: number }[]).forEach((entry) => {
                if (!events.has(entry.id)) {
                    events.set(entry.id, []); // Initialize an empty array for the ID
                }
                events.get(entry.id)!.push(new Date(entry.timestamp * 1000)); // Add new date
            });

            var lines: { name: string; x: Date[]; y: number[] }[] = [];

            if (trails.includes("All Trails")) {
                const response = await GetAllTrailsBetweenDates(
                  Math.floor(startDate.getTime() / 1000),
                  Math.floor(endDate.getTime() / 1000)
                );
                const responseJson = await response.json;
                const dates = (responseJson as { timestamp: number }[]).map(e => new Date(e.timestamp * 1000));
                const occurrences = countOccurrencesInRanges(ranges, dates);
                lines.push({
                    name: "All Trails",
                    x: Array.from(occurrences.keys()),
                    y: Array.from(occurrences.values())
                });
            }

            for (let i = 0; i < trails.length; i++) {
                const trailName = trails[i];
                const trailId = trailMap[trailName];
                const dates: Date[] = events.get(trailId) ?? [];
                if (dates.length === 0) continue;
                const occurrences = countOccurrencesInRanges(ranges, dates);
            
                const xData = Array.from(occurrences.keys());
                const yData = Array.from(occurrences.values());
            
                lines.push({ name: trailName, x: xData, y: yData });
            }
            setGraphLines(lines);

            setGraphTitle(formatGraphTitle(startDate, endDate, trails));
        }catch (error) {
            console.error("Error fetching trail data:", error);
        }
    }

    function formatGraphTitle(startDate: Date | null, endDate: Date | null, trails: string[]): string {
        if (!startDate || !endDate || trails.length === 0) return "No trails selected";
    
        const startStr = startDate.toLocaleDateString();
        const endStr = endDate.toLocaleDateString();
        const includesAll = trails.includes("All Trails");

        if (includesAll && trails.length === 0) {
            return `All Trails from ${startStr} to ${endStr}`;
        } else if (includesAll && trails.length > 1) {
            return `Trails from ${startStr} to ${endStr}`;
        } else if (trails.length === 1) {
            return `${trails[0]} from ${startStr} to ${endStr}`;
        } else if (trails.length === 2) {
            return `${trails[0]} & ${trails[1]} from ${startStr} to ${endStr}`;
        } else {
            return `Trails from ${startStr} to ${endStr}`;
        }
    }
    

    const handleStartDateChange = (startDate: Date | null) => {
        setSelectedDate(startDate);
    }

    const handleEndDateChange = (endDate: Date | null) => {
        setSelectedDateEnd(endDate);
    }

    const handleTrailChange = (selectedTrails: string[]) => {
        setTrails(selectedTrails);

        if (selectedTrails.length === 0) {
            setGraphLines([]); 
            setGraphTitle("No Trails Selected");
            return;
        }
      }

    const handleGranularityChange = (granularity: string) => {
        setGranularity(granularity);
    }

    const trailMap: Record<string, number> = {
        "All Trails": 0,
        "Mt. Marcy": 1,
        "Wolf Creek Mountain": 2,
        "Mt. Joe": 3,
        "Mt. America": 4
    };

    return(
        <body>
            <div className="dashboard-div">
                <div style={{ display: "flex", padding: "10px" }}>
                    <button className="logout-button" type="button" onClick={handleLogout} style={{ marginLeft: "auto" }}>
                    Logout
                    </button>
                </div>
                <Plot className="graph"
                    config={ {displayModeBar: false} }
                    data={graphLines.map((line, index) => ({
                        x: line.x,
                        y: line.y,
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: line.name,
                        marker: {
                            color: ['red', 'blue', 'green', 'orange', 'goldenrod', 'limegreen', 'papayawhip'][index % 7]
                        }
                    }))}
                    layout={{
                        title: {
                            text: graphTitle,
                            font: { size: 24 },
                            xref: "paper",
                            x: 0.05
                        },
                        width: 1000,
                        height: 700, 
                        xaxis: { title: { text: 'Date', font: { size: 18, color: '#7f7f7f' } },autorange: true, rangemode: 'tozero' },
                        yaxis: { title: { text: 'Hikers', font: { size: 18, color: '#7f7f7f' } },range: [0, null],autorange: true, rangemode: 'tozero',},
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
                            className="date-picker-start-date"
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
                            className="date-picker-end-date"
                        />
                    </div>
                    <div className="filter-group">
                        <label>Granularity:</label>
                        <select 
                            id="granularity"
                            className="select-box"
                            value={granularity ?? ""}
                            onChange={(e) => handleGranularityChange(e.target.value)}
                        >
                            {granularityOptions.map(option => (
                                <option key={option} value={option}>{option}</option>
                            ))}
                        </select>
                    </div>
                    <div className="filter-group">
                        <label>Trail:</label>
                        <TrailSelector onChange={handleTrailChange}
                        clearTrails={() => setTrails([])}
                        clearGraph={() => setGraphLines([])}
                        clearName={() => setGraphTitle("No Trails Selected")}    
                        />
                    </div>
                </div>
            </div>
        </body>
    );
}

export default dashboard;