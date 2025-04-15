import React, { useState, useEffect } from "react";
import TrailSelector from "./components/trailselector";
import "./styles/dashboard.css"
import Plot from "react-plotly.js"
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
import { useNavigate } from "react-router-dom";
    
const dashboard = () => {
    const [count, setCount] = useState(0)
    const navigate = useNavigate();
    const handleLogout = () => {
      sessionStorage.clear();
      navigate("/login");
    };

    const { getAll, GetTrailDataBetweenDates, GetAllTrailsBetweenDates } = TrailData();
    const [data, setData] = useState<Array<{ 
        x: Date[]; 
        y: number[]; 
        type: string; 
        mode: string; 
        name: string; 
        marker: { color: string };
    }>>([]);
    const [xDataList, setXDataList] = useState<Date[][]>([]);
    const [yDataList, setYDataList] = useState<number[][]>([]);

    useEffect(() => {   
        if (xDataList.length > 0 && yDataList.length > 0) {
            const newData = xDataList.map((xData, index) => ({
                x: xData,
                y: yDataList[index],
                type: 'scatter',
                mode: 'lines+markers',
                name: `Trail ${trails[index]}`,
                marker: { color: ['red', 'blue', 'green', 'orange', 'goldenrod', 'limegreen', 'papayawhip'][index % 7] },
            }));
            setData(newData);
        }
    }, [xDataList, yDataList]); // React to changes in xDataList and yDataList

    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedDateEnd, setSelectedDateEnd] = useState<Date | null>(new Date());
    const [trails, setTrails] = useState<string[]>([]);
    const [granularity, setGranularity] = useState<string| null>(null);
    const [granularityOptions, setGranularityOptions] = useState<string[]>([]);
    const [graphTitle, setGraphTitle] = useState<string>("Trail Data");

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

            var lines: [Date[], number[]][] = [];
   
            for (const key of events.keys()) {
                let dates: Date[] = events.get(key) ?? [];
                let occurrences = countOccurrencesInRanges(ranges, dates);

                Object.keys(occurrences).sort(); // Ensure chronological order
                const xData: Date[] = Array.from(occurrences.keys()).map(key => new Date(key));
                const yData: number[] = Array.from(occurrences.values());

                lines.push([xData, yData]); 
            }

            if (trails.indexOf("All Trails") > -1) {
                response = await GetAllTrailsBetweenDates(Math.floor(startDate.getTime() / 1000),Math.floor(endDate.getTime() / 1000));
                const responseJson = await response.json;
                let dates: Date[] = [];

                // Process timestamps into daily counts
                Object.values(responseJson as { timestamp: number }[]).forEach((entry) => {
                    dates.push(new Date(entry.timestamp * 1000));
                });
                dates.sort();

                let occurrences = countOccurrencesInRanges(ranges, dates);
                var xData = Array.from(occurrences.keys()).map(key => new Date(key));
                var yData = Array.from(occurrences.values())
                lines.push([xData, yData]);   
            }
            
            
            if (lines.length > 0) {
                setXDataList(lines.map(line => line[0])); // Extract xData from each line
                setYDataList(lines.map(line => line[1])); // Extract yData from each line
            }

            setGraphTitle(formatGraphTitle(startDate, endDate, trails));
        }catch (error) {
            console.error("Error fetching trail data:", error);
        }
    }

    function formatGraphTitle(startDate: Date | null, endDate: Date | null, trails: string[]): string {
        if (!startDate || !endDate) return "Trail Data";
    
        const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
        const startStr = startDate.toLocaleDateString(undefined, options);
        const endStr = endDate.toLocaleDateString(undefined, options);
    
        if (trails.includes("All Trails")) {
            return `All Trails from ${startStr} to ${endStr}`;
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
        if (startDate && selectedDateEnd && trails.length > 0 && granularity) {
            getResponse(startDate, selectedDateEnd, trails, granularity);
        }
    }

    const handleEndDateChange = (endDate: Date | null) => {
        setSelectedDateEnd(endDate);
        if (selectedDate && endDate && trails.length > 0 && granularity) {
            getResponse(selectedDate, endDate, trails, granularity);
        }
    }

    const handleTrailChange = (selectedTrails: string[]) => {
        setTrails(selectedTrails);

        if (selectedTrails.length === 0) {
            setData([]); 
            return;
        }
        if (selectedDate && selectedDateEnd && selectedTrails.length > 0 && granularity) {
          getResponse(selectedDate, selectedDateEnd, selectedTrails, granularity);
        }
      }

    const handleGranularityChange = (granularity: string) => {
        setGranularity(granularity);
        if (selectedDate && selectedDateEnd && trails.length > 0 && granularity) {
            getResponse(selectedDate, selectedDateEnd, trails, granularity);
        }
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
                    data={data}
                    layout={{
                        title: {
                            text: graphTitle,
                            font: { size: 24 },
                            xref: "paper",
                            x: 0.05
                        },
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
                        <TrailSelector onChange={handleTrailChange}/>
                    </div>
                </div>
            </div>
        </body>
    );
}

export default dashboard;