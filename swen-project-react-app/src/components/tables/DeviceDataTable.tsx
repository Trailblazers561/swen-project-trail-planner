import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";

interface DeviceRow {
  name: string;
  id: number;
  trailName: string;
  weeklyCount: number;
  firmware_version:string;
  batteryStatus: number | null;
  lastUpdated: string | null;
}

interface Props {
  data: DeviceRow[];
  loading: boolean;
}

const columns: TableColumn<DeviceRow>[] = [
  {
    name: "Device Name",
    selector: (row) => row.name,
    sortable: false,
    center: true,
  },
    {
    name: "Associated Trail",
    // selector: (row) => row.trailName,
    cell: (row) => {
        if(row.trailName == null)
            return <span className="text-gray-400">Unassociated</span>;
        else
            return <span>{row.trailName}</span>;
    },
    sortable: false,
    center: true,
  },
  {
    name: "Weekly Count",
    selector: (row) => row.weeklyCount,
    sortable: true,
    center: true,
  },
  {
    name: "Battery Status",
    sortable: false,
    center: true,
    cell: (row) => {
      if (row.batteryStatus == null)
        return <span className="text-gray-400">N/A</span>;

      let batteryClass = "";

      if (row.batteryStatus > 50) {
        batteryClass = "text-green-700";
      } else if (row.batteryStatus > 20) {
        batteryClass = "text-orange-600";
      } else {
        batteryClass = "text-red-600";
      }

      return (
        <span className={batteryClass}>
          {row.batteryStatus}%
        </span>
      );
    },
    sortFunction: (a, b) =>
      (a.batteryStatus ?? -1) - (b.batteryStatus ?? -1),
  },
  {
    name: "Last Updated",
    sortable: true,
    center: true,
    cell: (row) => {
    if (!row.lastUpdated) {
      return <span className="text-gray-400">N/A</span>;
    }

    return <span>{row.lastUpdated}</span>;
  },
  sortFunction: (a, b) =>
    (a.lastUpdated ?? "").localeCompare(b.lastUpdated ?? ""),
  },
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

const DeviceDataTable: React.FC<Props> = ({ data, loading }) => {
  return (
    <div className="bg-gray-50 shadow-md" data-testid="device-status-table">
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
            No trails found.
          </div>
        }
      />
    </div>
  );
};

export default DeviceDataTable;