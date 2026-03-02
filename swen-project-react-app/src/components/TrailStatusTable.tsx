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
        return <span className="na-text">N/A</span>;

      const color =
        row.batteryStatus > 50
          ? "#2e7d32"
          : row.batteryStatus > 20
          ? "#ed6c02"
          : "#d32f2f";

      return (
        <span style={{ color, fontWeight: 600 }}>
          {row.batteryStatus}%
        </span>
      );
    },
    sortFunction: (a, b) =>
      (a.batteryStatus ?? -1) - (b.batteryStatus ?? -1),
  },
  {
    name: "Last Updated",
    selector: (row) => row.lastUpdated ?? "N/A",
    sortable: true,
    center: true,
  },
];

const customStyles = {
  headRow: {
    style: {
      backgroundColor: "#f4f1ea",
      fontWeight: 600,
      fontSize: "16px",
    },
  },
  rows: {
    style: {
      fontSize: "15px",
      paddingTop: "8px",
      paddingBottom: "8px",
    },
  },
  table: {
    style: {
      borderRadius: "10px",
      overflow: "hidden",
    },
  },
};

const TrailStatusTable: React.FC<Props> = ({ data, loading }) => {
  return (
    <DataTable
      columns={columns}
      data={data}
      progressPending={loading}
      pagination
      highlightOnHover
      responsive
      customStyles={customStyles}
      noDataComponent="No trails found."
    />
  );
};

export default TrailStatusTable;