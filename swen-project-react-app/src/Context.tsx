import { createContext, useContext, useEffect, useState } from "react";

export enum Role {
    Guest = 1,
    Manager = 2,
    Admin = 3,
    Root = 4
};

type AuthContextType = {
    email: string;
    role: Role | null;
};

const ROLE_MAPPING: Record<string, Role> = {
    guest: Role.Guest,
    manager: Role.Manager,
    admin: Role.Admin,
    root: Role.Root,
};

const Context = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [role, setRole] = useState<Role | null>(null);
    const [email, setEmail] = useState<string>("");

    useEffect(() => {
        const idToken = sessionStorage.getItem("idToken");

        if (idToken) {
            try {
                const payload = JSON.parse(atob(idToken.split('.')[1]));
                
                const roles: string[] = payload['cognito:groups'] || [];

                //find the correct role based on searching the string returned
                const matchedRole= roles.find(role =>
                    role.includes("root") ||
                    role.includes("admin") ||
                    role.includes("manager") ||
                    role.includes("guest")
                );
                
                if (matchedRole) {
                if (matchedRole.includes("root")) {
                    setRole(Role.Root);
                } else if (matchedRole.includes("admin")) {
                    setRole(Role.Admin);
                } else if (matchedRole.includes("manager")) {
                    setRole(Role.Manager);
                } else if (matchedRole.includes("guest")) {
                    setRole(Role.Guest);
                }
                } else {
                setRole(null);
                }

                setEmail(payload['email'] || "");

            } catch(e) {
                console.error("Failed to parse idToken:", e);
            }
        }

    }, []);

    return (
        <Context.Provider value={{ email, role}}>  
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