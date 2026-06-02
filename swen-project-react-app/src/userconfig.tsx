import Navbar from "./components/Navbar";
import { useEffect, useState } from "react";
import { TrailData } from "./api";
import UserDataTable from "./components/tables/UserDataTable";
import { Role } from "./Context";

interface User {
    user_id: string;
    username: string;
    email: string;
    role: Role;
}

export const stringToEnum: Record<string, number> = {
    "user": 1,
    "trail_manager": 2,
    "admin": 3,
    "root_admin": 4,
};

const Privileges = () => {
    const [users, setUsers] = useState<string[]>([]);
    const [userListData, setUserListData] = useState<Array<User>>([]);

    const { getUsers } = TrailData();

    const loadUsers = async () => {
        try {
            const response = await getUsers();

            if (response.success) {
                const data: User[] = await response.json;

                console.log("Users:", data);

                setUsers(data.map((user) => user.username));

                setUserListData(
                    data.map((user) => ({
                        user_id: user.user_id,
                        username: user.username,
                        email: user.email,
                        role: stringToEnum[user.role],
                    }))
                );
            }
        } catch (error) {
            console.error("Error loading users:", error);
        }
    };

    const handleRoleUpdated = (username: string, newRole: Role) => {
        setUserListData(prev =>
            prev.map(user =>
                user.username === username
                    ? { ...user, role: newRole }
                    : user
            )
        );
    };

    useEffect(() => {
        loadUsers();
    }, []);

    return (
        <div className="flex flex-col">
            <Navbar />

            <div className="w-full bg-[var(--color-button-secondary)]">
                <div className="font-semibold text-2xl p-2 ml-2 text-left"> User Configuration </div>
            </div>

            {/* Render users */}
            <div className="p-4">
                {users.length === 0 ? (
                    <div>Loading...</div>
                ) : (
                    <div className="pt-4 m-4">
                        <UserDataTable data={userListData} onRoleUpdated={handleRoleUpdated} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default Privileges;