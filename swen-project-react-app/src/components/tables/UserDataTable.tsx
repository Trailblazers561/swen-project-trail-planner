import { Role, roleMap, useAuth } from "@/Context";
import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";
import { TrailData } from "@/api";
import { Button } from "../templates/button";

interface UserRow {
    user_id: string;
    username: string;
    email: string;
    role: Role;
    banned: boolean;
}

interface Props {
    data: UserRow[];
    onRefresh: () => Promise<void>;
}

const updateUserRole = async (option: string, row: UserRow, onRefresh: () => Promise<void>) => {
    const isPromote = option === "promote";
    const isDemote = option === "demote";
    const { updateUserRole } = TrailData();

    try {
        let newRole: Role = row.role;

        if (isPromote && newRole < Role.Root) {
            newRole = newRole + 1;
        }

        if (isDemote && newRole > Role.User) {
            newRole = newRole - 1;
        }

        const roleForApi = roleMap[newRole];

        const response = await updateUserRole(row.username, roleForApi);
        console.log(response.json);
        if (response.success) {
            await onRefresh();
            console.log(`Successfully updated role for ${row.username} to ${roleForApi}`);
        }
    } catch (error) {
        console.error("Error updating role: ", error);
    }
};

const banUser = async (username: string, onRefresh: () => Promise<void>) => {
    const confirmed = window.confirm(
        `Are you sure you want to ban ${username}?`
    );

    if (!confirmed) {
        return;
    }

    const { banUser } = TrailData();

    try {
        const response = await banUser(username);
        console.log(response.json);

        if (response.success) {
            console.log(`Successfully banned user ${username}`);
            await onRefresh();
        }
    } catch (error) {
        console.error("Error banning user:", error);
    }
};

const unbanUser = async (username: string, onRefresh: () => Promise<void>) => {
    await onRefresh();
    const confirmed = window.confirm(
        `Are you sure you want to unban ${username}?`
    );

    if (!confirmed) {
        return;
    }

    const { updateUserRole } = TrailData();

    try {
        const response = await updateUserRole(username, roleMap[Role.User]);
        console.log(response.json);
        if (response.success) {
            console.log(`Successfully unbanned user ${username}`);
        }
    } catch (error) {
        console.error("Error unbanning user:", error);
    }
};

const customStyles = {
    table: {
        style: {
            overflow: "hidden",
        },
    },
    headRow: {
        style: {
            backgroundColor: "#C0D3D1",
            minHeight: "52px",
        },
    },
    headCells: {
        style: {
            fontWeight: 600,
            fontSize: "15px",
            letterSpacing: "0.05em",
        },
    },
    rows: {
        style: {
            fontSize: "15px",
            minHeight: "48px",
        },
        stripedStyle: {
            backgroundColor: "#edeef0",
        },
    },
    pagination: {
        style: {
            borderBottomLeftRadius: "0.75rem",
            borderBottomRightRadius: "0.75rem",
        },
    },
};

const roleDisplayMap: Record<string | number, string> = {
    [Role.User]: "User",
    [Role.Manager]: "Trail Manager",
    [Role.Admin]: "Admin",
    [Role.Root]: "Root Admin",
};

const UserDataTable: React.FC<Props> = ({ data, onRefresh}) => {

    const { currentRole, username } = useAuth();

    const columns: TableColumn<UserRow>[] = [
        {
            name: "Username",
            selector: (row) => row.username,
            sortable: true,
            grow: 2,
        },
        {
            name: "Role",
            selector: (row) =>
            row.role == null ? "None" : (roleDisplayMap[row.role] ?? "None"),
            sortable: true,
            center: true,
        },
        {
            name: "Banned?",
            selector: (row) => row.banned ? "Yes" : "No",
            sortable: true,
            center: true,
        },
        {
            name: "Email",
            selector: (row) => row.email,
            sortable: true,
            center: true,
        },
        {
            name: "Actions",
            center: true,
            cell: (row: UserRow) => {


                return (
                    <div>
                        <Button
                            onClick={() => { updateUserRole("promote", row, onRefresh); }}
                            disabled={row.username === username || row.role === Role.Root || row.role === Role.Admin || (row.role === Role.Manager && currentRole === Role.Admin)}
                            className="bg-green-500 hover:bg-green-600 text-white px-2 py-1 mr-2"
                        >
                            Promote
                        </Button>
                        <Button
                            onClick={() => { updateUserRole("demote", row, onRefresh); }}
                            disabled={row.username === username || row.role === Role.User || row.role === Role.Root}
                            className="bg-red-500 hover:bg-red-600 text-white px-2 py-1"
                        >
                            Demote
                        </Button>
                        {row.banned ? (
                            <Button
                                onClick={() => unbanUser(row.username, onRefresh)}
                                className="bg-blue-700 hover:bg-blue-600 text-white px-2 py-1"
                                disabled={row.role === Role.Root || row.role === currentRole}
                            >
                                Unban
                            </Button>
                        ) : (
                            <Button
                                onClick={() => banUser(row.username, onRefresh)}
                                className="bg-red-700 hover:bg-red-600 text-white px-2 py-1"
                                disabled={row.role === Role.Root || row.role === currentRole}
                            >
                                Ban
                            </Button>
                        )}

                    </div>
                );
            }
        }
    ];

    return (
        <div className="bg-gray-50 shadow-md" data-testid="trail-user-table">
            <DataTable
                columns={columns}
                data={data}
                pagination={true}
                striped
                responsive
                customStyles={customStyles}
                noDataComponent={
                    <div className="py-6 text-gray-500">
                        No users found.
                    </div>
                }
            />
        </div>
    );
};

export default UserDataTable;