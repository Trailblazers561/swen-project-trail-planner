import { createContext, useContext, useEffect, useState } from "react";
import { Granularity } from "./lib/apiTypes";
import moment from "moment-timezone";

export enum DatePreset {
    Day = "day",
    Week = "week",
    Fortnight = "fortnight",
    Month = "month",
    Custom = "custom"
}

type DateContextType = {
    startDate: Date | null;
    setStartDate: (startDate: Date| null) => void;
    endDate: Date | null;
    setEndDate: (endDate: Date| null) => void;
    granularity: Granularity;
    setGranularity: (granularity: Granularity) => void;
    datePreset: DatePreset;
    setDatePreset: (datePreset: DatePreset) => void;
};

const Context = createContext<DateContextType | null>(null);

export const DateProvider = ({ children }: { children: React.ReactNode }) => {
    const [startDate, setStartDateInternal] = useState<Date | null>(null);
    const [endDate, setEndDateInternal] = useState<Date | null>(null);
    const [granularity, setGranularity] = useState<Granularity>(Granularity.Day);
    const [datePreset, setDatePreset] = useState<DatePreset>(DatePreset.Month);
    //     const idToken = localStorage.getItem("idToken");

    //     if (idToken) {
    //         try {
    //             const payload = JSON.parse(atob(idToken.split(".")[1]));

    //             const groups: string[] = payload["cognito:groups"] || [];

    //             const parsedRoles: Role[] = [];

    //             groups.forEach((group) => {
    //                 if (group === "root_admin") parsedRoles.push(Role.Root);
    //                 else if (group === "admin") parsedRoles.push(Role.Admin);
    //                 else if (group === "trail_manager") parsedRoles.push(Role.Manager);
    //                 else if (group === "user") parsedRoles.push(Role.User);
    //             });

    //             setRoles(parsedRoles.length ? parsedRoles : []);
    //             setUsername(payload["cognito:username"] || "");
    //         } catch (e) {
    //             console.error("Failed to parse idToken:", e);
    //         }
    //     }
    //     else {
    //         setRoles([]);
    //         setUsername("");
    //     }
    // };

    useEffect(() => {
        //check for custom first so that dates aren't changed at all
        if (datePreset === DatePreset.Custom) {
            return;
        }

        const endMoment = moment.tz("America/New_York").startOf("day");
        let startMoment: moment.Moment | undefined;

        switch (datePreset) {
            case DatePreset.Day:
                startMoment = endMoment.clone().subtract(1, "day");
                break;
            case DatePreset.Week:
                startMoment = endMoment.clone().subtract(1, "week");
                break;
            case DatePreset.Fortnight:
                startMoment = endMoment.clone().subtract(2, "weeks");
                break;
            case DatePreset.Month:
                startMoment = endMoment.clone().subtract(1, "month");
                break;
        }

        if (!startMoment) return;

        endMoment.subtract(1, "day");

        setStartDateInternal(startMoment.toDate());
        setEndDateInternal(endMoment.toDate());
        setGranularity(Granularity.Day);
    }, [datePreset]);

    const setStartDate = (startDate: Date | null) => {
        setStartDateInternal(startDate);
        setDatePreset(DatePreset.Custom);
    }

    const setEndDate = (endDate: Date | null) => {
        setEndDateInternal(endDate);
        setDatePreset(DatePreset.Custom);
    }

    return (
        <Context.Provider value={{ startDate, setStartDate, endDate, setEndDate, granularity, setGranularity, datePreset, setDatePreset }}>
            {children}
        </Context.Provider>
    );
};

export const useDate = () => {
    const context = useContext(Context);
    if (!context) {
        throw new Error("useDate must be used within DateProvider");
    }
    return context;
};