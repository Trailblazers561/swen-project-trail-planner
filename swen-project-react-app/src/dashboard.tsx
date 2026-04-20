import React, { useState, useEffect, useMemo, useRef } from "react";
import EditTrailModal from "./components/EditTrailModal";
import EditTrailGroupModal from "./components/EditTrailGroupModal";
import AssociateDeviceModal from "./components/AssociateDeviceModal";
import TrailStatusTable from "./components/TrailDataTable.tsx";
import "./styles/dashboard.css";
import Plot from "react-plotly.js";
import type { Layout } from "plotly.js";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select.tsx";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
import { DatePickerWithRange } from "./components/ui/daterangepicker.tsx";
import { DateRange } from "node_modules/react-day-picker/dist/esm/types/shared";
import { MultiSelect, MultiSelectOption, MultiSelectGroup, MultiSelectRef } from "./components/ui/multi-select.tsx";
import { Button } from "./components/ui/button.tsx";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Navbar from "./components/Navbar.tsx";
import { Granularity, GranularityText } from "./lib/apiTypes";
import { Loader2, Check } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Role, useAuth } from "@/Context";
import moment from "moment-timezone";

interface Trail {
    id: number;
    name: string;
}

interface TrailGroup {
    name: string;
    trail_ids: number[];
}

interface Line {
    trail_name: string;
    startDate: Date[];
    endDate: Date[];
    count: number[];
    granularity: Granularity;
}

