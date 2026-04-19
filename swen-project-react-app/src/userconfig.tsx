import Navbar from "./components/Navbar";
import { useEffect, useState } from "react";
import { TrailData } from "./api";

const Privileges = () => {

    const [users, setUsers] = useState<string[]>([]);

    const {
        getUsers
    } = TrailData();

    const loadActiveUserData = async () => {
        try {
            const [metadataResponse, usersResponse] = await Promise.all([
                getUsers,
            ]);

            if (metadataResponse.success && usersResponse.success) {
                const metadata = await metadataResponse.json;
                const usersData = await usersResponse.json;

                //filter any invalid entries?

                //setTrailMetadata(metadata); probably not needed
                setUsers(usersData);
            }
        } catch (error) {
            console.error("Error loading trail data:", error);
        }
    };

    // Load users from database
    useEffect(() => {

    }, []);



    return (
        <div className="flex flex-col">
            <Navbar />

            <div className="filter-group w-full bg-[var(--color-button-secondary)]">
                <div className="font-semibold text-2xl p-2 ml-2 text-left">
                    Privilege Management
                </div>
            </div>

            <div>hello, world!</div>
        </div>
    );
}

export default Privileges;