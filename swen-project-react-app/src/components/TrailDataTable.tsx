import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";

interface TrailRow {
  trail_id: number;
  trail_name: string;
  weeklyCount: number;
  batteryStatus: number | null;
  lastUpdated: string | null;
}

interface Props {
  data: TrailRow[];
  loading: boolean;
}

const columns: TableColumn<TrailRow>[] = [
  {
    name: "Trail Name",
    selector: (row) => row.trail_name,
    sortable: true,
    grow: 2,
  },
  {
    name: "Weekly Count",
    selector: (row) => row.weeklyCount,
    sortable: true,
    center: true,
  },
  {
    name: "Battery Status",
    sortable: true,
    center: true,
    cell: (row) => {
      if (row.batteryStatus === null)
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

const TrailDataTable: React.FC<Props> = ({ data, loading }) => {
  return (
    <div className="bg-gray-50 shadow-md" data-testid="trail-status-table">
      <DataTable
        columns={columns}
        data={data}
        progressPending={loading}
        pagination = {true}
        highlightOnHover
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

export default TrailDataTable;