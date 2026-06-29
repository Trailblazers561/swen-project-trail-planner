const API_URL = import.meta.env.VITE_API_URL;
import { UserRole, Granularity, HeatmapAlgorithm } from "./lib/apiTypes";
import {refreshTokens} from "./cognito/authService";
import { isAuthenticated, isTokenExpired, getToken } from "@/AuthContext";

export function TrailData() {
  /**
   * Get trail metadata (names, IDs, notes, etc.) 
   * @param trailIdList - Optional list of trail ids of trails to retrieve
   * @param retired - Optional bool to retrieve retired trails or unretired trails
   */
  async function getTrailMetadata(trailIdList?: number[], retired?: boolean) {
    const queries: string[] = []
    if (trailIdList)
      trailIdList.forEach(id => {queries.push(`trail_id=${id}`)})
    if (retired)
      queries.push("retired");
    const queryString = queries.length ? `?${queries.join("&")}` : "";
    return await request(`${API_URL}/trail_metadata${queryString}`, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /**
   * Get areas
   * @param areaList - Optional list of area names of areas to retrieve
   * @param retired - Optional bool to retrieve retired trails or unretired trails
   */
  async function getAreaMetadata(areaList?: string[], retired?: boolean) {
    const queries: string[] = []
    if (areaList)
      areaList.forEach(area => {queries.push(`name=${encodeURIComponent(area)}`)})
    if (retired)
      queries.push("retired");
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
   * Get device logs for specific devices
   * @param deviceIdList array of device ids of devices to retrieve data for
   * @param limit Optional limit number of logs to retrieve for each device, defautls to -5
   */
  async function getDeviceLogs(deviceIdList: number[], limit?: number) {
    const queries: string[] = []
    deviceIdList.forEach(id => {queries.push(`device_id=${id}`)})
    if (limit)
      queries.push(`limit=${limit}`)
    const queryString = queries.length ? `?${queries.join("&")}` : "";

    const url = `${API_URL}/device_management${queryString}`;
    return await request(url, {
      method: "GET",
      headers: await authHeaders(),
    });
  }

  /**
   * Get device logs for specific trails between two dates
   * @param trailIdList array of trail ids of trails to retrieve data for
   * @param startDate ISO format date for earliest date to retrieve
   * @param endDate ISO format date for earliest date to retrieve
   * @param heatmapAlgorithm Optional HeatmapAlgorithm for which algorithm to use, defaults to absolute
   */
  async function getHeatmapData(trailIdList: number[], startDate: Date, endDate: Date, heatmapAlgorithm?: HeatmapAlgorithm) {
    const trailIdQueries: string[] = []
    trailIdList.forEach(id => {trailIdQueries.push(`trail_id=${id}`)})
    const trailIdQueryString = trailIdQueries.length ? `&${trailIdQueries.join("&")}` : "";
    const algorithmQueryString = heatmapAlgorithm ? `&algorithm=${heatmapAlgorithm}` : "";

    const url = `${API_URL}/heatmap?start_time=${startDate.toISOString()}&end_time=${endDate.toISOString()}${algorithmQueryString}${trailIdQueryString}`;
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
  async function updateTrailMetadata(trailId: number, trailName?: string, area?: string, notes?: string, latitude?: number, longitude?: number) {
    const payload: Record<string, any> = {trail_id: trailId};
    if (trailName)
      payload.name = trailName;
    if (area)
      payload.area_name = area;
    if (notes)
      payload.notes = notes;
    if (latitude)
      payload.latitude = latitude;
    if (longitude)
      payload.longitude = longitude;

    return await request(`${API_URL}/trail_metadata`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify(payload),
    });
  }

  /**
   * Update device trail association
   * @param deviceId - The device ID to update
   * @param trailId - The trail ID to associate the device with
   * @param dateInstalled - Optional: Date the device was installed on the new trail
   * @param dateRemoved - Optional: Date the device was removed from the old trail
   */
  async function updateDeviceTrailAssociation(deviceId: number, trailId: number, dateInstalled?: Date, dateRemoved?: Date) {
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
   * Creates a device
   * @param deviceName - The name of the device to create
   * @param deviceSerial - The serial of the device to create
   */
  async function createDevice(deviceName: string, deviceSerial: string) {
    return await request(`${API_URL}/registration`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify({
        device_name: deviceName,
        device_serial: deviceSerial
      }),
    });
  }

  /**
   * Updates a device
   * @param registrationId - The registration id to update
   * @param deviceName - Optional The name of the device to update
   * @param deviceSerial - Optional The serial of the device to update
   */
  async function updateRegistration(registrationId: number, deviceName?: string, deviceSerial?: string) {
    return await request(`${API_URL}/registration`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        registration_id: registrationId,
        device_name: deviceName,
        device_serial: deviceSerial
      }),
    });
  }

  /**
   * Updates a device
   * @param registrationId - The registration id to update
   */
  async function deleteRegistration(registrationId: number) {
    return await request(`${API_URL}/registration`, {
      method: "DELETE",
      headers: await authHeaders(),
      body: JSON.stringify({
        registration_id: registrationId
      }),
    });
  }

  /**
   * Archives/Unarchives a device
   * @param deviceId - The device id to archive
   * @param isArchived - Whether or not to archive a device
   */
  async function archiveDevice(deviceId: number, isArchived: boolean) {
    return await request(`${API_URL}/archive`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        device_id: deviceId,
        is_archived: isArchived
      }),
    });
  }

  /**
   * Blocks/Unblocks a device
   * @param deviceId - The device id to archive
   * @param isBlocked - Whether or not to archive a device
   */
  async function blockDevice(deviceId: number, isBlocked: boolean) {
    return await request(`${API_URL}/block`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        device_id: deviceId,
        is_blocked: isBlocked
      }),
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
      name: trailName
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
   * @param dateRetired - Optional date to set when it was retired
   */
  async function retireTrail(trailId: number, dateRetired?: Date) {
    return await request(`${API_URL}/trail_metadata`, {
      method: "DELETE",
      headers: await authHeaders(),
      body: JSON.stringify({
        trail_id: trailId,
        date_retired: dateRetired?.toISOString()
      }),
    });
  }

  /**
   * Create a new area
   * @param areaName - The name of the area to create
   * @param trailIds - Optional array of trail IDs to include in the area
   */
  async function createArea(areaName: string, trailIds: number[] = []) {
    return await request(`${API_URL}/areas`, {
      method: "POST",
      headers: await authHeaders(),
      body: JSON.stringify({
        name: areaName,
        trail_ids: trailIds,
      }),
    });
  }

  /**
   * Update a area (rename or change trail IDs)
   * @param oldName - The current name of the area
   * @param newName - Optional new name for the area
   * @param trailIds - Optional array of trail IDs to update in the area
   */
  async function updateArea(oldName: string, newName?: string, trailIds?: number[]) {
    return await request(`${API_URL}/areas`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        original_name: oldName,
        new_name: newName,
        trail_ids: trailIds,
      }),
    });
  }

  /**
   * Retire an area
   * @param areaName - The name of the area to retire
   */
  async function retireArea(areaName: string) {
    return await request(`${API_URL}/areas`, {
      method: "DELETE",
      headers: await authHeaders(),
      body: JSON.stringify({
        name: areaName
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

        const { uploadUrl, s3FilePath } = (await request(`${API_URL}/csv_url`, {
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
   * Updates cognito user's role
   * @param targetUsername - Username for the user that will be updated
   * @param targetUserRole - UserRole to set the given user to
   */
  async function updateUserRole(targetUsername: string, targetUserRole: UserRole) {
    return await request(`${API_URL}/users`, {
      method: "PUT",
      headers: await authHeaders(),
      body: JSON.stringify({
        target_username: targetUsername,
        target_user_role: targetUserRole
      }),
    });
  }

  /**
   * Bans cognito user
   * @param targetUsername - Username for the user that will be banned
   */
  async function banUser(targetUsername: string) {
    return await request(`${API_URL}/users`, {
      method: "DELETE",
      headers: await authHeaders(),
      body: JSON.stringify({
        target_username: targetUsername
      }),
    });
  }



  return {
    getTrailMetadata,
    getAreaMetadata,
    getDeviceMetadata,
    createDevice,
    updateRegistration,
    deleteRegistration,
    archiveDevice,
    blockDevice,
    getTrailLogs,
    getDeviceLogs,
    getHeatmapData,
    updateTrailMetadata,
    createTrail,
    updateDeviceTrailAssociation,
    retireTrail,
    createArea,
    updateArea,
    retireArea,
    exportCSV,
    importCSV,
    getUsers,
    updateUserRole,
    banUser,
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