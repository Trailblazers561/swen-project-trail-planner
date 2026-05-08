import React, { useState, useEffect, useMemo, useRef } from "react";
import TrailSelector from "./components/trailselector.tsx";
import EditTrailModal from "./components/EditTrailModal";
import EditTrailGroupModal from "./components/EditTrailGroupModal";
import AssociateDeviceModal from "./components/AssociateDeviceModal";
import "./styles/dashboard.css";
import Plot from "react-plotly.js";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
import { useNavigate } from "react-router-dom";

interface Trail {
    trail_id: number;
    trail_name: string;
}

interface TrailGroup {
    group_name: string;
    trail_ids: number[];
}

const dashboard = () => {
    const navigate = useNavigate();
    const handleLogout = () => {
        sessionStorage.clear();
        navigate("/login");
    };

    const {
        getTrailLogsBetweenDates,
        getDeviceMetadata,
        getTrailMetadata,
        getTrailGroups,
    } = TrailData();

    const [trailMetadata, setTrailMetadata] = useState<Trail[]>([]);
    const [trailGroups, setTrailGroups] = useState<TrailGroup[]>([]);

    // Build trail map from metadata - updates automatically when metadata changes
    const trailMap = useMemo<Record<string, number>>(() => {
        const map: Record<string, number> = { "All Trails": 0 };
        trailMetadata
            .filter((t) => t && t.trail_name && t.trail_name.trim().length > 0)
            .forEach((trail: Trail) => {
                map[trail.trail_name] = trail.trail_id;
            });
        return map;
    }, [trailMetadata]);

    const [selectedTrailForEdit, setSelectedTrailForEdit] =
        useState<Trail | null>(null);
    const [isEditTrailModalOpen, setIsEditTrailModalOpen] = useState(false);
    const [isAddTrailModalOpen, setIsAddTrailModalOpen] = useState(false);
    const [isEditGroupModalOpen, setIsEditGroupModalOpen] = useState(false);
    const [isAddGroupModalOpen, setIsAddGroupModalOpen] = useState(false);
    const [isAssociateDeviceModalOpen, setIsAssociateDeviceModalOpen] =
        useState(false);

    const [graphLines, setGraphLines] = useState<
        Array<{
            name: string;
            x: Date[];
            y: number[];
        }>
    >([]);

    // Auto-select 01/01/2025 as start date
    const [selectedDate, setSelectedDate] = useState<Date | null>(
        new Date(new Date().getFullYear(), 0, 1)
    );
    const [selectedDateEnd, setSelectedDateEnd] = useState<Date | null>(
        new Date()
    );
    const [trails, setTrails] = useState<string[]>([]);
    const [granularity, setGranularity] = useState<string | null>(null);
    const [granularityOptions, setGranularityOptions] = useState<string[]>([]);
    const [graphTitle, setGraphTitle] = useState<string>("No Trails Selected");
    const [hasDefaulted, setHasDefaulted] = useState(false);
    const [viewMode, setViewMode] = useState<"graph" | "list">("graph");
    const [trailListData, setTrailListData] = useState<
        Array<{
            trail_id: number;
            trail_name: string;
            weeklyCount: number;
            batteryStatus: number | null;
            lastUpdated: string | null;
        }>
    >([]);
    const [loadingListData, setLoadingListData] = useState(false);
    const [deviceMetadataCache, setDeviceMetadataCache] = useState<any[] | null>(
        null
    );
    const [dataFetchError, setDataFetchError] = useState<string | null>(null);
    const [loadingChart, setLoadingChart] = useState(false);
    const [aggregate, setAggregate] = useState(false);
    const isFetchingListData = useRef(false);

    // Load trail metadata and groups from database
    useEffect(() => {
        loadTrailData();
    }, []);

    // Default to "All Trails" when data is loaded and dates are set (only once)
    useEffect(() => {
        if (
            trailMetadata.length > 0 &&
            trails.length === 0 &&
            selectedDate &&
            selectedDateEnd &&
            !hasDefaulted
        ) {
            const defaultTrails = ["All Trails"];
            setTrails(defaultTrails);
            setHasDefaulted(true);
            // Trigger graph load after a small delay to ensure state is set
            setTimeout(() => {
                if (granularity) {
                    getResponse(
                        selectedDate,
                        selectedDateEnd,
                        defaultTrails,
                        granularity
                    );
                }
            }, 100);
        }
    }, [trailMetadata, selectedDate, selectedDateEnd, granularity, hasDefaulted]);

    const loadTrailData = async () => {
        try {
            const [metadataResponse, groupsResponse] = await Promise.all([
                getTrailMetadata(),
                getTrailGroups(),
            ]);

            if (metadataResponse.success && groupsResponse.success) {
                const metadata = await metadataResponse.json;
                const groups = await groupsResponse.json;

                // Filter out any invalid entries
                const validMetadata = (metadata || []).filter(
                    (t: Trail) =>
                        t &&
                        t.trail_id !== undefined &&
                        t.trail_name &&
                        t.trail_name.trim().length > 0
                );
                // Filter out invalid groups and empty groups (groups with no trails)
                const validGroups = (groups || []).filter(
                    (g: TrailGroup) =>
                        g &&
                        g.group_name &&
                        g.group_name.trim().length > 0 &&
                        g.trail_ids &&
                        Array.isArray(g.trail_ids) &&
                        g.trail_ids.length > 0
                );

                setTrailMetadata(validMetadata);
                setTrailGroups(validGroups);
            } else {
                // 401 triggers a redirect in api.ts; any other failure shows an error
                setDataFetchError("Failed to load trail list. Please refresh the page.");
            }
        } catch (error) {
            console.error("Error loading trail data:", error);
            setDataFetchError("Failed to load trail list. Please refresh the page.");
        }
    };

    const handleEditTrail = () => {
        setIsEditTrailModalOpen(true);
        setSelectedTrailForEdit(null);
    };

    const handleAddTrail = () => {
        setIsAddTrailModalOpen(true);
    };

    const handleEditGroup = () => {
        setIsEditGroupModalOpen(true);
    };

    const handleAddGroup = () => {
        setIsAddGroupModalOpen(true);
    };

    const handleAssociateDevice = () => {
        setIsAssociateDeviceModalOpen(true);
    };

    const handleTrailUpdated = async () => {
        await loadTrailData();
        // Refresh graph - wait for state to update
        setTimeout(() => {
            const currentTrails = trails.length > 0 ? trails : ["All Trails"];
            if (selectedDate && selectedDateEnd && granularity) {
                if (trails.length === 0) {
                    setTrails(currentTrails);
                }
                getResponse(selectedDate, selectedDateEnd, currentTrails, granularity);
            }
        }, 500);
    };

    function getDateDifference(startDate: Date, endDate: Date): number {
        const diffTime = Math.abs(endDate.getTime() - startDate.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    function updateGranularityOptions(
        startDate: Date | null,
        endDate: Date | null
    ) {
        if (!startDate || !endDate) return;

        const daysDiff = getDateDifference(startDate, endDate);

        let options: string[] = [];
        if (daysDiff >= 1825) {
            options = ["Yearly", "Monthly"];
        } else if (daysDiff >= 730) {
            options = ["Yearly", "Monthly", "Weekly", "Daily"];
        } else if (daysDiff >= 60) {
            options = ["Monthly", "Weekly", "Daily"];
        } else if (daysDiff >= 30) {
            options = ["Weekly", "Daily"];
        } else if (daysDiff >= 7) {
            options = ["Daily"];
        } else if (daysDiff <= 3) {
            options = ["Daily", "Hourly"];
        } else {
            options = ["Daily"];
        }

        setGranularityOptions(options);
        setGranularity(options.includes("Weekly") ? "Weekly" : options[0]);
    }

    useEffect(() => {
        updateGranularityOptions(selectedDate, selectedDateEnd);
    }, [selectedDate, selectedDateEnd]);

    useEffect(() => {
        if (selectedDate && selectedDateEnd && trails.length > 0 && granularity) {
            getResponse(selectedDate, selectedDateEnd, trails, granularity);
        }
    }, [selectedDate, selectedDateEnd, trails, granularity]);

    function getDateRanges(
        startDate: Date,
        endDate: Date,
        granularity: string = "Daily"
    ): { start: Date; end: Date }[] {
        let ranges: { start: Date; end: Date }[] = [];
        let current: Date = new Date(startDate);
        let end: Date = new Date(endDate);

        while (current < end) {
            let next: Date = new Date(current);
            if (granularity === "Hourly") {
                next.setHours(next.getHours() + 1);
            } else if (granularity === "Daily") {
                next.setDate(next.getDate() + 1);
            } else if (granularity === "Weekly") {
                next.setDate(next.getDate() + 7);
            } else if (granularity === "Monthly") {
                next.setMonth(next.getMonth() + 1);
            } else if (granularity === "Yearly") {
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

    function countOccurrencesInRanges(
        ranges: { start: Date; end: Date }[],
        events: Date[]
    ): Map<Date, number> {
        let occurrences = new Map<Date, number>();

        for (let range of ranges) {
            let count = events.filter(
                (date) => date >= range.start && date <= range.end
            ).length;
            occurrences.set(range.start, count);
        }
        return occurrences;
    }

    async function getResponse(
        startDate: Date | null,
        endDate: Date | null,
        trails: string[],
        granularity: string = "Daily"
    ) {
        if (!startDate || !endDate || !granularity || trails.length === 0) return;

        setDataFetchError(null);
        setLoadingChart(true);
        try {
            let trailIds: number[] = [];
            let includesAllTrails = trails.includes("All Trails");

            if (includesAllTrails) {
                trailIds = trailMetadata
                    .filter((t) => t && t.trail_id && t.trail_id !== 0)
                    .map((t) => t.trail_id);
            } else {
                for (var i = 0; i < trails.length; i++) {
                    const trailId = trailMap[trails[i]];
                    if (trailId !== undefined) {
                        trailIds.push(trailId);
                    }
                }
            }

            if (trailIds.length === 0 && !includesAllTrails) return;

            const response = await getTrailLogsBetweenDates(
                Math.floor(startDate.getTime() / 1000),
                Math.floor(endDate.getTime() / 1000),
                trailIds
            );

            const responseJson = await response.json;

            let ranges = getDateRanges(startDate, endDate, granularity);
            let events: Map<number, Date[]> = new Map<number, Date[]>();

            (responseJson as { trail_id: number; timestamp: number }[]).forEach(
                (entry) => {
                    if (!events.has(entry.trail_id)) {
                        events.set(entry.trail_id, []);
                    }
                    events.get(entry.trail_id)!.push(new Date(entry.timestamp * 1000));
                }
            );

            var lines: { name: string; x: Date[]; y: number[] }[] = [];

            const trailIdToName = new Map<number, string>();
            trailMetadata
                .filter((t) => t && t.trail_name)
                .forEach((trail: Trail) => {
                    trailIdToName.set(trail.trail_id, trail.trail_name);
                });

            if (includesAllTrails) {
                events.forEach((dates, trailId) => {
                    if (trailId !== 0 && dates.length > 0) {
                        const trailName = trailIdToName.get(trailId) || `Trail ${trailId}`;
                        const occurrences = countOccurrencesInRanges(ranges, dates);
                        lines.push({
                            name: trailName,
                            x: Array.from(occurrences.keys()),
                            y: Array.from(occurrences.values()),
                        });
                    }
                });
            } else {
                for (let i = 0; i < trails.length; i++) {
                    const trailName = trails[i];
                    const trailId = trailMap[trailName];
                    if (trailId === undefined) continue;

                    const dates: Date[] = events.get(trailId) ?? [];
                    if (dates.length === 0) continue;

                    const occurrences = countOccurrencesInRanges(ranges, dates);
                    const xData = Array.from(occurrences.keys());
                    const yData = Array.from(occurrences.values());

                    lines.push({ name: trailName, x: xData, y: yData });
                }
            }
            setGraphLines(lines);
            setGraphTitle(formatGraphTitle(startDate, endDate, trails));
        } catch (error) {
            console.error("Error fetching trail data:", error);
            setDataFetchError("Failed to load trail data. Check your connection and try again.");
        } finally {
            setLoadingChart(false);
        }
    }

    function formatGraphTitle(
        startDate: Date | null,
        endDate: Date | null,
        trails: string[]
    ): string {
        if (!startDate || !endDate || trails.length === 0)
            return "No trails selected";

        const startStr = startDate.toLocaleDateString();
        const endStr = endDate.toLocaleDateString();
        const includesAll = trails.includes("All Trails");

        if (includesAll && trails.length === 1) {
            return `All Trails from ${startStr} to ${endStr}`;
        } else if (includesAll && trails.length > 1) {
            return `All Trails and others from ${startStr} to ${endStr}`;
        } else if (trails.length === 1) {
            return `${trails[0]} from ${startStr} to ${endStr}`;
        } else if (trails.length === 2) {
            return `${trails[0]} & ${trails[1]} from ${startStr} to ${endStr}`;
        } else {
            return `${trails.length} Trails from ${startStr} to ${endStr}`;
        }
    }

    const handleStartDateChange = (startDate: Date | null) => {
        setSelectedDate(startDate);
    };

    const handleEndDateChange = (endDate: Date | null) => {
        setSelectedDateEnd(endDate);
    };

    const handleTrailChange = (selectedTrails: string[]) => {
        setTrails(selectedTrails);

        if (selectedTrails.length === 0) {
            setGraphLines([]);
            setGraphTitle("No Trails Selected");
            return;
        }
    };

    const handleGranularityChange = (granularity: string) => {
        setGranularity(granularity);
    };

    // Load device metadata once and cache it
    useEffect(() => {
        if (deviceMetadataCache === null) {
            (async () => {
                const response = await getDeviceMetadata();
                if (response.success) {
                    const devices = await response.json;
                    setDeviceMetadataCache(devices);
                }
            })();
        }
    }, []);

    // Compute list data from cached data and trail metadata
    useEffect(() => {
        if (
            viewMode === "list" &&
            trailMetadata.length > 0 &&
            deviceMetadataCache !== null &&
            !isFetchingListData.current
        ) {
            isFetchingListData.current = true;
            setLoadingListData(true);

            (async () => {
                try {
                    // Get last week's date range
                    const now = new Date();
                    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    const startTimestamp = Math.floor(oneWeekAgo.getTime() / 1000);
                    const endTimestamp = Math.floor(now.getTime() / 1000);

                    // Get all trail IDs
                    const trailIds = trailMetadata
                        .filter((t) => t && t.trail_id && t.trail_id !== 0)
                        .map((t) => t.trail_id);

                    if (trailIds.length === 0) {
                        setTrailListData([]);
                        setLoadingListData(false);
                        isFetchingListData.current = false;
                        return;
                    }

                    // Fetch weekly counts
                    const logsResponse = await getTrailLogsBetweenDates(
                        startTimestamp,
                        endTimestamp,
                        trailIds
                    );
                    const logs = logsResponse.success ? await logsResponse.json : [];
                    const devices = deviceMetadataCache || [];

                    // Group devices by trail_id and find most recent for each trail
                    const trailDeviceMap = new Map<
                        number,
                        { battery: number | null; lastUpdate: number | null }
                    >();

                    devices.forEach((device: any) => {
                        const trailId = device.current_trail_id;
                        if (trailId && trailId !== 0) {
                            const lastUpdate = device.last_update
                                ? typeof device.last_update === "number"
                                    ? device.last_update
                                    : parseInt(device.last_update)
                                : null;
                            const battery =
                                device.battery !== undefined && device.battery !== null
                                    ? typeof device.battery === "number"
                                        ? device.battery
                                        : parseFloat(device.battery)
                                    : null;

                            const existing = trailDeviceMap.get(trailId);
                            if (
                                !existing ||
                                (lastUpdate &&
                                    (!existing.lastUpdate || lastUpdate > existing.lastUpdate))
                            ) {
                                trailDeviceMap.set(trailId, { battery, lastUpdate });
                            }
                        }
                    });

                    // Count logs per trail for the week
                    const trailCounts = new Map<number, number>();
                    logs.forEach((log: { trail_id: number }) => {
                        const trailId = log.trail_id;
                        trailCounts.set(trailId, (trailCounts.get(trailId) || 0) + 1);
                    });

                    // Build the list data
                    const listData = trailMetadata
                        .filter((t) => t && t.trail_name && t.trail_id && t.trail_id !== 0)
                        .map((trail) => {
                            const weeklyCount = trailCounts.get(trail.trail_id) || 0;
                            const deviceInfo = trailDeviceMap.get(trail.trail_id);
                            const batteryStatus = deviceInfo?.battery ?? null;
                            const lastUpdateTimestamp = deviceInfo?.lastUpdate ?? null;

                            let lastUpdated: string | null = null;
                            if (lastUpdateTimestamp) {
                                const date = new Date(lastUpdateTimestamp * 1000);
                                const month = String(date.getMonth() + 1).padStart(2, "0");
                                const day = String(date.getDate()).padStart(2, "0");
                                const year = date.getFullYear();
                                // Format as MM/DD/YYYY
                                lastUpdated = `${month}/${day}/${year}`;
                            }

                            return {
                                trail_id: trail.trail_id,
                                trail_name: trail.trail_name,
                                weeklyCount,
                                batteryStatus,
                                lastUpdated,
                            };
                        })
                        .sort((a, b) => a.trail_name.localeCompare(b.trail_name));

                    setTrailListData(listData);
                    setLoadingListData(false);
                    isFetchingListData.current = false;
                } catch (error) {
                    console.error("Error loading trail list data:", error);
                    setTrailListData([]);
                    setLoadingListData(false);
                    isFetchingListData.current = false;
                }
            })();
        }
    }, [viewMode, trailMetadata, deviceMetadataCache]);

    // Reset fetch flag when switching away from list view
    useEffect(() => {
        if (viewMode === "graph") {
            isFetchingListData.current = false;
        }
    }, [viewMode]);

    const toggleView = () => {
        setViewMode((prev) => (prev === "graph" ? "list" : "graph"));
    };

    return (
        <body>
            <div className="dashboard-div">
                <div
                    style={{
                        display: "flex",
                        padding: "10px",
                        gap: "10px",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}
                >
                    <button
                        className="action-button"
                        type="button"
                        onClick={toggleView}
                        style={{
                            backgroundColor: viewMode === "graph" ? "#007bff" : "#6c757d",
                            color: "white",
                        }}
                    >
                        {viewMode === "graph"
                            ? "Switch to List View"
                            : "Switch to Graph View"}
                    </button>
                    <div style={{ display: "flex", gap: "10px" }}>
                        <button
                            className="action-button"
                            type="button"
                            onClick={handleAddTrail}
                        >
                            Add Trail
                        </button>
                        <button
                            className="action-button"
                            type="button"
                            onClick={handleEditTrail}
                        >
                            Edit Trail Info
                        </button>
                        <button
                            className="action-button"
                            type="button"
                            onClick={handleAddGroup}
                        >
                            Add Group
                        </button>
                        <button
                            className="action-button"
                            type="button"
                            onClick={handleEditGroup}
                        >
                            Edit Group
                        </button>
                        <button
                            className="action-button"
                            type="button"
                            onClick={handleAssociateDevice}
                        >
                            Associate Device
                        </button>
                        <button
                            className="logout-button"
                            type="button"
                            onClick={handleLogout}
                        >
                            Logout
                        </button>
                    </div>
                </div>
                {viewMode === "graph" ? (
                    <div style={{ position: "relative" }}>
                        {loadingChart && (
                            <div style={{
                                position: "absolute",
                                top: 0, left: 0, right: 0, bottom: 0,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                background: "rgba(255,255,255,0.6)",
                                zIndex: 10,
                            }}>
                                <div style={{
                                    width: 48,
                                    height: 48,
                                    border: "5px solid #e0e0e0",
                                    borderTopColor: "#007bff",
                                    borderRadius: "50%",
                                    animation: "spin 0.8s linear infinite",
                                }} />
                            </div>
                        )}
                        <Plot
                            className="graph"
                            config={{ displayModeBar: false }}
                            data={aggregate && graphLines.length > 0
                                ? [{
                                    x: graphLines[0].x,
                                    y: graphLines[0].y.map((_, i) =>
                                        graphLines.reduce((sum, line) => sum + (line.y[i] ?? 0), 0)
                                    ),
                                    type: "scatter" as const,
                                    mode: "lines+markers" as const,
                                    name: "Combined",
                                    marker: { color: "blue" },
                                }]
                                : graphLines.map((line, index) => ({
                                    x: line.x,
                                    y: line.y,
                                    type: "scatter" as const,
                                    mode: "lines+markers" as const,
                                    name: line.name,
                                    marker: {
                                        color: [
                                            "red",
                                            "blue",
                                            "green",
                                            "orange",
                                            "goldenrod",
                                            "limegreen",
                                            "papayawhip",
                                        ][index % 7],
                                    },
                                }))
                            }
                            layout={{
                                title: {
                                    text: graphTitle,
                                    font: { size: 24 },
                                    xref: "paper",
                                    x: 0.05,
                                },
                                width: 1000,
                                height: 700,
                                xaxis: {
                                    title: { text: "Date", font: { size: 18, color: "#7f7f7f" } },
                                    autorange: true,
                                    rangemode: "tozero",
                                },
                                yaxis: {
                                    title: {
                                        text: "Hikers",
                                        font: { size: 18, color: "#7f7f7f" },
                                    },
                                    range: [0, null],
                                    autorange: true,
                                    rangemode: "tozero",
                                },
                            }}
                        />
                        {dataFetchError && (
                            <div style={{
                                color: "#721c24",
                                background: "#f8d7da",
                                border: "1px solid #f5c6cb",
                                borderRadius: "4px",
                                padding: "8px 16px",
                                margin: "0 16px 8px",
                            }}>
                                {dataFetchError}
                            </div>
                        )}
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
                                    {granularityOptions.map((option) => (
                                        <option key={option} value={option}>
                                            {option}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="filter-group">
                                <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer" }}>
                                    <input
                                        type="checkbox"
                                        checked={aggregate}
                                        onChange={(e) => setAggregate(e.target.checked)}
                                        style={{ width: 16, height: 16, cursor: "pointer" }}
                                    />
                                    Aggregate
                                </label>
                            </div>
                            <div className="filter-group">
                                <label>Trail:</label>
                                <TrailSelector
                                    onChange={handleTrailChange}
                                    clearTrails={() => setTrails([])}
                                    clearGraph={() => setGraphLines([])}
                                    clearName={() => setGraphTitle("No Trails Selected")}
                                    trailMetadata={trailMetadata}
                                    trailGroups={trailGroups}
                                />
                            </div>
                        </div>
                    </div>
                ) : (
                    <div style={{ padding: "20px" }}>
                        <h2
                            style={{
                                marginBottom: "20px",
                                fontSize: "24px",
                                fontWeight: "bold",
                                color: "#333",
                            }}
                        >
                            Trail Status Overview
                        </h2>
                        {loadingListData ? (
                            <div style={{ textAlign: "center", padding: "40px" }}>
                                Loading trail data...
                            </div>
                        ) : (
                            <div style={{ overflowX: "auto" }}>
                                <table
                                    style={{
                                        width: "100%",
                                        borderCollapse: "collapse",
                                        backgroundColor: "#fff",
                                        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                                    }}
                                >
                                    <thead>
                                        <tr style={{ backgroundColor: "#007bff", color: "white" }}>
                                            <th
                                                style={{
                                                    padding: "12px",
                                                    textAlign: "left",
                                                    border: "1px solid #ddd",
                                                    fontWeight: "bold",
                                                }}
                                            >
                                                Trail Name
                                            </th>
                                            <th
                                                style={{
                                                    padding: "12px",
                                                    textAlign: "center",
                                                    border: "1px solid #ddd",
                                                    fontWeight: "bold",
                                                }}
                                            >
                                                Weekly Count
                                            </th>
                                            <th
                                                style={{
                                                    padding: "12px",
                                                    textAlign: "center",
                                                    border: "1px solid #ddd",
                                                    fontWeight: "bold",
                                                }}
                                            >
                                                Battery Status
                                            </th>
                                            <th
                                                style={{
                                                    padding: "12px",
                                                    textAlign: "center",
                                                    border: "1px solid #ddd",
                                                    fontWeight: "bold",
                                                }}
                                            >
                                                Last Updated
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {trailListData.length === 0 ? (
                                            <tr>
                                                <td
                                                    colSpan={4}
                                                    style={{
                                                        padding: "20px",
                                                        textAlign: "center",
                                                        color: "#666",
                                                    }}
                                                >
                                                    No trails found
                                                </td>
                                            </tr>
                                        ) : (
                                            trailListData.map((trail, index) => (
                                                <tr
                                                    key={trail.trail_id}
                                                    style={{
                                                        backgroundColor:
                                                            index % 2 === 0 ? "#f9f9f9" : "#ffffff",
                                                        borderBottom: "1px solid #e0e0e0",
                                                    }}
                                                >
                                                    <td
                                                        style={{
                                                            padding: "12px",
                                                            border: "1px solid #ddd",
                                                            fontWeight: "500",
                                                            color: "#333",
                                                        }}
                                                    >
                                                        {trail.trail_name}
                                                    </td>
                                                    <td
                                                        style={{
                                                            padding: "12px",
                                                            textAlign: "center",
                                                            border: "1px solid #ddd",
                                                            color: "#333",
                                                        }}
                                                    >
                                                        {trail.weeklyCount}
                                                    </td>
                                                    <td
                                                        style={{
                                                            padding: "12px",
                                                            textAlign: "center",
                                                            border: "1px solid #ddd",
                                                            color: "#333",
                                                        }}
                                                    >
                                                        {trail.batteryStatus !== null ? (
                                                            <span
                                                                style={{
                                                                    color:
                                                                        trail.batteryStatus > 50
                                                                            ? "#28a745"
                                                                            : trail.batteryStatus > 20
                                                                                ? "#ffc107"
                                                                                : "#dc3545",
                                                                    fontWeight: "bold",
                                                                }}
                                                            >
                                                                {trail.batteryStatus}%
                                                            </span>
                                                        ) : (
                                                            <span style={{ color: "#999" }}>N/A</span>
                                                        )}
                                                    </td>
                                                    <td
                                                        style={{
                                                            padding: "12px",
                                                            textAlign: "center",
                                                            border: "1px solid #ddd",
                                                            color: "#333",
                                                        }}
                                                    >
                                                        {trail.lastUpdated || (
                                                            <span style={{ color: "#999" }}>N/A</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}
            </div>
            <EditTrailModal
                isOpen={isEditTrailModalOpen}
                onClose={() => {
                    setIsEditTrailModalOpen(false);
                    setSelectedTrailForEdit(null);
                }}
                trail={selectedTrailForEdit}
                onUpdate={handleTrailUpdated}
                availableTrails={trailMetadata}
                isCreateMode={false}
            />
            <EditTrailModal
                isOpen={isAddTrailModalOpen}
                onClose={() => {
                    setIsAddTrailModalOpen(false);
                }}
                trail={null}
                onUpdate={handleTrailUpdated}
                availableTrails={trailMetadata}
                isCreateMode={true}
            />
            <EditTrailGroupModal
                isOpen={isEditGroupModalOpen}
                onClose={() => setIsEditGroupModalOpen(false)}
                onUpdate={handleTrailUpdated}
                availableTrails={trailMetadata}
                trailGroups={trailGroups}
                isCreateMode={false}
            />
            <EditTrailGroupModal
                isOpen={isAddGroupModalOpen}
                onClose={() => setIsAddGroupModalOpen(false)}
                onUpdate={handleTrailUpdated}
                availableTrails={trailMetadata}
                trailGroups={trailGroups}
                isCreateMode={true}
            />
            <AssociateDeviceModal
                isOpen={isAssociateDeviceModalOpen}
                onClose={() => setIsAssociateDeviceModalOpen(false)}
                onUpdate={handleTrailUpdated}
            />
        </body>
    );
};

export default dashboard;
