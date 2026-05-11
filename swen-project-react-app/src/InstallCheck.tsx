import { useEffect, useState, useCallback } from "react";
import { TrailData } from "./api";

// Phone-friendly "is my device alive" view. Designed for use immediately
// after installing a counter in the field — opens fast, shows clearly
// whether the device has called in, with auto-refresh so the user doesn't
// have to keep reloading. Backed by the same /device_call_log endpoint
// used by Device View on the main dashboard.

type CallLogRow = {
  device_id: string;
  timestamp: number;
  trail_id?: number;
  battery?: number;
  firmware_version?: string;
  rssi?: number;
  rsrp?: number;
  rsrq?: number;
  record_count?: number;
};

type DeviceMeta = {
  device_id: string;
  current_trail_id?: number;
  battery?: number;
  last_update?: number;
};

type Trail = {
  trail_id: number;
  trail_name: string;
};

const REFRESH_INTERVAL_MS = 15_000;

const palette = {
  fresh: "#1f7a3a",       // green — called in within 24h
  stale: "#b88500",       // amber — 24–72h
  dead: "#b03030",        // red — >72h or never
  unassigned: "#5a6470",  // gray — no trail_id
  bg: "#f5f5f7",
  cardBg: "#ffffff",
  cardBorder: "#dfe2e6",
  text: "#1a1a1a",
  subtext: "#6c727a",
};

function formatAge(unixSec: number): { text: string; bucket: "fresh" | "stale" | "dead" } {
  const ageSec = Math.floor(Date.now() / 1000) - unixSec;
  if (ageSec < 0) return { text: "just now", bucket: "fresh" };
  if (ageSec < 60) return { text: `${ageSec}s ago`, bucket: "fresh" };
  if (ageSec < 3600) return { text: `${Math.floor(ageSec / 60)} min ago`, bucket: "fresh" };
  if (ageSec < 86400) return { text: `${Math.floor(ageSec / 3600)} hours ago`, bucket: "fresh" };
  const days = Math.floor(ageSec / 86400);
  const bucket = days < 3 ? "stale" : "dead";
  return { text: `${days} day${days === 1 ? "" : "s"} ago`, bucket };
}

function signalQuality(rssi?: number): string {
  if (rssi === undefined || rssi === null) return "—";
  if (rssi >= -70) return `${rssi} dBm (excellent)`;
  if (rssi >= -85) return `${rssi} dBm (good)`;
  if (rssi >= -100) return `${rssi} dBm (fair)`;
  return `${rssi} dBm (poor)`;
}

function batteryDisplay(b?: number): string {
  if (b === undefined || b === null) return "—";
  return `${b}%`;
}

