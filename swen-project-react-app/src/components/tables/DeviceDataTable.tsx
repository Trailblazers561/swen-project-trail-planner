import React from "react";
import DataTable, { TableColumn } from "react-data-table-component";
import { useMediaQuery } from "react-responsive";

export interface DeviceRow {
  name: string;
  id: number;
  trailName: string | null;
  weeklyCount: number;
  firmware_version:string;
  batteryStatus: number | null;
  lastUpdated: string | null;
}

interface Props {
  data: DeviceRow[];
  loading: boolean;
  onRowClick?: (device: DeviceRow) => void;
}

type DeviceType = {
    children: React.ReactNode;
  }

const Desktop = ({children}: DeviceType) => {
  const isDesktop = useMediaQuery({ minWidth: 1024 })
  return isDesktop ? children : null
}
const Mobile = ({children}: DeviceType) => {
  const isMobile = useMediaQuery({maxWidth: 1023})
  return isMobile ? children: null
}

const columns: TableColumn<DeviceRow>[] = [
  {
    name: "Device Name",
    selector: (row) => row.name,
    sortable: true,
    grow: 2,
  },
    {
    name: "Associated Trail",
    sortable: true,
    cell: (row) => {
        if(row.trailName == null)
            return <span className="text-gray-400">Unassociated</span>;
        else
            return <span>{row.trailName}</span>;
    },
    sortFunction: (a, b) =>
    (a.trailName ?? "").localeCompare(b.trailName ?? ""),
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

const columnsMobile: TableColumn<DeviceRow>[] = [
  {
    name: "Device Name",
    selector: (row) => row.name,
    sortable: true,
  },
  {
    name: "Associated Trail",
    sortable: true,
    cell: (row) => {
        if(row.trailName == null)
            return <span className="text-gray-400">Unassociated</span>;
        else
            return <span>{row.trailName}</span>;
    },
    sortFunction: (a, b) =>
    (a.trailName ?? "").localeCompare(b.trailName ?? ""),
    center: true,
  },
  {
    name: "Weekly Count",
    selector: (row) => row.weeklyCount,
    sortable: true,
    center: true,
  }
]

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
      "&:nth-of-type(odd):hover": {
        backgroundColor: "#e3e4e6",
      },
      "&:nth-of-type(even):hover": {
        backgroundColor: "#f7f7f7",
      },
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
      fontSize: "15px",
      letterSpacing: "0.05em",
    },
  },
  rows: {
    style: {
      fontSize: "12px",
      minHeight: "48px",
      "&:nth-of-type(odd):hover": {
        backgroundColor: "#e3e4e6",
      },
      "&:nth-of-type(even):hover": {
        backgroundColor: "#f7f7f7",
      },
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

const DeviceDataTable: React.FC<Props> = ({ data, loading, onRowClick }) => {
  return (
    <div className="bg-gray-50 shadow-md" data-testid="device-status-table">
      <Desktop>
        <DataTable
          columns={columns}
          data={data}
          progressPending={loading}
          pagination={true}
          striped
          responsive
          customStyles={customStyles}
          pointerOnHover
          highlightOnHover
          onRowClicked={onRowClick}
          noDataComponent={
            <div className="py-6 text-gray-500">
              No devices found.
            </div>
          }
        />
      </Desktop>
      <Mobile>
        <DataTable
        columns={columnsMobile}
        data={data}
        progressPending={loading}
        striped
        responsive
        customStyles={customStylesMobile}
        onRowClicked={onRowClick}
        noDataComponent={
          <div className="py-6 text-gray-500">
            No devices found.
          </div>
        }
        />
      </Mobile>
    </div>
  );
};
export default DeviceDataTable;