import React, { useState, useEffect, useMemo, useRef } from "react";
import TrailSelector from "./components/trailselector.tsx";
import EditTrailModal from "./components/EditTrailModal";
import EditTrailGroupModal from "./components/EditTrailGroupModal";
import DeviceDetailModal from "./components/DeviceDetailModal";
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
        getDeviceCallLog,
        getTrailMetadata,
        getTrailGroups,
        updateDeviceTrailAssociation,
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
    const [assigningDeviceId, setAssigningDeviceId] = useState<string | null>(null);
    const [assignTrailId, setAssignTrailId] = useState<number>(0);
    const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null);

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
    const [deviceListData, setDeviceListData] = useState<
        Array<{
            device_id: string;
            trail_name: string | null;
            trail_id: number | null;
            weeklyCount: number;
            batteryStatus: number | null;
            firmwareVersion: string | null;
            lastCallIn: string | null;
        }>
    >([]);
    const [loadingListData, setLoadingListData] = useState(false);
    const [deviceFilter, setDeviceFilter] = useState("");
    const [deviceMetadataCache, setDeviceMetadataCache] = useState<any[] | null>(
        null
    );
    const [dataFetchError, setDataFetchError] = useState<string | null>(null);
    const [loadingChart, setLoadingChart] = useState(false);
    const [aggregate, setAggregate] = useState(false);
    const [selectedGroupName, setSelectedGroupName] = useState<string | null>("All Areas");
    const [pendingRefresh, setPendingRefresh] = useState(false);
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

    // Refresh graph after a trail/group update — runs after render so trailMetadata is fresh.
    // Derives trail list from fresh group data when a group is active, bypassing stale trails state.
    useEffect(() => {
        if (!pendingRefresh) return;
        if (!selectedDate || !selectedDateEnd || !granularity) return;
        let currentTrails: string[];
        if (selectedGroupName && selectedGroupName !== "All Areas") {
            const group = trailGroups.find(g => g.group_name === selectedGroupName);
            if (group) {
                currentTrails = group.trail_ids
                    .map(id => trailMetadata.find(t => t.trail_id === id)?.trail_name)
                    .filter((name): name is string => !!name);
            } else {
                currentTrails = trails.length > 0 ? trails : ["All Trails"];
            }
        } else {
            currentTrails = trails.length > 0 ? trails : ["All Trails"];
        }
        getResponse(selectedDate, selectedDateEnd, currentTrails, granularity);
        setPendingRefresh(false);
    }, [pendingRefresh, trailMetadata]);

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


    const handleTrailUpdated = async () => {
        await loadTrailData();
        setPendingRefresh(true);
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
        // Gate on trailMetadata being loaded — otherwise getResponse builds
        // its trailIdToName map from an empty array and falls back to
        // "Trail N" for every legend label. Adding trailMetadata to the
        // dependency array also makes the chart re-fetch with correct names
        // if trailMetadata arrives after the first attempted render (which
        // happens on cold loads when /trail_data returns before
        // /trail_metadata).
        if (
            selectedDate &&
            selectedDateEnd &&
            trails.length > 0 &&
            granularity &&
            trailMetadata.length > 0
        ) {
            getResponse(selectedDate, selectedDateEnd, trails, granularity);
        }
    }, [selectedDate, selectedDateEnd, trails, granularity, trailMetadata]);

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

            if (!response.success) {
                setDataFetchError("Failed to load trail data. Check your connection and try again.");
                return;
            }

            const responseJson = response.json;

            if (!Array.isArray(responseJson)) {
                setDataFetchError("Failed to load trail data. Check your connection and try again.");
                return;
            }

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
            setGraphTitle(formatGraphTitle(startDate, endDate, trails, selectedGroupName));
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
        trails: string[],
        groupName: string | null
    ): string {
        if (!startDate || !endDate || trails.length === 0)
            return "No trails selected";

        const startStr = startDate.toLocaleDateString();
        const endStr = endDate.toLocaleDateString();

        if (groupName) {
            return `${groupName} from ${startStr} to ${endStr}`;
        }

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

                    // Fetch call log and device metadata in parallel; weekly counts fetched after
                    const [callLogResponse, devicesResponse] = await Promise.all([
                        getDeviceCallLog(),
                        getDeviceMetadata(),
                    ]);
                    const callLogEntries: any[] = callLogResponse.success ? callLogResponse.json : [];
                    const devices: any[] = devicesResponse.success ? devicesResponse.json : (deviceMetadataCache || []);

                    if (callLogEntries.length === 0) {
                        setDeviceListData([]);
                        setLoadingListData(false);
                        isFetchingListData.current = false;
                        return;
                    }

                    // Map device_id → current trail_id from DeviceMetadata
                    const deviceTrailMap = new Map<string, number>();
                    devices.forEach((d: any) => {
                        if (d.device_id && d.current_trail_id && d.current_trail_id !== 0) {
                            deviceTrailMap.set(d.device_id, d.current_trail_id);
                        }
                    });

                    // Map trail_id → trail_name
                    const trailNameMap = new Map<number, string>();
                    trailMetadata.forEach((t: any) => {
                        if (t.trail_id && t.trail_name) trailNameMap.set(t.trail_id, t.trail_name);
                    });

                    // Get weekly counts for all trails that have a device
                    const trailIdsWithDevices = [...new Set(
                        callLogEntries.map(e => deviceTrailMap.get(e.device_id)).filter((id): id is number => !!id && id !== 0)
                    )];
                    let trailCounts = new Map<number, number>();
                    if (trailIdsWithDevices.length > 0) {
                        const logsResponse = await getTrailLogsBetweenDates(startTimestamp, endTimestamp, trailIdsWithDevices);
                        const logs: any[] = logsResponse.success ? logsResponse.json : [];
                        logs.forEach((log: { trail_id: number }) => {
                            trailCounts.set(log.trail_id, (trailCounts.get(log.trail_id) || 0) + 1);
                        });
                    }

                    const formatDate = (ts: number | null) => {
                        if (!ts) return null;
                        const d = new Date(ts * 1000);
                        return `${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}/${d.getFullYear()}`;
                    };

                    // Build device-centric list from call log entries
                    const callLogDeviceIds = new Set(callLogEntries.map((e: any) => e.device_id));
                    const callLogRows = callLogEntries.map((entry: any) => {
                        const trailId = deviceTrailMap.get(entry.device_id) ?? null;
                        const trailName = trailId ? (trailNameMap.get(trailId) ?? null) : null;
                        const ts = entry.timestamp ? (typeof entry.timestamp === "number" ? entry.timestamp : parseInt(entry.timestamp)) : null;
                        return {
                            device_id: entry.device_id,
                            trail_name: trailName,
                            trail_id: trailId,
                            weeklyCount: trailId ? (trailCounts.get(trailId) || 0) : 0,
                            batteryStatus: entry.battery != null ? parseFloat(entry.battery) : null,
                            firmwareVersion: entry.firmware_version ?? null,
                            lastCallIn: formatDate(ts),
                        };
                    });

                    // Also include unassociated devices from DeviceMetadata that have never called in
                    const metadataOnlyRows = devices
                        .filter((d: any) => (!d.current_trail_id || d.current_trail_id === 0) && !callLogDeviceIds.has(d.device_id))
                        .map((d: any) => ({
                            device_id: d.device_id,
                            trail_name: null,
                            trail_id: null,
                            weeklyCount: 0,
                            batteryStatus: d.battery != null ? parseFloat(d.battery) : null,
                            firmwareVersion: null,
                            lastCallIn: null,
                        }));

                    // Unassociated devices first, then associated; alphabetical within each group
                    const listData = [...callLogRows, ...metadataOnlyRows].sort((a, b) => {
                        if (!a.trail_name && b.trail_name) return -1;
                        if (a.trail_name && !b.trail_name) return 1;
                        return a.device_id.localeCompare(b.device_id);
                    });

                    setDeviceListData(listData);
                    setLoadingListData(false);
                    isFetchingListData.current = false;
                } catch (error) {
                    console.error("Error loading device list data:", error);
                    setDeviceListData([]);
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
                <div className="dashboard-toolbar">
                    <button
                        className="action-button toggle-button"
                        type="button"
                        onClick={toggleView}
                    >
                        {viewMode === "graph"
                            ? "Device View"
                            : "Switch to Graph View"}
                    </button>
                    <div className="dashboard-toolbar-actions">
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
                            Add Area
                        </button>
                        <button
                            className="action-button"
                            type="button"
                            onClick={handleEditGroup}
                        >
                            Edit Area
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
                    <div className="graph-wrapper">
                        {loadingChart && (
                            <div className="loading-overlay">
                                <div className="loading-spinner" />
                            </div>
                        )}
                        <Plot
                            className="graph"
                            useResizeHandler
                            style={{ width: "100%", height: "700px" }}
                            config={{ displayModeBar: false, responsive: true }}
                            data={aggregate && graphLines.length > 0
                                ? [{
                                    x: graphLines[0].x,
                                    y: graphLines[0].y.map((_, i) =>
                                        graphLines.reduce((sum, line) => sum + (line.y[i] ?? 0), 0)
                                    ),
                                    type: "scatter" as const,
                                    mode: "lines+markers" as const,
                                    name: "Combined",
                                    marker: { color: "#6a9e5e" },
                                }]
                                : graphLines.map((line, index) => ({
                                    x: line.x,
                                    y: line.y,
                                    type: "scatter" as const,
                                    mode: "lines+markers" as const,
                                    name: line.name,
                                    marker: {
                                        color: [
                                            "#6a9e5e",
                                            "#c87941",
                                            "#5b8db8",
                                            "#c4a040",
                                            "#8b6b4a",
                                            "#5b9e8a",
                                            "#7b5ea7",
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
                                autosize: true,
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
                            <div className="data-error-banner">
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
                                <label className="aggregate-label">
                                    <input
                                        type="checkbox"
                                        className="aggregate-checkbox"
                                        checked={aggregate}
                                        onChange={(e) => setAggregate(e.target.checked)}
                                    />
                                    Aggregate
                                </label>
                            </div>
                            <div className="filter-group">
                                <label>Trail:</label>
                                <TrailSelector
                                    onChange={handleTrailChange}
                                    onGroupChange={setSelectedGroupName}
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
                    <div className="device-view">
                        <h2 className="device-view-title">Device Status Overview</h2>
                        <div className="device-filter-container">
                            <input
                                type="text"
                                className="device-filter-input"
                                placeholder="Filter by device ID…"
                                value={deviceFilter}
                                onChange={e => setDeviceFilter(e.target.value)}
                            />
                        </div>
                        {loadingListData ? (
                            <div className="device-view-loading">
                                Loading trail data...
                            </div>
                        ) : (
                            <div className="device-table-wrapper">
                                <table className="device-table">
                                    <thead>
                                        <tr className="device-table-header">
                                            {["Device ID", "Associated Trail", "Weekly Count", "Firmware", "Battery", "Last Call-in"].map((h) => (
                                                <th key={h}>{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {deviceListData.length === 0 ? (
                                            <tr className="device-table-empty">
                                                <td colSpan={6}>No devices found</td>
                                            </tr>
                                        ) : (
                                            deviceListData.filter(d => !deviceFilter || d.device_id.toLowerCase().includes(deviceFilter.toLowerCase())).map((device, index) => {
                                                const na = <span className="device-na">N/A</span>;
                                                const cell = (content: React.ReactNode) => <td>{content}</td>;
                                                const batteryClass = device.batteryStatus !== null
                                                    ? device.batteryStatus > 50 ? "battery-high" : device.batteryStatus > 20 ? "battery-medium" : "battery-low"
                                                    : "";
                                                return (
                                                    <tr
                                                        key={device.device_id}
                                                        className={index % 2 === 0 ? "device-table-row-even" : "device-table-row-odd"}
                                                    >
                                                        <td
                                                            className="device-id-cell"
                                                            onClick={() => setSelectedDeviceId(device.device_id)}
                                                        >
                                                            {device.device_id}
                                                        </td>
                                                        {device.trail_name && assigningDeviceId !== device.device_id ? (
                                                            <td className="device-trail-cell">
                                                                <span className="device-trail-label">{device.trail_name}</span>
                                                                <button
                                                                    className="device-edit-btn"
                                                                    onClick={() => { setAssigningDeviceId(device.device_id); setAssignTrailId(device.trail_id ?? 0); }}
                                                                >✎</button>
                                                            </td>
                                                        ) : (
                                                            <td className="device-trail-cell">
                                                                {assigningDeviceId === device.device_id ? (
                                                                    <div className="device-assign-form">
                                                                        <select
                                                                            className="device-assign-select"
                                                                            value={assignTrailId}
                                                                            onChange={e => setAssignTrailId(Number(e.target.value))}
                                                                        >
                                                                            <option value={0}>Select trail…</option>
                                                                            {(() => {
                                                                                const assignedTrailIds = new Set(
                                                                                    deviceListData
                                                                                        .filter(d => d.trail_id && d.device_id !== device.device_id)
                                                                                        .map(d => d.trail_id)
                                                                                );
                                                                                return trailMetadata
                                                                                    .filter(t => t.trail_id && t.trail_name && !assignedTrailIds.has(t.trail_id))
                                                                                    .map(t => (
                                                                                        <option key={t.trail_id} value={t.trail_id}>{t.trail_name}</option>
                                                                                    ));
                                                                            })()}
                                                                        </select>
                                                                        <button
                                                                            className="device-assign-btn"
                                                                            disabled={!assignTrailId}
                                                                            onClick={async () => {
                                                                                await updateDeviceTrailAssociation(device.device_id, assignTrailId);
                                                                                setAssigningDeviceId(null);
                                                                                setAssignTrailId(0);
                                                                                handleTrailUpdated();
                                                                            }}
                                                                        >Save</button>
                                                                        {device.trail_name && (
                                                                            <button
                                                                                className="device-unassign-btn"
                                                                                onClick={async () => {
                                                                                    await updateDeviceTrailAssociation(device.device_id, 0);
                                                                                    setAssigningDeviceId(null);
                                                                                    setAssignTrailId(0);
                                                                                    handleTrailUpdated();
                                                                                }}
                                                                            >Unassign</button>
                                                                        )}
                                                                        <button
                                                                            className="device-assign-btn"
                                                                            onClick={() => { setAssigningDeviceId(null); setAssignTrailId(0); }}
                                                                        >✕</button>
                                                                    </div>
                                                                ) : (
                                                                    <button
                                                                        className="device-assign-trail-btn"
                                                                        onClick={() => { setAssigningDeviceId(device.device_id); setAssignTrailId(0); }}
                                                                    >Assign Trail</button>
                                                                )}
                                                            </td>
                                                        )}
                                                        {cell(device.weeklyCount)}
                                                        {cell(device.firmwareVersion ?? na)}
                                                        {cell(device.batteryStatus !== null ? (
                                                            <span className={batteryClass}>
                                                                {device.batteryStatus}%
                                                            </span>
                                                        ) : na)}
                                                        {cell(device.lastCallIn ?? na)}
                                                    </tr>
                                                );
                                            })
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
            <DeviceDetailModal
                deviceId={selectedDeviceId}
                onClose={() => setSelectedDeviceId(null)}
            />
        </body>
    );
};

export default dashboard;