export default function InstallCheck() {
  const { getDeviceCallLog, getDeviceMetadata, getTrailMetadata } = TrailData();
  const [rows, setRows] = useState<CallLogRow[]>([]);
  const [meta, setMeta] = useState<DeviceMeta[]>([]);
  const [trails, setTrails] = useState<Trail[]>([]);
  const [lastFetch, setLastFetch] = useState<number>(0);
  const [now, setNow] = useState<number>(Date.now());
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [callLogRes, metaRes, trailRes] = await Promise.all([
        getDeviceCallLog(),
        getDeviceMetadata(),
        getTrailMetadata(),
      ]);
      if (!callLogRes.success || !metaRes.success || !trailRes.success) {
        setError("Failed to load device status. Check connection.");
        return;
      }
      setRows(((await callLogRes.json) || []) as CallLogRow[]);
      setMeta(((await metaRes.json) || []) as DeviceMeta[]);
      setTrails(((await trailRes.json) || []) as Trail[]);
      setLastFetch(Date.now());
    } catch (e) {
      setError("Network error while fetching device status.");
    } finally {
      setLoading(false);
    }
  }, [getDeviceCallLog, getDeviceMetadata, getTrailMetadata]);

  // Initial fetch + auto-refresh
  useEffect(() => {
    fetchAll();
    const refresh = setInterval(fetchAll, REFRESH_INTERVAL_MS);
    return () => clearInterval(refresh);
  }, [fetchAll]);

  // Tick the "now" clock once a second so the "N seconds ago" text updates
  // smoothly between full refreshes.
  useEffect(() => {
    const tick = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(tick);
  }, []);

  const trailNameById = new Map<number, string>();
  for (const t of trails) {
    if (t && typeof t.trail_id === "number" && t.trail_name) {
      trailNameById.set(t.trail_id, t.trail_name);
    }
  }

  const metaByDevice = new Map<string, DeviceMeta>();
  for (const m of meta) {
    if (m && m.device_id) metaByDevice.set(m.device_id, m);
  }

  // Merge: one row per device, prefer the call-log entry; fall back to
  // device-metadata-only if a device has been associated but never called in.
  const seen = new Set<string>();
  const merged: Array<{
    device_id: string;
    last_call_in?: number;
    trail_id?: number;
    battery?: number;
    rssi?: number;
    firmware_version?: string;
    record_count?: number;
  }> = [];

  for (const r of rows) {
    if (!r.device_id || seen.has(r.device_id)) continue;
    seen.add(r.device_id);
    const m = metaByDevice.get(r.device_id);
    merged.push({
      device_id: r.device_id,
      last_call_in: r.timestamp,
      trail_id: r.trail_id ?? m?.current_trail_id ?? 0,
      battery: r.battery ?? m?.battery,
      rssi: r.rssi,
      firmware_version: r.firmware_version,
      record_count: r.record_count,
    });
  }
  for (const m of meta) {
    if (!m.device_id || seen.has(m.device_id)) continue;
    merged.push({
      device_id: m.device_id,
      last_call_in: m.last_update,
      trail_id: m.current_trail_id ?? 0,
      battery: m.battery,
    });
  }

  // Sort: unassociated devices first (newly-installed devices typically
  // start unassigned, so this floats them to the top), then by most-recent
  // call-in within each group.
  merged.sort((a, b) => {
    const aUnassoc = !a.trail_id || a.trail_id === 0;
    const bUnassoc = !b.trail_id || b.trail_id === 0;
    if (aUnassoc !== bUnassoc) return aUnassoc ? -1 : 1;
    const aT = a.last_call_in ?? 0;
    const bT = b.last_call_in ?? 0;
    return bT - aT;
  });

  const lastFetchAge = Math.floor((now - lastFetch) / 1000);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: palette.bg,
        color: palette.text,
        fontFamily: "-apple-system, BlinkMacSystemFont, system-ui, sans-serif",
        padding: "16px",
        boxSizing: "border-box",
      }}
    >
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
        }}
      >
        <h1 style={{ fontSize: "20px", fontWeight: 600, margin: 0 }}>
          Install Check
        </h1>
        <button
          onClick={fetchAll}
          disabled={loading}
          style={{
            fontSize: "14px",
            padding: "8px 14px",
            background: loading ? "#cccccc" : "#1f6feb",
            color: "white",
            border: "none",
            borderRadius: "6px",
            fontWeight: 500,
          }}
        >
          {loading ? "..." : "Refresh"}
        </button>
      </header>

      <div
        style={{
          fontSize: "12px",
          color: palette.subtext,
          marginBottom: "16px",
        }}
      >
        {lastFetch === 0
          ? "Loading..."
          : `Updated ${lastFetchAge}s ago · auto-refreshing every ${REFRESH_INTERVAL_MS / 1000}s`}
      </div>

      {error && (
        <div
          style={{
            background: "#fde2e2",
            color: "#7a1a1a",
            padding: "12px",
            borderRadius: "6px",
            marginBottom: "16px",
            fontSize: "14px",
          }}
        >
          {error}
        </div>
      )}

      {merged.length === 0 && !loading && !error && (
        <div style={{ color: palette.subtext, fontSize: "14px" }}>
          No devices found.
        </div>
      )}

      {merged.map((d) => {
        const trailName = d.trail_id && d.trail_id !== 0
          ? trailNameById.get(d.trail_id) ?? `Trail ${d.trail_id}`
          : null;
        const age = d.last_call_in ? formatAge(d.last_call_in) : null;
        const accentColor = !age
          ? palette.dead
          : age.bucket === "fresh"
          ? palette.fresh
          : age.bucket === "stale"
          ? palette.stale
          : palette.dead;

        return (
          <div
            key={d.device_id}
            style={{
              background: palette.cardBg,
              border: `1px solid ${palette.cardBorder}`,
              borderLeft: `6px solid ${accentColor}`,
              borderRadius: "8px",
              padding: "14px 16px",
              marginBottom: "12px",
              boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
            }}
          >
            <div
              style={{
                fontFamily: "ui-monospace, SFMono-Regular, monospace",
                fontSize: "13px",
                color: palette.subtext,
                marginBottom: "6px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {d.device_id}
            </div>
            <div
              style={{
                fontSize: "16px",
                fontWeight: 600,
                marginBottom: "10px",
                color: trailName ? palette.text : palette.unassigned,
              }}
            >
              {trailName ? trailName : "Unassigned"}
            </div>

            <Row label="Last call-in" value={age ? age.text : "Never"} bold />
            <Row label="Battery" value={batteryDisplay(d.battery)} />
            <Row label="Signal" value={signalQuality(d.rssi)} />
            <Row
              label="Firmware"
              value={d.firmware_version ?? "—"}
            />
            <Row
              label="Last upload"
              value={
                d.record_count !== undefined
                  ? `${d.record_count} timestamp${d.record_count === 1 ? "" : "s"}`
                  : "—"
              }
            />
          </div>
        );
      })}
    </div>
  );
}

function Row({
  label,
  value,
  bold,
}: {
  label: string;
  value: string;
  bold?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        fontSize: "14px",
        marginBottom: "4px",
      }}
    >
      <span style={{ color: palette.subtext }}>{label}</span>
      <span style={{ fontWeight: bold ? 600 : 400 }}>{value}</span>
    </div>
  );
}
