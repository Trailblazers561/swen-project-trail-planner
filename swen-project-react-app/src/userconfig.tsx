import Navbar from "./components/Navbar";
import { useEffect, useState } from "react";
import { TrailData } from "./api";
import UserDataTable from "./components/tables/UserDataTable";

interface User {
    user_id: number;
    username: string;
    email: string;
    role: string;
}

const Privileges = () => {
    const [users, setUsers] = useState<string[]>([]);
    const [userListData, setUserListData] = useState<Array<User>>([]);
    const [loadingListData, setLoadingListData] = useState(false);

    const { getUsers } = TrailData();

    const loadUsers = async () => {
        try {
            const response = await getUsers();

            if (response.success) {
                const data: User[] = await response.json;

                console.log("Users:", data);

                setUsers(data.map((user) => user.username));
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
                    // <ul>
                    //     {users.map((user, index) => (
                    //         <li key={index} className="p-2 border-b">
                    //             {user}
                    //         </li>
                    //     ))}
                    // </ul>
                    <div className="pt-4 m-4">
                        <UserDataTable data={users} loading={loadingListData} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default Privileges;