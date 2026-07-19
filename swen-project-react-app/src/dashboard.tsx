import React, { useState, useEffect, useMemo, useRef } from "react";
import EditTrailModal from "./components/modals/EditTrailModal.tsx";
import EditAreaModal from "./components/modals/EditAreaModal.tsx";
import AssociateDeviceModal from "./components/modals/AssociateDeviceModal.tsx";
import TrailStatusTable from "./components/tables/TrailDataTable.tsx";
import "./styles/dashboard.css";
import Plot from "react-plotly.js";
import type { Layout, Data } from "plotly.js";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "./components/templates/select.tsx";
import "react-datepicker/dist/react-datepicker.css";
import { TrailData } from "./api";
import { DatePickerWithRange } from "./components/templates/daterangepicker.tsx";
import { DateRange } from "node_modules/react-day-picker/dist/esm/types/shared";
import { MultiSelect, MultiSelectOption, MultiSelectGroup, MultiSelectRef } from "./components/templates/multi-select.tsx";
import { Button } from "./components/templates/button.tsx";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/templates/dropdown-menu.tsx";
import { Granularity, GranularityText } from "./lib/apiTypes";
import { Loader2, Check, X } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/templates/popover.tsx";
import { fileOpen } from 'browser-fs-access';
import { useSearchParams } from "react-router-dom";
import { Role, useAuth } from "@/AuthContext.tsx";
import { useDate } from "@/DateContext.tsx"
import moment from "moment-timezone";

interface Trail {
    id: number;
    name: string;
    notes: string;
    latitude: number;
    longitude: number;
}

interface Area {
    name: string;
    trail_ids: number[];
}

interface Line {
    trail_name: string;
    startDates: Date[];
    endDates: Date[];
    counts: number[];
    noDatas: boolean[];
    granularity: Granularity;
}

interface TrailListItem {
    trail_id: number;
    trail_name: string;
    weeklyCount: number;
    batteryStatus: number | null;
    lastUpdated: string | null;
}

