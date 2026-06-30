import { useEffect, useState } from "react";
import { TrailData } from "./api";
import UserDataTable from "./components/tables/UserDataTable";
import type { UserRow } from "./components/tables/UserDataTable";
import AccountDataTable from "./components/tables/AccountDataTable";
import { Role, useAuth } from "./Context";
import { useMediaQuery } from "react-responsive";

interface User {
    user_id: string;
    username: string;
    email: string;
    role: Role;
    banned: boolean
}

export const stringToEnum: Record<string, number> = {
    "guest": 0,
    "user": 1,
    "trail_manager": 2,
    "admin": 3,
    "root_admin": 4,
};

type DeviceType = {
    children: React.ReactNode;
  }

  const Desktop = ({children}: DeviceType) => {
    const isDesktop = useMediaQuery({ minWidth: 992 })
    return isDesktop ? children : null
  }
  const Mobile = ({children}: DeviceType) => {
    const isMobile = useMediaQuery({maxWidth: 500})
    return isMobile ? children: null
  }

const Privileges = () => {
    const [users, setUsers] = useState<string[]>([]);
    const [userListData, setUserListData] = useState<Array<User>>([]);
    const [selectedUser, setSelectedUser] = useState<Array<UserRow>>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { getUsers } = TrailData();

    const {currentRole} = useAuth();

    // const modalHandler = () => {
    //     if (selectedUser.length == 0) {
    //         setIsModalOpen(false)
    //     }
    //     else {
    //         setIsModalOpen(true)
    //     }
    // }

    const handleRowClick = (user: UserRow) => {
        setSelectedUser([user]);
        setIsModalOpen(true);

        // console.log("User: ", user);
        // console.log("Selected User Array: ", selectedUser); //For some reason, selectedUser isn't updated until after this function concludes
        
    }

    const handleModalClose = () => {
        setSelectedUser([]);
        setIsModalOpen(false); //does not use updated selectedUser for some reason

        // console.log("Selected User Array: ", selectedUser);
    }
    

    const loadUsers = async () => {
        try {
            const response = await getUsers();
            
            if (response.success) {
                const data: User[] = await response.json;
                
                if(currentRole == null) {
                    return;
                }

                setUsers(data.filter((user) => stringToEnum[user.role] < currentRole).map((user) => user.username));

                setUserListData(
                    data.filter((user) => stringToEnum[user.role] < currentRole).map((user) => ({
                        user_id: user.user_id,
                        username: user.username,
                        email: user.email,
                        role: stringToEnum[user.role],
                        banned: user.banned
                    }))
                );
            }
        } catch (error) {
            console.error("Error loading users:", error);
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    useEffect(() => {

    }, [selectedUser]);

    // console.log(selectedUser);

    return (
        <><meta name="viewport" content="width=device-width initial-scale=1.0" /><div className="flex flex-col">

            <div className="w-full bg-[var(--color-button-secondary)]">
                <div className="font-semibold text-2xl p-2 ml-2 text-left"> User Configuration </div>
            </div>

            {/* Render users */}
            <div className="lg:p-4 p-2">
                {users.length === 0 ? (
                    <div>Loading...</div>
                ) : (
                    <div className="pt-4 lg:m-4">
                        <UserDataTable data={userListData} onRefresh={loadUsers} onRowClick={handleRowClick} />
                    </div>
                )}
            </div>
            {isModalOpen && <Mobile>
                <AccountDataTable data={selectedUser} onClose={handleModalClose}/>
            </Mobile>}
        </div></>
    );
};

export default Privileges;