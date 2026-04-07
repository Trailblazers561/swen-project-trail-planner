import React, { useState, useEffect, useMemo, useRef } from "react";
import EditTrailModal from "./components/EditTrailModal";
import EditTrailGroupModal from "./components/EditTrailGroupModal";
import AssociateDeviceModal from "./components/AssociateDeviceModal";
import TrailStatusTable from "./components/TrailDataTable.tsx";
import "./styles/dashboard.css";
import Plot from "react-plotly.js";
import type { Layout } from "plotly.js";
import {Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue} from "./components/ui/select.tsx";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
import { useNavigate } from "react-router-dom";
import { DatePickerWithRange } from "./components/ui/daterangepicker.tsx";
import { DateRange } from "node_modules/react-day-picker/dist/esm/types/shared";
import { MultiSelect, MultiSelectOption } from "./components/ui/multi-select.tsx";
import { Button } from "./components/ui/button.tsx";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import Navbar from "./components/Navbar.tsx";
import { Granularity, GranularityText } from "./lib/apiTypes";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select.tsx";
import { Loader2, Check } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";


interface Trail {
    id: number;
    name: string;
}

interface TrailGroup {
    name: string;
    trail_ids: number[];
}


const dashboard = () => {

    const {
        getTrailLogs,
        getDeviceMetadata,
        getTrailMetadata,
        getTrailGroupMetadata,
        exportCSV
    } = TrailData();

    const [trailMetadata, setTrailMetadata] = useState<Trail[]>([]);
    const [trailGroups, setTrailGroups] = useState<TrailGroup[]>([]);
    const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
    const [selectedTrails, setSelectedTrails] = useState<string[]>([]);

    // Build trail map from metadata - updates automatically when metadata changes
    const trailMap = useMemo<Record<string, number>>(() => {
        const map: Record<string, number> = { "All Trails": 0 };
        trailMetadata
            .filter((t) => t && t.name && t.name.trim().length > 0)
            .forEach((trail: Trail) => {
                map[trail.name] = trail.id;
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

    // Auto-select one year ago as start date
    const [selectedDate, setSelectedDate] = useState<Date | null>(
        (() => {
            const now = new Date();
            const lastYear = new Date(now);
            lastYear.setFullYear(now.getFullYear() - 1);
            return lastYear;
        })()
    );
    const [selectedDateEnd, setSelectedDateEnd] = useState<Date | null>(
        new Date()
    );
    
    const [range, setRange] = React.useState<DateRange | undefined>(undefined)
    const [trails, setTrails] = useState<string[]>([]);
    
    const [granularity, setGranularity] = useState<Granularity | null>(null);
    const [granularityOptions, setGranularityOptions] = useState<Granularity[]>([]);
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
            device_id: number;
        }>
    >([]);
    const [loadingListData, setLoadingListData] = useState(false);
    const [deviceMetadataCache, setDeviceMetadataCache] = useState<any[] | null>(
        null
    );
    const isFetchingListData = useRef(false);
    const [isDownloadingStatus, setIsDownloadingStatus] = useState<"idle" | "downloading" | "done" | "error"> ("idle");


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
                getTrailGroupMetadata(),
            ]);

            if (metadataResponse.success && groupsResponse.success) {
                const metadata = await metadataResponse.json;
                const groups = await groupsResponse.json;

                // Filter out any invalid entries
                const validMetadata = (metadata || []).filter(
                    (t: Trail) =>
                        t &&
                        t.id !== undefined &&
                        t.name &&
                        t.name.trim().length > 0
                );
                // Filter out invalid groups and empty groups (groups with no trails)
                const validGroups = (groups || []).filter(
                    (g: TrailGroup) =>
                        g &&
                        g.name &&
                        g.name.trim().length > 0 &&
                        g.trail_ids &&
                        Array.isArray(g.trail_ids) &&
                        g.trail_ids.length > 0
                );

                setTrailMetadata(validMetadata);
                setTrailGroups(validGroups);
            }
        } catch (error) {
            console.error("Error loading trail data:", error);
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

    const handleExportData = async() => {
        setIsDownloadingStatus("downloading");
        let trailList = [];
        for (let i = 0; i < trailListData.length; i++) {
            trailList.push(trailListData[i].trail_id)
        }
        if (selectedDate === null) {
            console.error("Error exporting: startDate must not be null");
            return;
        }
        if (selectedDateEnd === null) {
            console.error("Error exporting: endDate must not be null");
            return;
        }
        
        try{
            const csv_url = (await exportCSV(trailList, selectedDate, selectedDateEnd))["json"]["url"];
            window.open(csv_url, "_self");
            setIsDownloadingStatus("done");
        } catch (error) {
            console.error("Download failed:", error);
            setIsDownloadingStatus("error");
        } finally {
            setTimeout(() => setIsDownloadingStatus("idle"), 1000);
        }
     }


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

        let options: Granularity[] = [];
        if (daysDiff >= 1825) {
            options = [Granularity.Year, Granularity.Month];
        } else if (daysDiff >= 730) {
            options = [Granularity.Year, Granularity.Month, Granularity.Week, Granularity.Day];
        } else if (daysDiff >= 60) {
            options = [Granularity.Month, Granularity.Week, Granularity.Day];
        } else if (daysDiff >= 30) {
            options = [Granularity.Week, Granularity.Day];
        } else if (daysDiff >= 7) {
            options = [Granularity.Day];
        } else if (daysDiff <= 3) {
            options = [Granularity.Day, Granularity.Hour];
        } else {
            options = [Granularity.Day];
        }

        setGranularityOptions(options);
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

    function getDateRanges(
        startDate: Date,
        endDate: Date,
        granularity: Granularity = Granularity.Day
    ): { start: Date; end: Date }[] {
        let ranges: { start: Date; end: Date }[] = [];
        let current: Date = new Date(startDate);
        let end: Date = new Date(endDate);

        while (current < end) {
            let next: Date = new Date(current);
            if (granularity === Granularity.Hour) {
                next.setHours(next.getHours() + 1);
            } else if (granularity === Granularity.Day) {
                next.setDate(next.getDate() + 1);
            } else if (granularity === Granularity.Week) {
                next.setDate(next.getDate() + 7);
            } else if (granularity === Granularity.Month) {
                next.setMonth(next.getMonth() + 1);
            } else if (granularity === Granularity.Year) {
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
        events: {start: Date, count: number}[]
    ): Map<Date, number> {
        let occurrences = new Map<Date, number>();

        for (let range of ranges) {
            const eventInRange = events.find(
                (event) => event.start >= range.start && event.start < range.end
            );
    
            if (eventInRange) 
                occurrences.set(range.start, eventInRange.count); // Can change range.start to eventInRange.start to make it have the correct start, but the other points are still messed up
            else 
                occurrences.set(range.start, 0);
        }
        return occurrences;
    }

    async function getResponse(
        startDate: Date,
        endDate: Date,
        trails: string[],
        granularity: Granularity = Granularity.Day
    ) {
        if (!startDate || !endDate || !granularity || trails.length === 0) return;

        try {
            let trailIds: number[] = [];
            let includesAllTrails = trails.includes("All Trails");

            if (includesAllTrails) {
                trailIds = trailMetadata
                    .filter((t) => t && t.id && t.id !== 0)
                    .map((t) => t.id);
            } else {
                for (var i = 0; i < trails.length; i++) {
                    const trailId = trailMap[trails[i]];
                    if (trailId !== undefined) {
                        trailIds.push(trailId);
                    }
                }
            }

            if (trailIds.length === 0 && !includesAllTrails) return;

            const response = await getTrailLogs(
                trailIds,
                startDate,
                endDate,
                granularity
            );

            const responseJson = await response.json;

            let ranges = getDateRanges(startDate, endDate, granularity);
            let events: Map<number, {start: Date, count: number}[]> = new Map<number, {start: Date, count: number}[]>();

            (responseJson as { trail_id: number; start: number, count: number }[]).forEach(
                (entry) => {
                    if (!events.has(entry.trail_id)) {
                        events.set(entry.trail_id, []);
                    }
                    events.get(entry.trail_id)!.push({start: new Date(entry.start * 1000), count: entry.count});
                }
            );

            var lines: { name: string; x: Date[]; y: number[] }[] = [];

            const trailIdToName = new Map<number, string>();
            trailMetadata
                .filter((t) => t && t.name)
                .forEach((trail: Trail) => {
                    trailIdToName.set(trail.id, trail.name);
                });

            if (includesAllTrails) {
                events.forEach((dateCountArray, trailId) => {
                    if (trailId !== 0 && dateCountArray.length > 0) {
                        const trailName = trailIdToName.get(trailId) || `Trail ${trailId}`;
                        const occurrences = countOccurrencesInRanges(ranges, dateCountArray);
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

                    const dateCountArray: {start: Date, count: number}[] = events.get(trailId) ?? [];
                    if (dateCountArray.length === 0) continue;

                    const occurrences = countOccurrencesInRanges(ranges, dateCountArray);
                    const xData = Array.from(occurrences.keys());
                    const yData = Array.from(occurrences.values());

                    lines.push({ name: trailName, x: xData, y: yData });
                }
            }
            setGraphLines(lines);
            setGraphTitle(formatGraphTitle(startDate, endDate, trails));
        } catch (error) {
            console.error("Error fetching trail data:", error);
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

    const handleDateRangeChange = (DateRange: DateRange | undefined) => {
        const formattedRange: DateRange | undefined = DateRange?.from && DateRange?.to ? {from: DateRange.from, to: DateRange.to,} : undefined
        setRange(formattedRange)
        setSelectedDate(DateRange?.from ?? null);
        setSelectedDateEnd(DateRange?.to ?? null);
        handleStartDateChange(DateRange?.from ?? null);
        handleEndDateChange(DateRange?.to ?? null);

    if (!DateRange?.from || !DateRange?.to) return

    updateGranularityOptions(DateRange.from, DateRange.to)

    }

    const handleTrailChange = (selectedTrails: string[]) => {
        setTrails(selectedTrails);

        if (selectedTrails.length === 0) {
            setGraphLines([]);
            setGraphTitle("No Trails Selected");
            return;
        }
    };

    const handleTrailGroupChange = (groupNames: string[]) => {
        setSelectedGroups(groupNames);

        const selectedGroupObjects = trailGroups.filter(group =>
            groupNames.includes(group.name)
        );

        let autoSelectedTrails: string[] = [];

        if (groupNames.includes("All Areas")) {
            autoSelectedTrails = ["All Trails"];
        } else {
            autoSelectedTrails = selectedGroupObjects.flatMap(group =>
                group.trail_ids
                    .map(id => trailMetadata.find(t => t.id === id))
                    .filter((t): t is Trail => t !== undefined)
                    .map(trail => trail.name)
            );
        }

        // remove duplicates
        autoSelectedTrails = [...new Set(autoSelectedTrails)];

        setSelectedTrails(autoSelectedTrails);
    };

     const fillTrailsMultiselect = (): MultiSelectOption[] => {
        const options: MultiSelectOption[] = [
            { value: "All Trails", label: "All Trails" },
        ];

        trailMetadata.forEach((trail) => {
            if (trail && trail.name && trail.name.trim().length > 0) {
                options.push({ value: trail.name, label: trail.name });
            }
        });

        return options;
    };

    const fillTrailGroupsMultiselect = (): MultiSelectOption[] => {
        const options: MultiSelectOption[] = [];

        trailGroups.forEach((group) => {
            if (group && group.name && group.name.trim().length > 0) {
                options.push({ value: group.name, label: group.name });
            }
        });

        return options;
    };

    const handleGranularityChange = (granularity: Granularity) => {
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

                    // Get all trail IDs
                    const trailIds = trailMetadata
                        .filter((t) => t && t.id && t.id !== 0)
                        .map((t) => t.id);

                    if (trailIds.length === 0) {
                        setTrailListData([]);
                        setLoadingListData(false);
                        isFetchingListData.current = false;
                        return;
                    }

                    // Fetch weekly counts
                    const logsResponse = await getTrailLogs(
                        trailIds,
                        oneWeekAgo,
                        now,
                        Granularity.Day
                    );
                    const logs = logsResponse.success ? await logsResponse.json : [];
                    const devices = deviceMetadataCache || [];

                    // Count logs per trail for the week
                    const deviceCounts = new Map<number, number>();

                    logs.forEach((log: { device_id: number, count: number }) => {
                        const deviceId = log.device_id;
                        deviceCounts.set(deviceId, (deviceCounts.get(deviceId) || 0) + log.count);
                    });

                    const listData = devices
                    .filter((d) => d && d.name && d.id && d.id !== 0)
                    .map((device) => {
                        const weeklyCount = deviceCounts.get(device.id) || 0;
                        const trail = trailMetadata.find(trail => trail.id === device.current_trail_id);
                        let trailName = trail ? trail.name : ""
                        const lastUpdateTimestamp = device.last_updated ?? null;

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
                            trail_id: device.current_trail_id,
                            trail_name: trailName,
                            weeklyCount,
                            batteryStatus: device.battery,
                            lastUpdated,
                            device_id: device.id
                        }
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

    //
    function getPlotLayout(lines: any[]): Partial<Layout> {

    return {   
        margin: { l: 60, r: 30, t: 20, b: 60 },
        plot_bgcolor: "white",
        paper_bgcolor: "white",

        xaxis: {
            type: "date",
            title: {
                text: "Date",
                font: { size: 14, color: "#6b7280" },
            },
            showgrid: false,
            zeroline: false,
            tickfont: { size: 12 },
        },

        yaxis: {
            title: {
              text: "Hikers",
              font: { size: 14, color: "#6b7280" },
            },
            showgrid: false,
            zeroline: false,
            tickfont: { size: 12 },
            rangemode: "tozero",
        },

        shapes: generateVerticalBands(lines),

        legend: {
        orientation: "h",
        y: -0.25,
        x: 0.5,
        xanchor: "center",
        },
    };
    }

    //Makes graph columns have alternating colors
    function generateVerticalBands(lines: any[]): NonNullable<Layout["shapes"]> { 
        const shapes: NonNullable<Layout["shapes"]> = [];
        
        if (!lines.length || !lines[0].x?.length) return shapes;

        const xValues: Date[] = lines[0].x;

        for (let i = 0; i < xValues.length - 1; i++) {
            if (i % 2 === 0) {
                shapes.push({
                    type: "rect",
                    xref: "x",
                    yref: "paper",
                    x0: xValues[i],
                    x1: xValues[i + 1],
                    y0: 0,
                    y1: 1,
                    fillcolor: "rgba(0,0,0,0.04)",
                    line: { width: 0 },
                    layer: "below",
                });
            }
        }

        return shapes;
    }

    return (
        <div>
            <Navbar />
        <div className="flex flex-col">
            <div className="filter-container flex flex-row gap-6 px-6 py-4 items-end">
                <div className="filter-group flex flex-col">

                    <label>Date Range:</label>
                    <DatePickerWithRange value={range} onChange={handleDateRangeChange} />
                </div>
                <div className="filter-group flex flex-col">
                    <label>Granularity:</label>
                    <Select value={granularity ?? undefined}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="Select an option" />
                    </SelectTrigger>

                    <SelectContent>
                        <SelectGroup>
                        {granularityOptions.map((option) => (
                            <SelectItem key={option} value={option}>
                            {GranularityText[option]}
                            </SelectItem>
                        ))}
                        </SelectGroup>
                    </SelectContent>
                    </Select>
                </div>
                <div className="filter-group flex flex-col">

                    <label>Trails:</label>
                    <MultiSelect options={fillTrailsMultiselect()} onValueChange={handleTrailChange} value={selectedTrails} />

                </div>
                <div className="filter-group flex flex-col">

                    <label>Trail Groups:</label>
                    <MultiSelect options={fillTrailGroupsMultiselect()} onValueChange={handleTrailGroupChange} value={selectedGroups} />

                </div>
                <div className="options-container flex flex-col">
                    <label className="">Additional Options:</label>
                    <div className="flex flex-row gap-2">
                        <Button variant="secondary" onClick={handleAssociateDevice} >Associate Device</Button>
                        <Popover>
                            <PopoverTrigger asChild>
                                <Button variant="secondary" onClick={handleExportData}>
                                    Export Data
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                                {isDownloadingStatus === "downloading" && (
                                    <div>
                                        <Loader2 className="animate-spin" />
                                        <span>Downloading...</span>
                                    </div>
                                )}
                                {isDownloadingStatus === "done" && (
                                    <div>
                                        <Check/>
                                        <span>Downloaded</span>
                                    </div>
                                )}
                            </PopoverContent>
                        </Popover>
                        <Button variant="secondary">Import Data</Button>
                    </div>
                </div>
            </div>
        </div>
            <div className="w-full border-t bg-gray-50">
                <div className="max-w-6xl mx-auto px-2 py-0.5 flex-col rounded-b-lg">
                    <div className="flex p-2.5 justify-between items-center">
                        <Button variant="primary" onClick={toggleView} className="items-center" >Toggle View</Button>
                        <div className="flex gap-2.5">
                            <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="primary">Trail Options</Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                                <DropdownMenuGroup>
                                <DropdownMenuItem onClick={handleAddTrail}>Add Trail</DropdownMenuItem>
                                <DropdownMenuItem onClick={handleEditTrail}>Edit Trail Info</DropdownMenuItem>
                                </DropdownMenuGroup>
                            </DropdownMenuContent>
                            </DropdownMenu>

                            <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="primary">Trail Group Options</Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                                <DropdownMenuGroup>
                                <DropdownMenuItem onClick={handleAddGroup}>Add Group</DropdownMenuItem>
                                <DropdownMenuItem onClick={handleEditGroup}>Edit Group</DropdownMenuItem>
                                </DropdownMenuGroup>
                            </DropdownMenuContent>
                            </DropdownMenu>
                        </div>
                    </div>
                </div>
                <div className="w-full pb-8 bg-gray-50">
                    <div className="w-full border-t border-gray-200">
                        {viewMode === "graph" ? (
                        <div className="w-full h-[65vh] min-h-[400px]">
                            <div className="text-lg font-semibold text-gray-800 mb-4 pt-4">
                                {graphTitle}
                            </div>
                            <Plot 
                                className="w-full h-full"
                                config={{ displayModeBar: false, responsive: true }}
                                useResizeHandler={true}
                                style={{ width: "100%", height: "100%" }}
                                data={graphLines.map((line) => ({
                                    x: line.x.map(d => d.toISOString()),
                                    y: line.y,
                                    type: "scatter",
                                    mode: "lines+markers",
                                    name: line.name,
                                    line: {
                                        width: 3,
                                    },
                                    marker: {
                                        size: 6,
                                    },
                                }))}
                                layout={getPlotLayout(graphLines)}
                            />
                        </div>
                        ) : (
                            <div className="pt-4">
                                <h2 className="text-[26px] mb-[18px] text-gray-900">Trail Status Overview</h2>
                                    <TrailStatusTable
                                        data={trailListData}
                                        loading={loadingListData}
                                    />
                            </div>
                        )}
                    </div>
                </div>
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
    </div>
    );
};

export default dashboard;
