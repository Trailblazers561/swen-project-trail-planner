import React, { useState } from "react";
import DataTable, { type TableColumn, type ExpanderComponentProps } from "react-data-table-component";
import moment from "moment-timezone";
import { CircleQuestionMark } from "lucide-react";
import { createPortal } from "react-dom";


interface DeviceLogRow {
  time: number;
  firmware_version: string | null;
  battery: number | null;
  rssi: number | null;
  rsrp: number | null;
  rsrq: number | null;
  count: number;
}

interface TooltipHeaderProps {
  label: string;
  expanded: string;
  description: string;
}

function TooltipHeader({label, expanded, description}: TooltipHeaderProps) {
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="flex items-center">
      {label}
      <div className="relative cursor-help">
        <CircleQuestionMark className="p-1" 
          onMouseEnter={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            setTooltipPosition({
              x: rect.left + rect.width / 2,
              y: rect.top,
            });
            setShowTooltip(true);
          }}
          onMouseLeave={() => setShowTooltip(false)}
        />
      </div>
      {showTooltip &&
        createPortal(
          <div
            className="fixed z-1000 bg-[#e9f2f1] text-[rgba(0,0,0,0.87)] rounded-xl px-3 py-2 w-75"
            style={{
              left: tooltipPosition.x,
              top: tooltipPosition.y - 15,
              transform: "translate(-50%, -100%)",
            }}
          >
            <strong>{label}</strong> stands for <strong>{expanded}</strong>. {description}
            <div className="absolute left-1/2 top-full -translate-x-1/2"
              style={{
                borderLeft: "30px solid transparent",
                borderRight: "30px solid transparent",
                borderTop: "15px solid #e9f2f1",
              }}
            />
          </div>,
        document.body)
      }
    </div>
  );
}

const columns: TableColumn<DeviceLogRow>[] = [
  {
    name: "Date / Time",
    selector: (row) => moment(row.time * 1000).tz("America/New_York").format("MM/DD/YYYY hh:mm:ss A"),
    grow: 2,
    center: true,
  },
  {
    name: "Firmware",
    selector: (row) => row.firmware_version ? row.firmware_version : "N/A",
    center: true,
    hide: 1023,
  },
  {
    name: "Battery",
    center: true,
    cell: (row) => {
      if (row.battery === null)
        return <span className="text-gray-400">N/A</span>;

      let batteryClass = "";

      if (row.battery > 50) {
        batteryClass = "text-green-700";
      } else if (row.battery > 20) {
        batteryClass = "text-orange-600";
      } else {
        batteryClass = "text-red-600";
      }

      return (
        <span className={batteryClass}>
          {row.battery}%
        </span>
      );
    },
  },
  {
    name: <TooltipHeader label="RSSI" expanded="Received Signal Strength Indicator" description="It measures the power level of a radio signal as it is received by a wireless device." />,
    center: true,
    cell: (row) => {
      if (row.rssi === null)
        return <span className="text-gray-400">N/A</span>;

      let rssiClass = "";

      if (row.rssi >= -65) {
        rssiClass = "text-green-700";
      } else if (row.rssi >= -80) {
        rssiClass = "text-orange-600";
      } else {
        rssiClass = "text-red-600";
      }

      return (
        <span className={rssiClass}>
          {row.rssi} dBm
        </span>
      );
    },
    hide: 1023
  },
  {
    name: <TooltipHeader label="RSRP" expanded="Reference Signal Received Power" description="It measures the strength of the signal being received from a nearby cell tower." />,
    center: true,
    cell: (row) => {
      if (row.rsrp === null)
        return <span className="text-gray-400">N/A</span>;

      let rsrpClass = "";

      if (row.rsrp >= -85) {
        rsrpClass = "text-green-700";
      } else if (row.rsrp >= -100) {
        rsrpClass = "text-orange-600";
      } else {
        rsrpClass = "text-red-600";
      }

      return (
        <span className={rsrpClass}>
          {row.rsrp} dBm
        </span>
      );
    },
    hide: 1023
  },
  {
    name: <TooltipHeader label="RSRQ" expanded="Reference Signal Received Quality" description="It measures the clarity and overall usability of a cellular signal." />,
    center: true,
    cell: (row) => {
      if (row.rsrq === null)
        return <span className="text-gray-400">N/A</span>;

      let rsrqClass = "";

      if (row.rsrq >= -7) {
        rsrqClass = "text-green-700";
      } else if (row.rsrq >= -11) {
        rsrqClass = "text-orange-600";
      } else {
        rsrqClass = "text-red-600";
      }

      return (
        <span className={rsrqClass}>
          {row.rsrq} dB
        </span>
      );
    },
    hide: 1023
  },
  {
    name: "Count",
    selector: (row) => row.count,
    center: true,
  }
];

const expandedRow = ({ data: row }: ExpanderComponentProps<DeviceLogRow>) => (
  <div style={{ padding: '16px 40px', background: '#f9fafb' }}>
    <div>Time: {moment(row.time * 1000).tz("America/New_York").format("MM/DD/YYYY hh:mm:ss A")}</div>
    <div>Firmware: {row.firmware_version ?? ""}</div>
    <div>
      <TooltipHeader label="RSSI" expanded="Received Signal Strength Indicator" description="It measures the power level of a radio signal as it is received by a wireless device." />
      {row.rssi}
    </div>
    <div>
      <TooltipHeader label="RSSI" expanded="Received Signal Strength Indicator" description="It measures the power level of a radio signal as it is received by a wireless device." />
      {row.rsrp}
    </div>
    <div>
      <TooltipHeader label="RSRQ" expanded="Reference Signal Received Quality" description="It measures the clarity and overall usability of a cellular signal." />
      {row.rsrq}
    </div>
  </div>
);

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

interface Props {
  data: DeviceLogRow[];
  loading: boolean;
}

const DeviceLogTable: React.FC<Props> = ({ data, loading }) => {
  return (
    <div className="bg-gray-50 shadow-md" data-testid="device-log-table">
      <DataTable
        columns={columns}
        data={data}
        progressPending={loading}
        pagination = {false}
        striped
        responsive
        customStyles={customStyles}
        noDataComponent={
          <div className="py-6 text-gray-500">
            No logs found.
          </div>
        }
        expandableRows={true}
        expandableRowsComponent={expandedRow}
      />
    </div>
  );
};

export default DeviceLogTable;