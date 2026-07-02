import { useEffect, useState } from "react";
import { Role, roleMap, useAuth } from "@/AuthContext";
import { TrailData } from "@/api";
import { Button } from "../templates/button";
import { LoaderCircle, ArrowUp, ArrowDown, Ban, Undo2 } from "lucide-react";
import { UserRow } from "../tables/UserDataTable";
import DataTable, { TableColumn } from "react-data-table-component";
import "./Modal.css";

interface Props {
    data: UserRow[];
    onClose?: () => void;
    onRefresh: () => Promise<void>;
    //loading: boolean;
}

//Simulates having headers at the start of a row by having each row contain the header and the respective user data
interface textRow {
        header: string;
        field: string;
    }

const columns: TableColumn<textRow>[] = [
    {
        selector: (row) => row.header, //row is a textRow instance
        // grow: 2,
    },
    {
        selector: (row) => row.field,
        grow: 2
    }
] 

const handleBannedText = (bool: boolean) => {
    if (bool) {
        return ("Yes");
    }
    else {
        return ("No")
    }
}

const handleRoleText = (role: Role) => {
    if (role == Role.User) {
        return("User");
    }
    else if (role == Role.Manager) {
        return("Trail Manager");
    }
    else if (role == Role.Admin) {
        return ("Admin");
    }
    else if (role == Role.Root) {
        return ("Root Admin");
    }
    else if (role == Role.Guest) {
        return ("Guest");
    }
    return("None");
}

const AccountDataTable: React.FC<Props> = ({ data, onClose, onRefresh }) => {

    const [textData, setTextData] = useState<Array<textRow>>([]);
        
    const { currentRole, username } = useAuth();
    const [loadingUsage, setLoadingUsage] = useState(false);
    
    const updateUserRole = async (option: string, row: UserRow, onRefresh: () => Promise<void>) => {
        const isPromote = option === "promote";
        const isDemote = option === "demote";
        const { updateUserRole } = TrailData();

        try {
            setLoadingUsage(true);
            let newRole: Role = row.role;

            if (isPromote && newRole < Role.Root) {
                newRole = newRole + 1;
            }

            if (isDemote && newRole > Role.User) {
                newRole = newRole - 1;
            }

            const roleForApi = roleMap[newRole];

            const response = await updateUserRole(row.username, roleForApi);
            if (response.success) {
                await onRefresh();
                console.log(`Successfully updated role for ${row.username} to ${roleForApi}`);
            }
        } catch (error) {
            console.error("Error updating role: ", error);
        } finally {
            setLoadingUsage(false);
        }
    };

    const banUser = async (user_name: string, onRefresh: () => Promise<void>) => {
        const confirmed = window.confirm(
            `Are you sure you want to ban ${user_name}?`
        );

        if (!confirmed) {
            return;
        }

        const { banUser } = TrailData();

        try {
            setLoadingUsage(true);
            const response = await banUser(user_name);
            console.log(response.json);

            if (response.success) {
                console.log(`Successfully banned user ${user_name}`);
                await onRefresh();
            }
        } catch (error) {
            console.error("Error banning user:", error);
        } finally {
            setLoadingUsage(false);
        }
    };

    const unbanUser = async (user_name: string, onRefresh: () => Promise<void>) => {
        const confirmed = window.confirm(
            `Are you sure you want to unban ${user_name}?`
        );

        if (!confirmed) {
            return;
        }

        const { updateUserRole } = TrailData();

        try {
            setLoadingUsage(true);
            const response = await updateUserRole(user_name, roleMap[Role.User]);
            console.log(response.json);
            if (response.success) {
                console.log(`Successfully unbanned user ${user_name}`);
                await onRefresh();
            }
        } catch (error) {
            console.error("Error unbanning user:", error);
        } finally {
            setLoadingUsage(false);
        }
    };
    

    const loadData = () => {


        if (data[0] != undefined) {

            const usernamerow:textRow = {header: "Username", field: data[0].username};
            const rolerow:textRow = {header: "Role", field: handleRoleText(data[0].role)};
            const bannedrow:textRow = {header: "Banned?", field: handleBannedText(data[0].banned)};
            const emailrow:textRow = {header: "Email", field: data[0].email}

            setTextData([usernamerow, rolerow, bannedrow, emailrow]);
        }

        else {
            setTextData([]);
        }
    }

    useEffect (() => {
        loadData();
    }, [data])
    

    return(
        <div className="bg-gray-50 shadow-md modal-overlay w-screen h-screen" data-testid="device-log-table">
            {loadingUsage && (
                <div className="absolute inset-0 z-[9998] flex items-center justify-center bg-black/20">
                    <LoaderCircle
                        size={80}
                        strokeWidth={2}
                        className="animate-spin text-navbar"
                    />
                </div>
            )}
            <div className="modal-content modal-content-extra-large" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header bg-navbar p-4!">
                    <div className="font-primary text-white font-semibold text-xl left-2">Account Details</div>
                    <button className="modal-close" onClick={onClose}>X</button>
                </div>
                <DataTable
                columns = {columns}
                data = {textData}
                noTableHead={true}
                />
                <div className="flex items-center gap-2">
                    <Button
                        onClick={() => { updateUserRole("promote", data[0], onRefresh); }}
                        disabled={data[0].username === username || data[0].role === Role.Root || data[0].role === Role.Admin || (data[0].role === Role.Manager && currentRole === Role.Admin)}
                        className="bg-green-500 hover:bg-green-600 text-white w-5/16 p-8"
                        title="Promote"
                    >
                        <ArrowUp size={18} />
                    </Button>
                    <Button
                        onClick={() => { updateUserRole("demote", data[0], onRefresh); }}
                        disabled={data[0].username === username || data[0].role === Role.User || data[0].role === Role.Root}
                        className="bg-red-500 hover:bg-red-600 text-white w-5/16 p-8"
                        title="Demote"
                    >
                        <ArrowDown size={18} />
                    </Button>
                    {data[0].banned ? (
                        <Button
                            onClick={() => unbanUser(data[0].username, onRefresh)}
                            className="bg-blue-700 hover:bg-blue-600 text-white w-5/16 p-8"
                            disabled={data[0].role === Role.Root || data[0].role === currentRole}
                            title="Unban"
                        >
                            <Undo2 size={18} />
                        </Button>
                    ) : (
                        <Button
                            onClick={() => banUser(data[0].username, onRefresh)}
                            className="bg-red-700 hover:bg-red-600 text-white w-5/16 p-8"
                            disabled={data[0].role === Role.Root || data[0].role === currentRole}
                            title="Ban"
                        >
                            <Ban size={18} />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    )
}

export default AccountDataTable