const dashboard = () => {

    const { currentRole } = useAuth();
    const { startDate, endDate, granularity, setStartDate, setEndDate, setGranularity } = useDate();
    const {
        getTrailLogs,
        getDeviceMetadata,
        getTrailMetadata,
        getAreaMetadata,
        exportCSV,
        importCSV,
    } = TrailData();

    const [trailMetadata, setTrailMetadata] = useState<Trail[]>([]);
    const [areas, setAreas] = useState<Area[]>([]);
    const [selectedAreas, setSelectedAreas] = useState<string[]>([]);

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
    const [isEditAreaModalOpen, setIsEditAreaModalOpen] = useState(false);
    const [isAddAreaModalOpen, setIsAddAreaModalOpen] = useState(false);
    const [isAssociateDeviceModalOpen, setIsAssociateDeviceModalOpen] =
        useState(false);

    const [graphLines, setGraphLines] = useState<Line[]>([]);

    const [range, setRange] = useState<DateRange | undefined>({ from: startDate ?? undefined, to: endDate ?? undefined })
    const [searchParams, setSearchParams] = useSearchParams();
    const trailName = searchParams.get("trailName");
    const [trails, setTrails] = useState<string[]>(trailName ? [trailName] : []);

    const [granularityOptions, setGranularityOptions] = useState<Granularity[]>([]);
    const [trailOptions, setTrailOptions] = useState<MultiSelectOption[] | MultiSelectGroup[]>([])
    const [areaOptions, setAreaOptions] = useState<MultiSelectOption[]>([])
    const [graphTitle, setGraphTitle] = useState<string>("No Trails Selected");
    const [graphBroken, setGraphBroken] = useState(false);
    const [hasDefaulted, setHasDefaulted] = useState(false);
    const [viewMode, setViewMode] = useState<"graph" | "list">("graph");
    const [allListData, setAllListData] = useState<Array<TrailListItem>>([]);
    const [trailListData, setTrailListData] = useState<Array<TrailListItem>>([]);
    const [loadingListData, setLoadingListData] = useState(false);
    const [deviceMetadataCache, setDeviceMetadataCache] = useState<any[] | null>(null);
    const isFetchingListData = useRef(false);
    const [isDownloadingStatus, setIsDownloadingStatus] = useState<"idle" | "downloading" | "done" | "error"> ("idle");
    const [isUploadingStatus, setIsUploadingStatus] = useState<"idle" | "uploading" | "done" | "error"> ("idle");


    const [graphUpdating, setGraphUpdating] = useState<boolean>(false);
    const graphUpdatingRef = useRef(0);

    // Load trail metadata and areas from database
    useEffect(() => {
        loadTrailData();
    }, []);

    // Default to "All Trails" when data is loaded and dates are set (only once)
    useEffect(() => {
        if (
            trailMetadata.length > 0 &&
            (trails.length === 0 || trails.length === 1) &&
            startDate &&
            endDate &&
            !hasDefaulted
        ) {
            setHasDefaulted(true);
            setSearchParams("");
            // Trigger graph load after a small delay to ensure state is set
            setTimeout(() => {
                if (granularity) {
                    getResponse(
                        startDate,
                        endDate,
                        trails,
                        granularity
                    );
                }
            }, 100);
        }
    }, [trailMetadata, startDate, endDate, granularity, hasDefaulted]);

    const loadTrailData = async () => {
        try {
            const [metadataResponse, areasResponse] = await Promise.all([
                getTrailMetadata(),
                getAreaMetadata(),
            ]);

            if (metadataResponse.success && areasResponse.success) {
                const metadata = await metadataResponse.json;
                const areas = await areasResponse.json;

                // Filter out any invalid entries
                const validMetadata = (metadata || []).filter(
                    (t: Trail) =>
                        t &&
                        t.id !== undefined &&
                        t.name &&
                        t.name.trim().length > 0
                );
                // Filter out invalid areas
                const validAreas = (areas || []).filter(
                    (a: Area) =>
                        a &&
                        a.name &&
                        a.name.trim().length > 0 &&
                        a.trail_ids &&
                        Array.isArray(a.trail_ids)
                );

                setTrailMetadata(validMetadata);
                setAreas(validAreas);
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

    const handleEditArea = () => {
        setIsEditAreaModalOpen(true);
    };

    const handleAddArea = () => {
        setIsAddAreaModalOpen(true);
    };

    const handleAssociateDevice = () => {
        setIsAssociateDeviceModalOpen(true);
    };

    const handleExportData = async () => {
        setIsDownloadingStatus("downloading");

        const trailList = trails.map(trail_name => trailMap[trail_name]);

        if (startDate === null) {
            console.error("Error exporting: startDate must not be null");
            return;
        }
        if (endDate === null) {
            console.error("Error exporting: endDate must not be null");
            return;
        }
        
        try{
            const response = await exportCSV(trailList, startDate, endDate, granularity);
            if (!response.success)
                throw new Error("Failed to export");

            const csv_url = (response)["json"]["url"];
            window.open(csv_url, "_self");
            setIsDownloadingStatus("done");
        } catch (error) {
            console.error("Download failed:", error);
            setIsDownloadingStatus("error");
        } finally {
            setTimeout(() => setIsDownloadingStatus("idle"), 1000);
        }
    }

    const handleImportData = async () => {
        try{
            setIsUploadingStatus("uploading");
            const file = await fileOpen();
            const response = await importCSV(file)

            if (response.success) {
                setIsUploadingStatus("done");
            } else {
                setIsUploadingStatus("error");
            }
        } catch (error) {
            setIsUploadingStatus("error");
        } finally {
            setTimeout(() => setIsUploadingStatus("idle"), 1000);
        }
     };

    const handleTrailUpdated = async () => {
        await loadTrailData();
        // Refresh graph - wait for state to update
        setTimeout(() => {
            const currentTrails = trails.length > 0 ? trails : [];
            if (startDate && endDate && granularity) {
                if (trails.length === 0) {
                    setTrails(currentTrails);
                }
                getResponse(startDate, endDate, currentTrails, granularity);
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
        if (!options.includes(granularity))
            setGranularity(options[0]);
    }

    useEffect(() => {
        updateGranularityOptions(startDate, endDate);
    }, [startDate, endDate]);

    useEffect(() => {
        updateTrailsOptions();
    }, [trailMetadata, selectedAreas])

    useEffect(() => {
        const areaNames = areas.map((area) => area.name);
        const areaValues = areaSelectRef.current?.getSelectedValues().filter(value => areaNames.includes(value)) ?? [];
        areaSelectRef.current?.setSelectedValues(areaValues)
        setAreaOptions(fillAreasMultiselect())
    }, [areas])

    useEffect(() => {
        if (startDate && endDate && trails.length > 0 && granularity) {
            getResponse(startDate, endDate, trails, granularity);
        }
    }, [startDate, endDate, trails, granularity]);

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
            if (!response.success)
                throw new Error("Failed to retrieve graph data");

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

            var lines: { trail_name: string; startDates: Date[]; endDates: Date[]; counts: number[]; noDatas: boolean[]; granularity: Granularity }[] = [];

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
                let noDataMap = new Map<Date, boolean>();

                for (let range of ranges) {
                    const eventsInRange = dateCountArray.filter(
                        (event) => (event.start >= range.start && event.start < range.end) || (event.start.getTime() == range.start.getTime())
                    );

                    const totalCount = eventsInRange.reduce((sum, event) => sum + event.count, 0);

                    dateMap.set(range.start, range.end);
                    countMap.set(range.start, totalCount);
                    noDataMap.set(range.start, eventsInRange.length === 0);
                }

                const startDates = Array.from(dateMap.keys());
                const endDates = Array.from(dateMap.values());
                const counts = Array.from(countMap.values());
                const noDatas = Array.from(noDataMap.values());

                lines.push({ trail_name: trailName, startDates: startDates, endDates: endDates, counts: counts, noDatas: noDatas, granularity: granularity });
            }

            if (responseGraphRef !== graphUpdatingRef.current)
                return;
            setGraphLines(lines);
            setGraphTitle(formatGraphTitle(startDate, endDate, trails));
            setGraphUpdating(false);
            setGraphBroken(false);
        } catch (error) {
            console.error("Error fetching trail data:", error);
            setGraphLines([]);
            setGraphTitle("");
            setGraphUpdating(false);
            setGraphBroken(true);
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

        if (selectedAreas.length === 1 && areas.find(a => a.name === selectedAreas[0])?.trail_ids.length === trails.length) {
            return `${selectedAreas[0]} from ${startStr} to ${endStr}`;
        } else if (includesAll) {
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
        setStartDate(startDate);
    };

    const handleEndDateChange = (endDate: Date | null) => {
        setEndDate(endDate);
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
        setStartDate(timezoneRange?.from ?? null);
        setEndDate(timezoneRange?.to ?? null);
        handleStartDateChange(timezoneRange?.from ?? null);
        handleEndDateChange(timezoneRange?.to ?? null);

        if (!timezoneRange?.from || !timezoneRange?.to) return;

        updateGranularityOptions(timezoneRange.from, timezoneRange.to);
    }

    const handleTrailChange = (selectedTrails: string[]) => {
        setTrails(selectedTrails);

        if (selectedTrails.length === 0) {
            ++graphUpdatingRef.current;
            setGraphLines([]);
            setGraphTitle("No Trails Selected");
            return;
        }
    };

    const handleAreaChange = (newSelectedAreas: string[]) => {
        const newAreas = newSelectedAreas.filter(area => !selectedAreas.includes(area));
        const trailValues = trails;
        const trailIdMap = new Map(trailMetadata.map(t => [t.id, t.name]));
        areas.forEach((area) => {
            if (newAreas.includes(area.name)) {
                area.trail_ids.forEach((id) => {
                    const trailName = trailIdMap.get(id);
                    if (trailName && !trailValues.includes(trailName))
                        trailValues.push(trailName)
                })
            }
        })
        if (trailMetadata.length !== 0)
            setTrailOptions(trailMetadata.map((trail) => ({value: trail.name, label: trail.name})));
        else
            setTrailOptions(trailValues.map((trail) => ({value: trail, label: trail})));
        trailSelectRef.current?.setSelectedValues(trailValues);
        if (selectedAreas.length !== 0 || newSelectedAreas.length !== 0)
            setSelectedAreas(newSelectedAreas);
    }

    const trailSelectRef = useRef<MultiSelectRef>(null);
    const updateTrailsOptions = () => {
        const availableTrails: string[] = [];
        if (selectedAreas.length === 0) {
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
            areas.forEach((area) => {
                if (selectedAreas.includes(area.name)) {
                    const areaOptions = area.trail_ids.map((id) => trailIdMap.get(id)).filter((name) => name != undefined).map((name) => ({ label: name, value: name }));
                    if (areaOptions.length > 0)
                        groups.push({ heading: area.name, options: areaOptions });
                    availableTrails.push(...areaOptions.map(option => option.label))
                }
            })
            setTrailOptions(groups);
        }

        const trailValues = trailSelectRef.current?.getSelectedValues().filter(value => availableTrails.includes(value)) ?? [];
        trailSelectRef.current?.setSelectedValues(trailValues);
    };

    const areaSelectRef = useRef<MultiSelectRef>(null);
    const fillAreasMultiselect = (): MultiSelectOption[] => {
        const options: MultiSelectOption[] = [];

        areas.forEach((area) => {
            if (area && area.name && area.name.trim().length > 0 && area.trail_ids && Array.isArray(area.trail_ids) && area.trail_ids.length > 0) {
                options.push({ value: area.name, label: area.name });
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
            trailMetadata.length > 0 &&
            deviceMetadataCache !== null &&
            !isFetchingListData.current
        ) {
            isFetchingListData.current = true;
            setLoadingListData(true);

            (async () => {
                try {
                    // Get last week's date range
                    const today = moment().tz("America/New_York").startOf("day").subtract(1, "second").toDate();
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

                    const deviceToBattery: Record<string, number> = {}
                    deviceMetadataCache.forEach(device => {
                        deviceToBattery[device.id] = device.battery;
                    })

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

                    logs.forEach((log: { trail_id: number, device_id: number, count: number, start: number}) => {
                        const trailId = log.trail_id;
                        const currentInformation = trailInformation.get(trailId) || {count: 0, battery: 0, lastUpdatedTimestamp: 0}
                        currentInformation.count += log.count;
                        currentInformation.battery = deviceToBattery[log.device_id];
                        currentInformation.lastUpdatedTimestamp = log.start;
                        trailInformation.set(trailId, currentInformation);
                    });

                    const allListData = trails
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

                    setAllListData(allListData);
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
    }, [trailMetadata, deviceMetadataCache]);

    // Update displayed list data to match trails variable
    useEffect(() => {
        if (
            viewMode === "list" &&
            allListData.length > 0 &&
            !isFetchingListData.current
        ) {
            if (trails.length == 0)
                setTrailListData(allListData);
            else
                setTrailListData(allListData.filter((item) => trails.includes(item.trail_name)));

        }
    }, [viewMode, trails, allListData]);

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
                range: lines.length === 0 ? [startDate?.toISOString(), endDate?.toISOString()] : undefined,
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

    function getPlotData(lines: Line[]): Data[] {
        const data: Data[] = [];
        // Enable this to display percentiles (update counts to use real percentiles)
        if (lines.length === 1 && false) {
            data.push({
                x: lines[0].startDates.map(d => d.toISOString()),
                y: lines[0].counts.map(c => c * 1.2),
                type: "scatter",
                mode: "lines",
                line: { width: 0 },
                hoverinfo: "skip",
                showlegend: false
            });
            data.push({
                x: lines[0].startDates.map(d => d.toISOString()),
                y: lines[0].counts.map(c => c * .8),
                type: "scatter",
                mode: "lines",
                line: { width: 0 },
                fill: "tonexty",
                fillcolor: "rgb(179, 205, 227)", // Pastel1 color (light blue)
                name: "25th-75th Percentile",
                hoverinfo: "skip"
            });
        }
        lines.forEach(line => {
            data.push({
                x: line.startDates.map(d => d.toISOString()),
                y: line.counts,
                type: "scatter",
                mode: "lines+markers",
                name: line.trail_name,
                line: {
                    width: 3,
                    color: line == lines[0] ? "#1F77B4" : undefined  // D3[0] default first line color
                },
                marker: {
                    size: 6,
                },
                hovertemplate: line.counts.map((count: number, i: number) => {
                    const s = new Date(line.startDates[i]);
                    const e = new Date(line.endDates[i]);
                    const sString = moment(s).tz("America/New_York").format("MMM D");
                    const sYear = moment(s).tz("America/New_York").format("YYYY");
                    const eString = moment(e).tz("America/New_York").format("MMM D");
                    const eYear = moment(e).tz("America/New_York").format("YYYY");
                    const sHour = moment(s).tz("America/New_York").format("h:mm A");

                    let dateString: string;
                    let countString: string;
                    if (line.granularity === Granularity.Hour) {
                        dateString = `${sString} ${sHour}`;
                    } else if (line.granularity === Granularity.Day) {
                        dateString = `${sString}, ${sYear}`;
                    } else {
                        dateString = `${sString}, ${sYear} - ${eString}, ${eYear}`;
                    }
                    countString = line.noDatas[i] ? "No Data" : `Count: ${count}`
                    return `${dateString} | ${countString}`
                  })
            });
        })
        return data;
    }

    // Makes graph columns have alternating colors
    function generateVerticalBands(lines: Line[]): NonNullable<Layout["shapes"]> {
        const shapes: NonNullable<Layout["shapes"]> = [];
        let dates;
        if (!lines.length || !lines[0].startDates?.length) {
            if (!startDate || !endDate)
                return shapes;
            dates = getDateRanges(startDate, endDate, granularity).map(d => d.start.toISOString())
        } else {
            dates = lines[0].startDates.map(d => d.toISOString());
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
            <div className="flex flex-col">
                <div className="filter-container flex w-full justify-between items-end px-2 lg:px-6 py-2">
                    {/* <div className="flex gap-8 items-start flex-wrap"> */}
                        {/* <div className="flex gap-2"> */}
                            <div className="filter-group flex flex-col">
                                <label>Date Range:</label>
                                <DatePickerWithRange value={range} onChange={handleDateRangeChange} />
                            </div>
                            <div className="filter-group flex flex-col">
                                <label>Granularity:</label>
                                <Select value={granularity} onValueChange={(value) => setGranularity(value as Granularity)}>
                                    <SelectTrigger className="w-[150px]" data-testid="granularity-select">
                                        <SelectValue placeholder="Select an option" data-testid="selected-granularity-option"/>
                                    </SelectTrigger>

                                    <SelectContent position="popper">
                                        <SelectGroup>
                                            {granularityOptions.map((option) => (
                                                <SelectItem key={option} value={option} data-testid="granularity-option">
                                                    {GranularityText[option]}
                                                </SelectItem>
                                            ))}
                                        </SelectGroup>
                                    </SelectContent>
                                </Select>
                            {/* </div> */}
                        {/* </div> */}
                    </div>
                    <div className="filter-group flex flex-col">
                        <label>Areas:</label>
                        <MultiSelect ref={areaSelectRef} options={areaOptions} onValueChange={handleAreaChange} value={selectedAreas} data-testid="area-selector" />
                    </div>
                    <div className="filter-group flex flex-col">
                        <label>Trails:</label>
                        <MultiSelect ref={trailSelectRef} options={trailOptions} onValueChange={handleTrailChange} value={trails} data-testid="trail-selector"/>
                    </div>
                    <div className="flex flex-col">
                        <label>Additional Options:</label>
                        <div className="flex flex-row gap-4 lg:gap-2 justify-between items-center">
                            {(currentRole === null ) && (
                                <div>Please log in or register to view additional options.</div>
                            )}
                            {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                                <Button variant="secondary" className="px-2" onClick={handleAssociateDevice} data-testid="associate-device">Associate Device</Button>
                            )}
                            {currentRole !== null && (
                                <Popover open={isDownloadingStatus !== "idle"}>
                                    <PopoverTrigger asChild>
                                        <Button variant="secondary" className="px-2" onClick={handleExportData} disabled={isDownloadingStatus !== "idle"} data-testid="export-data">
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
                                        {isDownloadingStatus === "error" && (
                                            <div>
                                                <X/>
                                                <span>Failed to download.</span>
                                            </div>
                                        )}
                                    </PopoverContent>
                                </Popover>
                            )}
                            {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                                <Popover open={isUploadingStatus !== "idle"}>
                                    <PopoverTrigger asChild>
                                        <Button variant="secondary" className="px-2" onClick={handleImportData} disabled={isUploadingStatus !== "idle"}>
                                            Import Data
                                        </Button>
                                    </PopoverTrigger>
                                    <PopoverContent className="w-auto p-0" align="start">
                                        {isUploadingStatus === "uploading" && (
                                            <div>
                                                <Loader2 className="animate-spin" />
                                                <span>Uploading...</span>
                                            </div>
                                        )}
                                        {isUploadingStatus === "done" && (
                                            <div>
                                                <Check/>
                                                <span>Uploaded</span>
                                            </div>
                                        )}
                                        {isUploadingStatus === "error" && (
                                            <div>
                                                <X/>
                                                <span>Failed to import.</span>
                                            </div>
                                        )}
                                    </PopoverContent>
                                </Popover>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            <div className="w-full border-t bg-gray-50">
                <div>
                    <div className="flex p-2.5 justify-between lg:justify-start lg:gap-2 items-center">
                        <Button variant="primary" onClick={toggleView} className="items-center px-2" data-testid="toggle-view">Toggle View</Button>
                        {(currentRole === Role.Root || currentRole === Role.Admin || currentRole === Role.Manager ) && (
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="primary" className="px-2" data-testid="trail-options">Trail Options</Button>
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
                                    <Button variant="primary" className="px-2" data-testid="area-options">Area Options</Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                    <DropdownMenuGroup>
                                        <DropdownMenuItem onClick={handleAddArea} data-testid="add-area">Add Area</DropdownMenuItem>
                                        <DropdownMenuItem onClick={handleEditArea} data-testid="edit-area">Edit Area</DropdownMenuItem>
                                    </DropdownMenuGroup>
                                </DropdownMenuContent>
                            </DropdownMenu>
                        )}
                    </div>
                {viewMode === "graph" && !graphBroken ? (
                    <div className="text-lg font-bold text-gray-800" data-testid="graph-title">
                        {graphTitle}
                    </div>
                ) : viewMode === "graph"  ? (
                    <div className="text-lg font-bold text-red-700 rounded-lg border border-red-800 bg-red-50 px-4 py-0.75 mx-2" data-testid="graph-title">
                        Failed to Load Trail Data. Check Your Connection and Try Again.
                    </div>
                ) : (
                    <div className="text-lg font-bold text-gray-800">Trail Status Overview</div>
                )}
                </div>
                <div className="w-full bg-gray-50">
                    <div className="w-full border-t border-gray-200">
                        {viewMode === "graph" ? (
                        <div className="relative w-full h-[65vh] min-h-[400px]" data-testid="outer-dashboard-graph" data-graph-updating={graphUpdating}>
                            {graphUpdating  && (
                                <div className="absolute h-full w-full bg-black/40 z-10">
                                    <Loader2
                                        size={80}
                                        strokeWidth={2}
                                        className="absolute left-1/2 -translate-x-1/2 top-1/4 z-10 animate-spin text-navbar"
                                    />
                                </div>
                            )}
                            <Plot 
                                className="w-full h-full"
                                config={{ displayModeBar: false, responsive: true }}
                                useResizeHandler={true}
                                style={{ width: "100%", height: "100%" }}
                                data={getPlotData(graphLines)}
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
            <EditAreaModal
                isOpen={isEditAreaModalOpen}
                onClose={() => setIsEditAreaModalOpen(false)}
                onUpdate={handleTrailUpdated}
                availableTrails={trailMetadata}
                areas={areas}
                isCreateMode={false}
            />
            <EditAreaModal
                isOpen={isAddAreaModalOpen}
                onClose={() => setIsAddAreaModalOpen(false)}
                onUpdate={handleTrailUpdated}
                availableTrails={trailMetadata}
                areas={areas}
                isCreateMode={true}
            />
            <AssociateDeviceModal
                isOpen={isAssociateDeviceModalOpen}
                onClose={() => setIsAssociateDeviceModalOpen(false)}
                onUpdate={handleTrailUpdated}
            />
        <div className="p-12"></div>
        </div>
    );
};

export default dashboard;
