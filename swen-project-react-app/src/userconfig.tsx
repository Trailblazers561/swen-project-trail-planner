import Navbar from "./components/Navbar";
import { useEffect, useState } from "react";
import { TrailData } from "./api";

const Privileges = () => {
    const [users, setUsers] = useState<string[]>([]);

    const { getUsers } = TrailData();

    //WIP loading for users, currently is not working (something with authentication not working)
    const loadUsers = async () => {
        try {
            const response = await getUsers();

            if (response.success) {
                const data = await response.json;

                console.log("Users:", data);

                setUsers(data.users || data);
            }
        } catch (error) {
            console.error("Error loading users:", error);
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    return (
        <div className="flex flex-col">
            <Navbar />

            <div className="w-full bg-[var(--color-button-secondary)]">
                <div className="font-semibold text-2xl p-2 ml-2 text-left"> Privilege Management </div>
            </div>

            {/* Render users */}
            <div className="p-4">
                {users.length === 0 ? (
                    <div>No users found</div>
                ) : (
                    <ul>
                        {users.map((user, index) => (
                            <li key={index} className="p-2 border-b">
                                {user}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default Privileges;