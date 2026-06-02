import { Role, roleMap } from "@/Context";
import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";
import { TrailData } from "@/api";
import { Button } from "../templates/button";

interface UserRow {
    user_id: string;
    username: string;
    email: string;
    role: Role;
}

interface Props {
    data: UserRow[];
    loading: boolean;
    onRoleUpdated: (username: string, newRole: Role) => void;
}

const stringToEnum: Record<string, Role> = {
    ["user"]: Role.User,
    ["trail_manager"]: Role.Manager,
    ["admin"]: Role.Admin,
    ["root_admin"]: Role.Root,
};

const updateUserRole = async (option: string, row: UserRow, onRoleUpdated: (username: string, newRole: Role) => void) => {
    const isPromote = option === "promote";
    const isDemote = option === "demote";
    const { updateUserRole } = TrailData();

    try {
        // the call filling the table converts our Roles back to strings, so we need to convert them back
        let newRole: Role = stringToEnum[row.role];

        if (isPromote && newRole < Role.Root) {
            newRole = newRole + 1;
        }
        
        if (isDemote && newRole > Role.User) {
            newRole = newRole - 1;
        }

        const roleForApi = roleMap[newRole];

        console.log(row.username);
        const response = await updateUserRole(row.username, roleForApi);
        console.log(response.json);
        if(response.success) {
            onRoleUpdated(row.username, newRole);
            console.log(`Successfully updated role for ${row.username} to ${roleForApi}`);
        }
    } catch (error) {
        console.error("Error updating role:", error);
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

    user: "User",
    trail_manager: "Trail Manager",
    admin: "Admin",
    root_admin: "Root Admin",
};

const UserDataTable: React.FC<Props> = ({ data, loading, onRoleUpdated, }) => {

    const columns: TableColumn<UserRow>[] = [
    {
        name: "Username",
        selector: (row) => row.username,
        sortable: true,
        grow: 2,
    },
    {
    name: "Role",
    selector: (row) => roleDisplayMap[row.role] ?? String(row.role),
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
    cell: (row: UserRow) => (
        <div>
            <Button onClick={() => { updateUserRole("promote", row, onRoleUpdated); }} disabled={row.role === Role.Root} className="bg-green-500 hover:bg-green-600 text-white px-2 py-1 mr-2">
                Promote
            </Button>
            <Button onClick={() => { updateUserRole("demote", row, onRoleUpdated); }} disabled={row.role === Role.User} className="bg-red-500 hover:bg-red-600 text-white px-2 py-1">
                Demote
            </Button>
        </div>
    ),
}
];

    return (
        <div className="bg-gray-50 shadow-md" data-testid="trail-user-table">
            <DataTable
                columns={columns}
                data={data}
                progressPending={loading}
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