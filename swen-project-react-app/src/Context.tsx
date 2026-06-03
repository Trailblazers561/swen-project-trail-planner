import { createContext, useContext, useEffect, useState } from "react";
import { UserRole } from "./lib/apiTypes";

export enum Role {
    User = 1,
    Manager = 2,
    Admin = 3,
    Root = 4
}

export const roleMap: Record<number, UserRole> = {
    1: UserRole.User,
    2: UserRole.TrailManager,
    3: UserRole.Admin,
    4: UserRole.RootAdmin,
};

type AuthContextType = {
    username: string;
    roles: Role[];
    currentRole: Role | null;
    clearAuth: () => void;
    setAuth: (idToken: string, accessToken: string, refreshToken: string) => void;
};



const Context = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    let initialRoles: Role[] = [];
    let initialUsername: string = "";
    const idToken = localStorage.getItem("idToken");

    if (idToken) {
        try {
            const payload = JSON.parse(atob(idToken.split(".")[1]));

            const groups: string[] = payload["cognito:groups"] || [];

            const parsedRoles: Role[] = [];

            groups.forEach((group) => {
                if (group === "root_admin") parsedRoles.push(Role.Root);
                else if (group === "admin") parsedRoles.push(Role.Admin);
                else if (group === "trail_manager") parsedRoles.push(Role.Manager);
                else if (group === "user") parsedRoles.push(Role.User);
            });

            initialRoles = parsedRoles.length ? parsedRoles : [];
            initialUsername = payload["cognito:username"] || "";
        } catch (e) {
            initialRoles = [];
            initialUsername = "";
        }
    }


    const [roles, setRoles] = useState<Role[]>(initialRoles);
    const [username, setUsername] = useState<string>(initialUsername);
    const currentRole = roles.length ? roles.reduce((a, b) => (b > a ? b : a)) : null;

    const refreshAuth = () => {
        const idToken = localStorage.getItem("idToken");

        if (idToken) {
            try {
                const payload = JSON.parse(atob(idToken.split(".")[1]));

                const groups: string[] = payload["cognito:groups"] || [];

                const parsedRoles: Role[] = [];

                groups.forEach((group) => {
                    if (group === "root_admin") parsedRoles.push(Role.Root);
                    else if (group === "admin") parsedRoles.push(Role.Admin);
                    else if (group === "trail_manager") parsedRoles.push(Role.Manager);
                    else if (group === "user") parsedRoles.push(Role.User);
                });

                setRoles(parsedRoles.length ? parsedRoles : []);
                setUsername(payload["cognito:username"] || "");
            } catch (e) {
                console.error("Failed to parse idToken:", e);
            }
        }
        else {
            setRoles([]);
            setUsername("");
        }
    };

    useEffect(() => {
        refreshAuth();
    }, []);

    const clearAuth = () => {
        localStorage.clear();
        refreshAuth();
    };

    const setAuth = (idToken: string, accessToken: string, refreshToken: string) => {
        setTokens(idToken, accessToken, refreshToken)

        refreshAuth();
    }

    return (
        <Context.Provider value={{ username, roles, currentRole, clearAuth, setAuth }}>
            {children}
        </Context.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(Context);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
};

export function isAuthenticated() {
    return !!localStorage.getItem("idToken");
}

export function isTokenExpired() {
    const idToken = localStorage.getItem("idToken");
    if (!idToken)
        return false;

    const expiration = JSON.parse(atob(idToken.split('.')[1]))["exp"] * 1000;

    return expiration <= Date.now();
}

export function setTokens(idToken: string, accessToken: string, refreshToken: string) {
    localStorage.setItem("idToken", idToken);
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
}

export function getToken() {
    return localStorage.getItem("accessToken") ?? "";
}