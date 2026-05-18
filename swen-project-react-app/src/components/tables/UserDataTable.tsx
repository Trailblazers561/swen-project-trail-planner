import { Role } from "@/Context";
import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";

interface UserRow {
  user_id: number;
  username: string;
  email: string;
  role: Role;
}

interface Props {
  data: string[];
  loading: boolean;
}

const columns: TableColumn<string>[] = [
  // {name: "ID",
  //   selector: (row) => row.user_id,
  //   sortable: true,
  //   center: true
  // },
  {
    name: "Username",
    selector: (row) => row,
    sortable: true,
    grow: 2,
  },
  // {
  //   name: "Role",
  //   selector: (row) => row.role,
  //   sortable: true,
  //   center: true,
  // },
  // {
  //   name: "Email",
  //   selector: (row) => row.email,
  //   sortable: true,
  //   center: true,
  // }
];

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
        pagination = {true}
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