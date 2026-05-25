import React, { useEffect, useState } from "react";
import { TrailData } from "../api";
import "./Modal.css";

interface DeviceDetailModalProps {
    deviceId: string | null;
    onClose: () => void;
}

const DeviceDetailModal: React.FC<DeviceDetailModalProps> = ({ deviceId, onClose }) => {
    const [entries, setEntries] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const { getDeviceCallLog } = TrailData();

    useEffect(() => {
        if (!deviceId) return;
        setLoading(true);
        getDeviceCallLog(deviceId).then((res) => {
            const data = res.success ? res.json : [];
            setEntries(data.slice(0, 5));
            setLoading(false);
        });
    }, [deviceId]);

    if (!deviceId) return null;

    const fmt = (ts: any) => {
        if (!ts) return "—";
        const d = new Date((typeof ts === "number" ? ts : parseInt(ts)) * 1000);
        return d.toLocaleString();
    };

    const headers = ["Date / Time", "Firmware", "Battery", "RSSI", "RSRP", "RSRQ", "Count"];

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content modal-content-large" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="device-detail-h2">{deviceId}</h2>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    {loading ? (
                        <p className="device-detail-status">Loading…</p>
                    ) : entries.length === 0 ? (
                        <p className="device-detail-status">No call-in history found.</p>
                    ) : (
                        <table className="device-detail-table">
                            <thead>
                                <tr className="device-detail-header-row">
                                    {headers.map((h) => (
                                        <th key={h} className="device-detail-th">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {entries.map((e, i) => {
                                    const batteryClass = e.battery != null
                                        ? e.battery > 50 ? "battery-high" : e.battery > 20 ? "battery-medium" : "battery-low"
                                        : "";
                                    return (
                                        <tr key={i} className={i % 2 === 0 ? "device-detail-row-even" : "device-detail-row-odd"}>
                                            <td className="device-detail-td-left">{fmt(e.timestamp)}</td>
                                            <td className="device-detail-td">{e.firmware_version ?? "—"}</td>
                                            <td className="device-detail-td">
                                                {e.battery != null ? (
                                                    <span className={batteryClass}>{e.battery}%</span>
                                                ) : "—"}
                                            </td>
                                            <td className="device-detail-td">{e.rssi != null ? `${e.rssi} dBm` : "—"}</td>
                                            <td className="device-detail-td">{e.rsrp != null ? `${e.rsrp} dBm` : "—"}</td>
                                            <td className="device-detail-td">{e.rsrq != null ? `${e.rsrq} dB` : "—"}</td>
                                            <td className="device-detail-td">{e.record_count ?? "—"}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </div>
                <div className="modal-footer">
                    <button onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
};

export default DeviceDetailModal;
