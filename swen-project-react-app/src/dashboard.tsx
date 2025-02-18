import React, { useState, useEffect } from "react";
import "./styles/dashboard.css"
import Plot from "react-plotly.js"
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";

const data = 
[
    ['AlgonquinPeak', new Date('2025-01-30T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-31T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-31T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-31T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-31T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-29T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-28T10:00:00')],
    ['AlgonquinPeak', new Date('2025-01-27T10:00:00')]
]

var xData = ['']

const startDate = new Date('2025-01-27T10:00:00')
const endDate = new Date('2025-01-31T10:00:00')
let dateFrequencies = {}

    
const dashboard = () => {
    const { getAll } = TrailData();

    getAll().then(response => {
        const responseJson = response.json;
        console.log(responseJson);
        console.log(responseJson[0])
        // const count = Object.keys(responseJson).length;
        // for (var i = 0; i < count; i++) {
        //     console.log(responseJson[i].timestamp)
        // }
        
        Object.values(responseJson).forEach((trail) => {
            xData.push(trail.timestamp)
        })
    })
        
    
    // console.log(getAll().then())

    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedDateEnd, setSelectedDateEnd] = useState<Date | null>(new Date());
    const [trail, setTrail] = useState<String>("All Trails");
    const [granularity, setGranularity] = useState<String | null>(null);

    const handleStartDateChange = (startDate: Date | null) => {
        setSelectedDate(startDate);
        console.log(startDate)
        console.log(selectedDateEnd)
        console.log(trail)

        
    }
    const handleEndDateChange = (e: Date | null) => {
        setSelectedDateEnd(e);

    }
    const handleTrailChange = (e:String) => {
        setTrail(e);
    }


    const handleGranularityChange = (e: String) => {
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
                        y: [2, 6, 3, 3, 4, 5, 7, 8],
                        type: 'line',
                        name: 'Wolf Jaw Peak',
                        mode: 'lines+markers',
                        marker: {color: 'red'},
                    },

                    ]}
                    layout={
                        {width: 1000,
                        height: 700, 
                        xaxis: {
                            title: {
                            text: 'Date',
                            font: {
                                size: 18,
                                color: '#7f7f7f'
                                }
                            },
                        },
                        yaxis: {
                            title: {
                            text: 'Hikers',
                            font: {
                                size: 18,
                                color: '#7f7f7f'
                                }
                            },
                        },
                    
                        }}
                />
                <div style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
                    <div>
                        <label>Start Date:</label>
                        <DatePicker
                            selected={selectedDate}
                            onChange={handleStartDateChange}
                            dateFormat="MM/dd/yyyy"
                            isClearable
                            placeholderText="Select a date"
                        />
                        </div>
                        <div>
                        <label>End Date:</label>
                        <DatePicker
                            selected={selectedDateEnd}
                            onChange={handleEndDateChange}
                            dateFormat="MM/dd/yyyy"
                            isClearable
                            placeholderText="Select a date"
                        />
                    </div>
                    <select 
                        name="Granularity" 
                        id="granularity"
                        onChange={(e) => handleGranularityChange(e.target.value)}>

                        <option value="Hourly">Hourly</option>
                        <option value="Daily">Daily</option>
                        <option value="Monthly">Monthly</option>
                        <option value="Yearly">Yearly</option>
                    </select>
                    <select 
                        name="Trail" 
                        id="trail"
                        onChange={(e) => handleTrailChange(e.target.value)}>
                        <option value="All Trails">All Trails</option>
                        <option value="Mt. Marcy">Mt. Marcy</option>
                        <option value="Wolf Creek Mountin">Wolf Creek Mountin</option>
                        <option value="Mt. Joe">Mt. Joe</option>
                        <option value="Mt. America">Mt. America</option>
                    </select>
                </div>
            </div>
        </body>
    );
}

export default dashboard;