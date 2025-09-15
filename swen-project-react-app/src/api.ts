const API_URL = import.meta.env.VITE_API_URL;

export function TrailData() {
  /**
   * Get all trail metadata (names, IDs, etc.)
   */
  async function getAll() {
    return await request(`${API_URL}/trail_metadata`, {
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
    const trailParam = Array.isArray(trailIDs) ? trailIDs.join(",") : trailIDs;
    const url = `${API_URL}/trail_data?trail_id=${trailParam}&start=${startdate}&end=${enddate}`;
    console.log("Fetching trail logs:", url);
    return await request(url, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  /**
   * Get all trail logs between two dates (no filtering by trail)
   */
  async function getAllLogsBetweenDates(startdate: number, enddate: number) {
    const url = `${API_URL}/trail_data?start=${startdate}&end=${enddate}`;
    console.log("Fetching all logs:", url);
    return await request(url, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  /**
   * Get device metadata (latest battery, current trail per device)
   */
  async function getDeviceMetadata() {
    return await request(`${API_URL}/device_metadata`, {
      method: "GET",
      headers: authHeaders(),
    });
  }

  return {
    getAll,
    getTrailLogsBetweenDates,
    getAllLogsBetweenDates,
    getDeviceMetadata,
  };
}

/**
 * Helper to add auth headers
 */
function authHeaders() {
  return {
    Authorization: `Bearer ${sessionStorage.getItem("idToken")}`,
    "Content-Type": "application/json",
  };
}

type RequestResult = {
  json: object;
  success: boolean;
};

/**
 * Fetch helper method.
 */
async function request(url: string, options?: RequestInit): Promise<RequestResult> {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    return {
      json: data,
      success: response.ok,
    };
  } catch (e) {
    console.error("API request failed:", e);
    return {
      json: {},
      success: false,
    };
  }
}