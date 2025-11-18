const API_URL = import.meta.env.VITE_API_URL;

export function TrailData() {
  /**
   * Get all trail metadata (names, IDs, etc.) 
   */
  async function getTrailMetadata() {
    return await request(`${API_URL}/trail_metadata`, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  /**
   * Get all trail groups 
   */
  async function getTrailGroups() {
    return await request(`${API_URL}/trail_groups`, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  /** 
   * Get device metadata (battery, current trail, etc.) 
   */
  async function getDeviceMetadata() {
    return await request(`${API_URL}/device_metadata`, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  /**
   * Get device logs for specific trails between two dates
   * @param startdate ISO or epoch start date
   * @param enddate ISO or epoch end date
   * @param trailIDs number or array of trail IDs
   */
  async function getTrailLogsBetweenDates(startdate: number, enddate: number, trailIDs: number | number[]) {
    const trailsParam = Array.isArray(trailIDs) ? trailIDs.join(",") : trailIDs;
    const url = `${API_URL}/trail_data?trails=${trailsParam}&start=${startdate}&end=${enddate}`;
    return await request(url, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  /** Get all logs between two dates
   * @param startdate ISO or epoch start date
   * @param enddate ISO or epoch end date
   */
  async function getAllLogsBetweenDates(startdate: number, enddate: number) {
    const url = `${API_URL}/trail_data?start=${startdate}&end=${enddate}`;
    return await request(url, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  return {
    getTrailMetadata,
    getTrailGroups,
    getDeviceMetadata,
    getTrailLogsBetweenDates,
    getAllLogsBetweenDates,
  };
}

function authHeaders() {
  return {
    Authorization: `Bearer ${sessionStorage.getItem("idToken")}`,
    "Content-Type": "application/json",
  };
}

type RequestResult = { json: any; success: boolean };

async function request(url: string, options?: RequestInit): Promise<RequestResult> {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    return { json: data, success: response.ok };
  } catch (e) {
    console.error("API request failed:", e);
    return { json: {}, success: false };
  }
}