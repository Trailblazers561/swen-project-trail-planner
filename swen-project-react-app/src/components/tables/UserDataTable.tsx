import { Role, roleMap } from "@/Context";
import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/templates/select";
import { TrailData } from "@/api";

interface UserRow {
    user_id: string;
    username: string;
    email: string;
    role: Role;
}

interface Props {
    data: UserRow[];
    loading: boolean;
}


const columns: TableColumn<UserRow>[] = [
    {
        name: "ID",
        selector: (row) => row.user_id,
        sortable: true,
        center: true
    },
    {
        name: "Username",
        selector: (row) => row.username,
        sortable: true,
        grow: 2,
    },
    {
        name: "Role",
        selector: (row) => row.role,
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
        <Select onValueChange={(value) => { updateUserRole(value, row); }}
        >
            <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select Action" />
            </SelectTrigger>

            <SelectContent>
                <SelectGroup>
                    <SelectItem value="promote">
                        Promote
                    </SelectItem>

                    <SelectItem value="demote">
                        Demote
                    </SelectItem>
                </SelectGroup>
            </SelectContent>
        </Select>
    ),
}
];

const stringToEnum: Record<string, Role> = {
    ["user"]: Role.User,
    ["trail_manager"]: Role.Manager,
    ["admin"]: Role.Admin,
    ["root_admin"]: Role.Root,
};

const updateUserRole = async (option: string, row: UserRow) => {
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

        const response = await updateUserRole(row.user_id, roleForApi);
        console.log(response.json);
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

const UserDataTable: React.FC<Props> = ({ data, loading }) => {
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