const dashboard = () => {

    const { currentRole } = useAuth();
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

    // Build trail map from metadata - updates automatically when metadata changes
    const trailMap = useMemo<Record<string, number>>(() => {
        const map: Record<string, number> = {};
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

    const [graphLines, setGraphLines] = useState<Line[]>([]);

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

    const [range, setRange] = React.useState<DateRange | undefined>({ from: selectedDate ?? undefined, to: selectedDateEnd ?? undefined })
    const [trails, setTrails] = useState<string[]>([]);

    const [granularity, setGranularity] = useState<Granularity>(Granularity.Month);
    const [granularityOptions, setGranularityOptions] = useState<Granularity[]>([]);
    const [trailOptions, setTrailOptions] = useState<MultiSelectOption[] | MultiSelectGroup[]>([])
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
    const isFetchingListData = useRef(false);
    const [isDownloadingStatus, setIsDownloadingStatus] = useState<"idle" | "downloading" | "done" | "error">("idle");

    const [graphUpdating, setGraphUpdating] = useState<boolean>(false);
    const graphUpdatingRef = useRef(0);

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
            const defaultTrails: string[] = [];
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

    const handleExportData = async () => {
        setIsDownloadingStatus("downloading");

        const trailList = trails.map(trail_name => trailMap[trail_name]);

        if (selectedDate === null) {
            console.error("Error exporting: startDate must not be null");
            return;
        }
        if (selectedDateEnd === null) {
            console.error("Error exporting: endDate must not be null");
            return;
        }
        
        try{
            const csv_url = (await exportCSV(trailList, selectedDate, selectedDateEnd, granularity))["json"]["url"];
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
            const currentTrails = trails.length > 0 ? trails : [];
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
            options = [Granularity.Year, Granularity.Month, Granularity.Week];
        } else if (daysDiff >= 180) {
            options = [Granularity.Month, Granularity.Week];
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
        updateTrailsOptions();
    }, [trailMetadata, selectedGroups])

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
        const ranges: { start: Date; end: Date }[] = [];

        const startMoment = moment(startDate).tz("America/New_York");
        const endMoment = moment(endDate).tz("America/New_York");

        const getNextGranularitMoments = (m: moment.Moment): {end: moment.Moment, start: moment.Moment} => {
            const nextMoment = m.clone();
            switch (granularity) {
                case Granularity.Hour:
                    nextMoment.add(1, "hour");
                    break;
                case Granularity.Day:
                    nextMoment.add(1, "day");
                    break;
                case Granularity.Week:
                    nextMoment.add(1, "week").startOf("isoWeek");
                    break;
                case Granularity.Month:
                    nextMoment.add(1, "month").startOf("month");
                    break;
                case Granularity.Year:
                    nextMoment.add(1, "year").startOf("year");
                    break;
            }

            const endMoment = nextMoment.clone();
            if (granularity === Granularity.Hour)
                endMoment.subtract(1, "minute");
            else 
            endMoment.subtract(1, "hour");

            return {start: nextMoment, end: endMoment};
        };

        let currentStart = startMoment.clone();

        let currentEnd: moment.Moment;
        let nextStart;

        while (currentStart.isSameOrBefore(endMoment)) {
            const nextGranularityMoments = getNextGranularitMoments(currentStart);
            currentEnd = nextGranularityMoments.end;
            nextStart = nextGranularityMoments.start;
            if (currentEnd.isAfter(endMoment))
                currentEnd = endMoment.clone();

            ranges.push({start: currentStart.toDate(), end: currentEnd.toDate()});
            currentStart = nextStart;
        }

        return ranges;
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

            for (var i = 0; i < trails.length; i++) {
                const trailId = trailMap[trails[i]];
                if (trailId !== undefined) {
                    trailIds.push(trailId);
                }
            }

            if (trailIds.length === 0) return;

            const responseGraphRef = ++graphUpdatingRef.current;
            setGraphUpdating(true);

            const response = await getTrailLogs(
                trailIds,
                startDate,
                endDate,
                granularity
            );

            const responseJson = await response.json;

            let ranges = getDateRanges(startDate, endDate, granularity);
            let events: Map<number, { start: Date, count: number }[]> = new Map<number, { start: Date, count: number }[]>();

            (responseJson as { trail_id: number; start: number, count: number }[]).forEach(
                (entry) => {
                    if (!events.has(entry.trail_id)) {
                        events.set(entry.trail_id, []);
                    }
                    events.get(entry.trail_id)!.push({ start: new Date(entry.start * 1000), count: entry.count });
                }
            );

            var lines: { trail_name: string; startDate: Date[]; endDate: Date[]; count: number[]; granularity: Granularity }[] = [];

            const trailIdToName = new Map<number, string>();
            trailMetadata
                .filter((t) => t && t.name)
                .forEach((trail: Trail) => {
                    trailIdToName.set(trail.id, trail.name);
                });

            for (let i = 0; i < trails.length; i++) {
                const trailName = trails[i];
                const trailId = trailMap[trailName];
                if (trailId === undefined) continue;

                const dateCountArray: { start: Date, count: number }[] = events.get(trailId) ?? [];

                let dateMap = new Map<Date, Date>();
                let countMap = new Map<Date, number>();

                for (let range of ranges) {
                    const eventsInRange = dateCountArray.filter(
                        (event) => (event.start >= range.start && event.start < range.end) || (event.start.getTime() == range.start.getTime())
                    );

                    const totalCount = eventsInRange.reduce((sum, event) => sum + event.count, 0);

                    dateMap.set(range.start, range.end);
                    countMap.set(range.start, totalCount);
                }

                const startDates = Array.from(dateMap.keys());
                const endDates = Array.from(dateMap.values());
                const counts = Array.from(countMap.values());

                lines.push({ trail_name: trailName, startDate: startDates, endDate: endDates, count: counts, granularity: granularity });
            }

            setGraphLines(lines);
            setGraphTitle(formatGraphTitle(startDate, endDate, trails));

            if (responseGraphRef === graphUpdatingRef.current)
                setGraphUpdating(false);
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

        const startStr = moment(startDate).tz("America/New_York").format("M/D/YYYY");
        const endStr = moment(endDate).tz("America/New_York").format("M/D/YYYY");
        const includesAll = trails.length == trailMetadata.length

        if (includesAll) {
            return `All Trails from ${startStr} to ${endStr}`;
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

    const handleDateRangeChange = (range: DateRange | undefined) => {
        const timezoneRange: DateRange = {from: undefined, to: undefined};
        if (range?.from) {
            const userISO = moment(range.from).tz(Intl.DateTimeFormat().resolvedOptions().timeZone).format("YYYY-MM-DD");
            const newYorkOffset = moment(range.from).tz("America/New_York").format("Z");
            timezoneRange.from = new Date(`${userISO}T00:00:00${newYorkOffset}`);
        }
        if (range?.to) {
            const userISO = moment(range.to).tz(Intl.DateTimeFormat().resolvedOptions().timeZone).format("YYYY-MM-DD");
            const newYorkOffset = moment(range.to).tz("America/New_York").format("Z");
            timezoneRange.to = new Date(`${userISO}T23:00:00${newYorkOffset}`);
        }

        setRange(range);
        setSelectedDate(timezoneRange?.from ?? null);
        setSelectedDateEnd(timezoneRange?.to ?? null);
        handleStartDateChange(timezoneRange?.from ?? null);
        handleEndDateChange(timezoneRange?.to ?? null);

        if (!timezoneRange?.from || !timezoneRange?.to) return;

        updateGranularityOptions(timezoneRange.from, timezoneRange.to);
    }

    const handleTrailChange = (selectedTrails: string[]) => {
        setTrails(selectedTrails);

        if (selectedTrails.length === 0) {
            setGraphLines([]);
            setGraphTitle("No Trails Selected");
            return;
        }
    };

    const trailSelectRef = useRef<MultiSelectRef>(null);
    const updateTrailsOptions = () => {
        const availableTrails: string[] = [];
        if (selectedGroups.length === 0) {
            const options: MultiSelectOption[] = [];
            trailMetadata.forEach((trail) => {
                if (trail && trail.name && trail.name.trim().length > 0) {
                    options.push({ value: trail.name, label: trail.name });
                    availableTrails.push(trail.name);
                }
            });
            setTrailOptions(options);
        } else {
            const groups: MultiSelectGroup[] = [];
            const trailIdMap = new Map(trailMetadata.map(t => [t.id, t.name]));
            trailGroups.forEach((group) => {
                if (selectedGroups.includes(group.name)) {
                    const groupOptions = group.trail_ids.map((id) => trailIdMap.get(id)).filter((name) => name != undefined).map((name) => ({ label: name, value: name }));
                    if (groupOptions.length > 0)
                        groups.push({ heading: group.name, options: groupOptions });
                    availableTrails.push(...groupOptions.map(option => option.label))
                }
            })
            setTrailOptions(groups);
        }
        const trailValues = trailSelectRef.current?.getSelectedValues().filter(value => availableTrails.includes(value)) ?? []
        trailSelectRef.current?.setSelectedValues(trailValues)
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
                    const today = moment().tz("America/New_York").startOf("day").toDate();
                    const oneWeekAgo = moment().tz("America/New_York").startOf("day").subtract(7, "days").toDate();

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
                        today,
                        Granularity.Day
                    );
                    const logs = logsResponse.success ? await logsResponse.json : [];
                    const trails = trailMetadata || [];

                    // Count logs per trail for the week
                    const trailInformation = new Map<number, {count: number, battery: number, lastUpdatedTimestamp: number}>();

                    logs.forEach((log: { trail_id: number, device_id: number, count: number, battery: number, start: number}) => {
                        const trailId = log.trail_id;
                        const currentInformation = trailInformation.get(trailId) || {count: 0, battery: 0, lastUpdatedTimestamp: 0}
                        currentInformation.count += log.count;
                        currentInformation.battery = log.battery;
                        currentInformation.lastUpdatedTimestamp = log.start;
                        trailInformation.set(trailId, currentInformation);
                    });

                    const listData = trails
                    .filter((t) => t && t.name && t.id && t.id !== 0)
                    .map((trail) => {
                        const information = trailInformation.get(trail.id);
                        const lastUpdateTimestamp = information?.lastUpdatedTimestamp ?? null;

                        let lastUpdated: string | null = lastUpdateTimestamp ? moment(lastUpdateTimestamp * 1000).tz("America/New_York").format("MM/DD/YYYY") : null;

                        return {
                            trail_id: trail.id,
                            trail_name: trail.name,
                            weeklyCount: information?.count ?? 0,
                            batteryStatus: information?.battery ?? null,
                            lastUpdated: lastUpdated
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

    // Creates the Plotly Layout With Custom Ranges and Shapes
    function getPlotLayout(lines: Line[]): Partial<Layout> {

        return {
            margin: { l: 60, r: 30, t: 20, b: 60 },
            plot_bgcolor: "white",
            paper_bgcolor: "white",

            xaxis: {
                range: lines.length === 0 ? [selectedDate?.toISOString(), selectedDateEnd?.toISOString()] : undefined,
                type: "date",
                title: {
                    text: "Date",
                    font: { size: 14, color: "#6b7280" },
                },
                showgrid: false,
                zeroline: false,
                tickfont: { size: 12 },
                rangemode: "normal"
            },

            yaxis: {
                range: lines.length === 0 ? [0, 100] : undefined,
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

    // Makes graph columns have alternating colors
    function generateVerticalBands(lines: Line[]): NonNullable<Layout["shapes"]> {
        const shapes: NonNullable<Layout["shapes"]> = [];
        let dates;
        if (!lines.length || !lines[0].startDate?.length) {
            if (!selectedDate || !selectedDateEnd)
                return shapes;
            dates = getDateRanges(selectedDate, selectedDateEnd, granularity).map(d => d.start.toISOString())
        } else {
            dates = lines[0].startDate.map(d => d.toISOString());
        }

        for (let i = 0; i < dates.length - 1; i++) {
            if (i % 2 === 0) {
                shapes.push({
                    type: "rect",
                    xref: "x",
                    yref: "paper",
                    x0: dates[i],
                    x1: dates[i + 1],
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
        <div data-testid="dashboard-root">
            <Navbar />
            <div className="flex flex-col">
                <div className="filter-container flex w-full justify-between items-end px-6 py-2">
                    <div className="flex gap-8 items-start flex-wrap">
                        <div className="flex gap-2">
                            <div className="filter-group flex flex-col">

                                <label>Date Range:</label>
                                <DatePickerWithRange value={range} onChange={handleDateRangeChange} />
                            </div>
                            <div className="filter-group flex flex-col">
                                <label>Granularity:</label>
                                <Select value={granularity} onValueChange={(value) => setGranularity(value as Granularity)}>
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
                        </div>
                        <div className="filter-group flex flex-col">
                            <label>Granularity:</label>
                            <Select value={granularity}  onValueChange={(value) => setGranularity(value as Granularity)}>
                            <SelectTrigger className="w-[150px]" data-testid="granularity-select">
                                <SelectValue placeholder="Select an option" data-testid="selected-granularity-option"/>
                            </SelectTrigger>

                            <SelectContent>
                                <SelectGroup>
                                {granularityOptions.map((option) => (
                                    <SelectItem key={option} value={option} data-testid="granularity-option">
                                    {GranularityText[option]}
                                    </SelectItem>
                                ))}
                                </SelectGroup>
                            </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <div className="filter-group flex flex-col">

                        <label>Trails:</label>
                        <MultiSelect ref={trailSelectRef} options={trailOptions} onValueChange={handleTrailChange} value={trails} data-testid="trail-selector"/>

                        </div>
                        <div className="filter-group flex flex-col">

                        <label>Trail Groups:</label>
                        <MultiSelect options={fillTrailGroupsMultiselect()} onValueChange={setSelectedGroups} value={selectedGroups} data-testid="trail-group-selector" />

                        </div>
                    </div>
                    <div className="flex flex-col ml-auto">
                        <label>Additional Options:</label>
                        <div className="flex flex-row gap-2">
                            {(currentRole === null ) && (
                                <div>Please log in or register to view additional options.</div>
                            )}
                            {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                                <Button variant="secondary" onClick={handleAssociateDevice} data-testid="associate-device">Associate Device</Button>
                            )}
                            {currentRole !== null && (
                                <Popover open={isDownloadingStatus !== "idle"}>
                                    <PopoverTrigger asChild>
                                        <Button variant="secondary" onClick={handleExportData} disabled={isDownloadingStatus !== "idle"} data-testid="export-data">
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
                                                <Check />
                                                <span>Downloaded</span>
                                            </div>
                                        )}
                                    </PopoverContent>
                                </Popover>
                            )}
                            {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                                <Button variant="secondary" data-testid="import-data">Import Data</Button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            <div className="w-full border-t bg-gray-50">
                <div>
                    <div className="flex p-2.5 justify-between items-center">
                        <Button variant="primary" onClick={toggleView} className="items-center" data-testid="toggle-view">Toggle View</Button>
                            {viewMode === "graph" ? (
                                <div className="text-lg font-bold text-gray-800" data-testid="graph-title">
                                {graphTitle}
                            </div>
                        ) : (
                            <div className="text-lg font-bold text-gray-800">Trail Status Overview</div>
                        )}
                        <div className="flex gap-2.5">
                            {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="primary" data-testid="trail-options">Trail Options</Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent>
                                        <DropdownMenuGroup>
                                            <DropdownMenuItem onClick={handleAddTrail} data-testid="add-trail">Add Trail</DropdownMenuItem>
                                            <DropdownMenuItem onClick={handleEditTrail} data-testid="edit-trail">Edit Trail Info</DropdownMenuItem>
                                        </DropdownMenuGroup>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            )}
                            {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="primary" data-testid="trail-group-options">Trail Group Options</Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent>
                                        <DropdownMenuGroup>
                                            <DropdownMenuItem onClick={handleAddGroup} data-testid="add-trail-group">Add Group</DropdownMenuItem>
                                            <DropdownMenuItem onClick={handleEditGroup} data-testid="edit-trail-group">Edit Group</DropdownMenuItem>
                                        </DropdownMenuGroup>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            )}
                        </div>
                    </div>
                </div>
                <div className="w-full pb-8 bg-gray-50">
                    <div className="w-full border-t border-gray-200">
                        {viewMode === "graph" ? (
                        <div className="w-full h-[65vh] min-h-[400px]" data-testid="outer-dashboard-graph" data-graph-updating={graphUpdating}>
                            <Plot 
                                className="w-full h-full"
                                config={{ displayModeBar: false, responsive: true }}
                                useResizeHandler={true}
                                style={{ width: "100%", height: "100%" }}
                                data={graphLines.map((line) => ({
                                    x: line.startDate.map(d => d.toISOString()),
                                    y: line.count,
                                    type: "scatter",
                                    mode: "lines+markers",
                                    name: line.trail_name,
                                    line: {
                                        width: 3,
                                    },
                                    marker: {
                                        size: 6,
                                    },
                                    hovertemplate: line.count.map((count: number, i: number) => {
                                        const s = new Date(line.startDate[i]);
                                        const e = new Date(line.endDate[i]);
                                        const sString = moment(s).tz("America/New_York").format("MMM D");
                                        const sYear = moment(s).tz("America/New_York").format("YYYY");
                                        const eString = moment(e).tz("America/New_York").format("MMM D");
                                        const eYear = moment(e).tz("America/New_York").format("YYYY");
                                        const sHour = moment(s).tz("America/New_York").format("h:mm A");

                                        if (line.granularity === Granularity.Hour) {
                                            return `${sString} ${sHour} | Count: ${count}`;
                                        } else if (line.granularity === Granularity.Day) {
                                            return `${sString}, ${sYear} | Count: ${count}`;
                                        } else {
                                            return `${sString}, ${sYear} - ${eString}, ${eYear} | Count: ${count}`;
                                        }
                                      }),
                                }))}
                                layout={getPlotLayout(graphLines)}
                            />
                        </div>
                        ) : (
                            <div className="pt-4 m-4">
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
