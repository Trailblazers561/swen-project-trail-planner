const API_URL = import.meta.env.VITE_API_URL;
import { UserRole, Granularity } from "./lib/apiTypes";
import {refreshTokens} from "./cognito/authService";
import { isAuthenticated, isTokenExpired, getToken } from "@/Context";

export function TrailData() {
  /**
   * Get trail metadata (names, IDs, notes, etc.) 
   * @param trailIdList - Optional list of trail ids of trails to retrieve
   */
  async function getTrailMetadata(trailIdList?: number[]) {
    const queries: string[] = []
    if (trailIdList)
      trailIdList.forEach(id => {queries.push(`trail_id=${id}`)})
    const queryString = queries.length ? `?${queries.join("&")}` : "";

    return await request(`${API_URL}/trail_metadata${queryString}`, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /**
   * Get areas
   * @param areaList - Optional list of area names of areas to retrieve
   */
  async function getAreaMetadata(areaList?: string[]) {
    const queries: string[] = []
    if (areaList)
      areaList.forEach(area => {queries.push(`area=${encodeURIComponent(area)}`)})
    const queryString = queries.length ? `?${queries.join("&")}` : "";

    return await request(`${API_URL}/areas${queryString}`, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /** 
   * Get device metadata (battery, current trail, etc.) 
   * @param trailIdList - Optional list of trail ids of trails to retrieve
   */
  async function getDeviceMetadata(deviceIdList?: number[]) {
    const queries: string[] = []
    if (deviceIdList)
      deviceIdList.forEach(id => {queries.push(`device_id=${id}`)})
    const queryString = queries.length ? `?${queries.join("&")}` : "";

    return await request(`${API_URL}/device_metadata${queryString}`, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /**
   * Get device logs for specific trails between two dates
   * @param trailIdList array of trail ids of trails to retrieve data for
   * @param startDate ISO format date for earliest date to retrieve
   * @param endDate ISO format date for earliest date to retrieve
   * Note: If your date range includes partials for the granularity it will not have all the counts for that
   * (eg. week data with startDate of Friday will only retrieve the Friday/Saturday data for that week)
   */
  async function getTrailLogs(trailIdList: number[], startDate: Date, endDate: Date, granularity: Granularity) {
    const trailIdQueries: string[] = []
    trailIdList.forEach(id => {trailIdQueries.push(`trail_id=${id}`)})
    const trailIdQueryString = trailIdQueries.length ? `&${trailIdQueries.join("&")}` : "";
    if (granularity == Granularity.Year) granularity = Granularity.Month;

    const url = `${API_URL}/trail_data?start_time=${startDate.toISOString()}&end_time=${endDate.toISOString()}&granularity=${granularity}${trailIdQueryString}`;
    return await request(url, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /**
   * Update trail metadata (name and/or area)
   * @param trailId - The ID of the trail to update
   * @param trailName - new name for the trail
   * @param area - Optional area name to assign the trail to
   */
  async function updateTrailMetadata(trailId: number, trailName?: string, area?: string) {
    return await request(`${API_URL}/trail_metadata`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        trail_id: trailId,
        name: trailName,
        area_name: area,
      }),
    });
  }

  /**
   * Update device trail association
   * @param deviceId - The device ID to update
   * @param trailId - The trail ID to associate the device with
   * @param dateInstalled - Optional: Date the device was installed on the new trail
   * @param dateRemoved - Optional: Date the device was removed from the old trail
   */
  async function updateDeviceTrailAssociation(deviceId: string, trailId: number, dateInstalled?: Date, dateRemoved?: Date) {
    const payload: Record<string, any> = {
      device_id: deviceId,
      trail_id: trailId,
    }
    if (dateInstalled)
      payload.date_installed = dateInstalled.toISOString();
    if (dateRemoved)
      payload.date_removed = dateRemoved.toISOString();

    return await request(`${API_URL}/device_metadata`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify(payload),
    });
  }

  /**
   * Create a new trail
   * @param trailName - The name of the trail to create
   * @param area - Optional area name to assign the trail to
   * @param notes - Optional notes for the created trail
   * @param latitude - Optional latitude of the trail head
   * @param longitude - Optional longitude of the trail head
   * @param dateActivated - Optional date trail was activated, defaults to current time if not specified
   */
  async function createTrail(trailName: string, area?: string, notes?: string, latitude?: number, longitude?: number, dateActivated?: Date) {
    const payload: Record<string, any> = {
      trail_name: trailName
    }
    if (area)
      payload.area_name = area;
    if (notes)
      payload.notes = notes;
    if (latitude)
      payload.latitude = latitude;
    if (longitude)
      payload.longitude = longitude;
    if (dateActivated)
      payload.date_activated = dateActivated.toISOString();
    return await request(`${API_URL}/trail_metadata`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify(payload)
    });
  }

  /**
   * Retires a trail and all associated data
   * @param trailId - The ID of the trail to retire
   */
  async function retireTrail(trailId: number) {
    return await request(`${API_URL}/trail_metadata`, {
      method: "DELETE",
      headers: await authHeaders(),
      body: JSON.stringify({
        trail_id: trailId,
      }),
    });
  }

  /**
   * Create a new area (NOT Implemented)
   * @param areaName - The name of the area to create
   * @param trailIds - Optional array of trail IDs to include in the area
   */
  async function createArea(areaName: string, trailIds: number[] = []) {
    return await request(`${API_URL}/areas`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify({
        area_name: areaName,
        trail_ids: trailIds,
      }),
    });
  }

  /**
   * Update a area (rename or change trail IDs) (NOT Implemented)
   * @param oldAreaName - The current name of the area
   * @param newAreaName - Optional new name for the area
   * @param trailIds - Optional array of trail IDs to update in the area
   */
  async function updateArea(oldAreaName: string, newAreaName?: string, trailIds?: number[]) {
    return await request(`${API_URL}/areas`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        original_area_name: oldAreaName,
        new_area_name: newAreaName,
        trail_ids: trailIds,
      }),
    });
  }

  /**
   * Delete a area
   * @param areaName - The name of the area to delete
   */
  async function deleteArea(areaName: string) {
    return await request(`${API_URL}/areas`, {
      method: "DELETE",
      headers: await authHeaders(),
      body: JSON.stringify({
        area_name: areaName,
      }),
    });
  }

  /**
   * Gets csv thats created from the database
   * @param trailIdList - List of trail IDs to include in the csv
   * @param startDate - ISO format date for earliest date to include in the csv
   * @param endDate - ISO format date for latest date to include in the csv
   * @param granularity - Optional granularity setting for output, can be hourly, day, week, or month
   */
  async function exportCSV(trailIdList: number[], startDate: Date, endDate: Date, granularity?: Granularity) {
    const queries: string[] = []
    trailIdList.forEach(id => {queries.push(`trail_id=${id}`)})
    queries.push(`start_time=${startDate.toISOString()}`)
    queries.push(`end_time=${endDate.toISOString()}`)
    if (granularity)
      queries.push(`granularity=${granularity}`)
    const queryString = queries.length ? `?${queries.join("&")}` : "";

    return await request(`${API_URL}/csv${queryString}`, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

      /**
   * Takes in a .csv file and adds it to the database
   * @param csvFile - Csv file itself
   */
      async function importCSV(csvFile: File) {

        const { uploadUrl, s3FilePath } = (await request(`${API_URL}/csv-url`, {
          method: "GET",
          headers: await authHeaders(),
        }))["json"];
    
        await fetch(uploadUrl, {
          method: "PUT",
          body: await csvFile.arrayBuffer(),
        });
    
        return await request(`${API_URL}/csv`, {
          method: "POST",
          headers: await authHeaders(),
          body: JSON.stringify({
            csv_file_path: s3FilePath,
          }),
        });
      }

  /**
   * Gets a list of cognito users
   * @param maxCount - Optional max number of users to retrieve; defaults to 99
   * @param targetUserRole - Optional List of trail IDs to include in the csv
   */
  async function getUsers(maxCount?: number, targetUserRole?: UserRole) {
    //?trails=${trailsParam}&start=${startdate}&end=${enddate}
    const queries: string[] = []
    if (maxCount !== undefined)
      queries.push(`max_count=${maxCount.toString()}`)
    if (targetUserRole !== undefined)
      queries.push(`target_user_role=${targetUserRole}`)
    const queryString = queries.length ? `?${queries.join("&")}` : "";

    return await request(`${API_URL}/users${queryString}`, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /**
   * Updates cognito users role
   * @param targetUserId - User ID for the user that will be updated
   * @param targetUserRole - UserRole to set the given user to
   */
  async function updateUserRole(targetUserId: string, targetUserRole: UserRole) {
    return await request(`${API_URL}/users`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify({
        target_user_id: targetUserId,
        target_user_role: targetUserRole
      }),
    });
  }



  return {
    getTrailMetadata,
    getAreaMetadata,
    getDeviceMetadata,
    getTrailLogs,
    updateTrailMetadata,
    createTrail,
    updateDeviceTrailAssociation,
    retireTrail,
    createArea,
    updateArea,
    deleteArea,
    exportCSV,
    importCSV,
    getUsers,
    updateUserRole,
  };
}

let refreshing: Promise<any | undefined>  | null = null;
async function authHeaders() {
  if (!isAuthenticated())
    return {Authorization: `Bearer `, "Content-Type": "application/json"};

  // If token is expired refresh it
  if (isTokenExpired()) {
    // If we haven't started a refresh then start a refresh
    if (!refreshing)
        refreshing = refreshTokens().finally(() => {refreshing = null;});

    // Wait for refresh to finish
    await refreshing;
  }

  return {
    Authorization: `Bearer ${getToken()}`,
    "Content-Type": "application/json",
  };
}

type RequestResult = { json: any; success: boolean };

/**
 * Make an API request
 * @param url - The URL to make the request to
 * @param options - Optional fetch request options (method, headers, body, etc.)
 * @returns Promise resolving to a RequestResult with json data and success status
 */
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