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
                    <h2 style={{ fontFamily: "monospace" }}>{deviceId}</h2>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    {loading ? (
                        <p style={{ textAlign: "center", color: "#666" }}>Loading…</p>
                    ) : entries.length === 0 ? (
                        <p style={{ textAlign: "center", color: "#666" }}>No call-in history found.</p>
                    ) : (
                        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9em" }}>
                            <thead>
                                <tr style={{ backgroundColor: "#007bff", color: "white" }}>
                                    {headers.map((h) => (
                                        <th key={h} style={{ padding: "10px 12px", textAlign: "center", border: "1px solid #ddd", fontWeight: "bold" }}>
                                            {h}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {entries.map((e, i) => (
                                    <tr key={i} style={{ backgroundColor: i % 2 === 0 ? "#f9f9f9" : "#fff" }}>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", whiteSpace: "nowrap" }}>{fmt(e.timestamp)}</td>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", textAlign: "center" }}>{e.firmware_version ?? "—"}</td>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", textAlign: "center" }}>
                                            {e.battery != null ? (
                                                <span style={{ color: e.battery > 50 ? "#28a745" : e.battery > 20 ? "#ffc107" : "#dc3545", fontWeight: "bold" }}>
                                                    {e.battery}%
                                                </span>
                                            ) : "—"}
                                        </td>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", textAlign: "center" }}>{e.rssi != null ? `${e.rssi} dBm` : "—"}</td>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", textAlign: "center" }}>{e.rsrp != null ? `${e.rsrp} dBm` : "—"}</td>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", textAlign: "center" }}>{e.rsrq != null ? `${e.rsrq} dB` : "—"}</td>
                                        <td style={{ padding: "10px 12px", border: "1px solid #ddd", textAlign: "center" }}>{e.record_count ?? "—"}</td>
                                    </tr>
                                ))}
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
