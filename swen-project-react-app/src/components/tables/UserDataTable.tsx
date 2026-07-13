import { Role, roleMap, useAuth } from "@/AuthContext";
import React, { useState } from "react";
import DataTable, { TableColumn } from "react-data-table-component";
import { TrailData } from "@/api";
import { Button } from "../templates/button";
import { LoaderCircle, ArrowUp, ArrowDown, Ban, Undo2 } from "lucide-react";
import { useMediaQuery } from "react-responsive";

export interface UserRow {
    user_id: string;
    username: string;
    email: string;
    role: Role;
    banned: boolean;
}

interface Props {
    data: UserRow[];
    onRefresh: () => Promise<void>;
    onRowClick?: (user: UserRow) => void;
}

type DeviceType = {
    children: React.ReactNode;
  }

  const Desktop = ({children}: DeviceType) => {
    const isDesktop = useMediaQuery({ minWidth: 500 })
    return isDesktop ? children : null
  }
  const Mobile = ({children}: DeviceType) => {
    const isMobile = useMediaQuery({maxWidth: 499})
    return isMobile ? children: null
  }

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

const customStylesMobile = {
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
            fontSize: "12px",
            letterSpacing: "0.05em",
        },
    },
    rows: {
        style: {
            fontSize: "12px",
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

const UserDataTable: React.FC<Props> = ({ data, onRefresh, onRowClick }) => {

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
                    <div className="flex items-center gap-2">
                        <Button
                            onClick={() => { updateUserRole("promote", row, onRefresh); }}
                            disabled={row.username === username || row.role === Role.Root || row.role === Role.Admin || (row.role === Role.Manager && currentRole === Role.Admin)}
                            className="bg-green-500 hover:bg-green-600 text-white p-2"
                            title="Promote"
                        >
                            <ArrowUp size={18} />
                        </Button>
                        <Button
                            onClick={() => { updateUserRole("demote", row, onRefresh); }}
                            disabled={row.username === username || row.role === Role.User || row.role === Role.Root}
                            className="bg-red-500 hover:bg-red-600 text-white p-2"
                            title="Demote"
                        >
                            <ArrowDown size={18} />
                        </Button>
                        {row.banned ? (
                            <Button
                                onClick={() => unbanUser(row.username, onRefresh)}
                                className="bg-blue-700 hover:bg-blue-600 text-white p-2"
                                disabled={row.role === Role.Root || row.role === currentRole}
                                title="Unban"
                            >
                                <Undo2 size={18} />
                            </Button>
                        ) : (
                            <Button
                                onClick={() => banUser(row.username, onRefresh)}
                                className="bg-red-700 hover:bg-red-600 text-white p-2"
                                disabled={row.role === Role.Root || row.role === currentRole}
                                title="Ban"
                            >
                                <Ban size={18} />
                            </Button>
                        )}

                    </div>
                );
            }
        }
    ];

    const columnsMobile: TableColumn<UserRow>[] = [
        {
            name: "Username",
            selector: (row) => row.username,
            sortable: true,
        },
        {
            name: "Role",
            selector: (row) => row.role == null ? "None" : (roleDisplayMap[row.role] ?? "None"),
            sortable: true,
        },
        {
            name: "Banned",
            selector: (row) => row.banned ? "Yes" : "No",
            sortable: true,
        }
    ]

    return (
        <div className="bg-gray-50 shadow-md" data-testid="trail-user-table">
            {loadingUsage && (
                <div className="absolute inset-0 z-[30] flex items-center justify-center bg-black/20">
                    <LoaderCircle
                        size={80}
                        strokeWidth={2}
                        className="animate-spin text-navbar"
                    />
                </div>
            )}
            <Desktop>
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
            </Desktop>
            <Mobile>
                <DataTable
                columns={columnsMobile}
                data={data}
                pagination={true}
                striped
                responsive
                customStyles={customStylesMobile}
                onRowClicked={onRowClick}
                noDataComponent={
                    <div className="py-6 text-gray-500">
                        No users found.
                    </div>
                }
                />
            </Mobile>
        </div>
    );
};

export default UserDataTable;