import { createContext, useContext, useEffect, useState } from "react";

const Context = createContext(null);

export const AuthProvider = ({ children }) => {
    const [role, setRole] = useState<string[]>([]);

    useEffect(() => {
        const idToken = sessionStorage.getItem("idToken");

        if (idToken) {
            try {
                const payload = JSON.parse(atob(idToken.split('.')[1]));
                setRole(payload['cognito:groups'] || []);
            } catch(e) {
                console.error("Failed to parse idToken:", e);
            }
        }

    }, []);

    return (
        <Context.Provider value={{ groups }}>
            {children}
        </Context.Provider>
    );
};

export const useAuth = () => useContext(Context);