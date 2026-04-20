import { createContext, useContext, useEffect, useState } from "react";

export enum Role {
    User = 1,
    Manager = 2,
    Admin = 3,
    Root = 4
}

type AuthContextType = {
    email: string;
    roles: Role[];
    currentRole: Role | null;
};

const Context = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [roles, setRoles] = useState<Role[]>([]);
    const [email, setEmail] = useState<string>("");

    const currentRole = roles.length ? roles.reduce((a, b) => (b > a ? b : a)) : null;

    useEffect(() => {
        const idToken = sessionStorage.getItem("idToken");

        if (idToken) {
            try {
                const payload = JSON.parse(atob(idToken.split(".")[1]));

                const groups: string[] = payload["cognito:groups"] || [];

                const parsedRoles: Role[] = [];

                groups.forEach((group) => {
                    if (group.includes("root")) parsedRoles.push(Role.Root);
                    else if (group.includes("admin")) parsedRoles.push(Role.Admin);
                    else if (group.includes("manager")) parsedRoles.push(Role.Manager);
                    else if (group.includes("user")) parsedRoles.push(Role.User);
                });

                setRoles(parsedRoles.length ? parsedRoles : []);
                setEmail(payload["email"] || "");
            } catch (e) {
                console.error("Failed to parse idToken:", e);
            }
        }
    }, []);

    return (
        <Context.Provider value={{ email, roles, currentRole }}>
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