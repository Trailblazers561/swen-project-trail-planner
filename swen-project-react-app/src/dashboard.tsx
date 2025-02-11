import React, { useState, useEffect } from "react";
import "./styles/dashboard.css"
import Plot from "react-plotly.js"
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

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

const startDate = new Date('2025-01-27T10:00:00')
const endDate = new Date('2025-01-31T10:00:00')
let dateFrequencies = {}

    
const dashboard = () => {
    return(
        <body>
            <div className="dashboard-div">
                <Plot className="graph"
                    config={ {displayModeBar: false} }
                    data={[
                    {
                        x: [
                            "2025-02-04 12:00:00",
                            "2025-02-08 18:30:00",
                            "2025-02-12 05:15:00",
                            "2025-02-16 23:45:00",
                            "2025-02-20 14:00:00",
                            "2025-02-24 07:20:00",
                            "2025-02-27 19:10:00",
                            "2025-03-03 02:50:00"],
                        y: [2, 6, 3, 3, 4, 5, 7, 8],
                        type: 'line',
                        name: 'Wolf Jaw Peak',
                        mode: 'lines+markers',
                        marker: {color: 'red'},
                    },
                    // {
                    //     type: 'line',
                    //     name: 'Mt. Marcy', // name of trace label
                    //     x: ['2013-10-04 22:23:00', '2013-11-04 22:23:00', '2013-12-04 22:23:00'], 
                    //     y: [2, 5, 7, 4, 5, 6, 4, 5]},
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
                            selected={startDate}
                            selectsStart
                            startDate={startDate}
                            endDate={endDate}
                        />
                        </div>
                        <div>
                        <label>End Date:</label>
                        <DatePicker
                            selected={endDate}
                            selectsEnd
                            startDate={startDate}
                            endDate={endDate}
                        />
                    </div>
                    <select name="Granularity" id="granularity">
                        <option value="Hourly">Hourly</option>
                        <option value="Daily">Daily</option>
                        <option value="Monthly">Monthly</option>
                        <option value="Yearly">Yearly</option>
                    </select>
                    <select name="Trail" id="trail">
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