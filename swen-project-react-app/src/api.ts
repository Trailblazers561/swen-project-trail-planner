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

  /**
   * Update trail metadata (name and/or trail group)
   * @param trailId - The ID of the trail to update
   * @param trailName - Optional new name for the trail
   * @param trailGroup - Optional trail group name to assign the trail to
   */
  async function updateTrailMetadata(trailId: number, trailName?: string, trailGroup?: string) {
    return await request(`${API_URL}/trail_metadata`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        trail_id: trailId,
        trail_name: trailName,
        trail_group: trailGroup,
      }),
    });
  }

  /**
   * Update device trail association
   * @param deviceId - The device ID to update
   * @param trailId - The trail ID to associate the device with
   */
  async function updateDeviceTrailAssociation(deviceId: string, trailId: number) {
    return await request(`${API_URL}/device_metadata`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        device_id: deviceId,
        trail_id: trailId,
      }),
    });
  }

  /**
   * Create a new trail
   * @param trailName - The name of the trail to create
   * @param trailGroup - Optional trail group name to assign the trail to
   */
  async function createTrail(trailName: string, trailGroup?: string) {
    return await request(`${API_URL}/trail_metadata`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        trail_name: trailName,
        trail_group: trailGroup,
      }),
    });
  }

  /**
   * Delete a trail and all associated data
   * @param trailId - The ID of the trail to delete
   */
  async function deleteTrail(trailId: number) {
    return await request(`${API_URL}/trail_metadata`, {
      method: "DELETE",
      headers: authHeaders(),
      body: JSON.stringify({
        trail_id: trailId,
      }),
    });
  }

  /**
   * Create a new trail group
   * @param groupName - The name of the trail group to create
   * @param trailIds - Optional array of trail IDs to include in the group
   */
  async function createTrailGroup(groupName: string, trailIds: number[] = []) {
    return await request(`${API_URL}/trail_groups`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        group_name: groupName,
        trail_ids: trailIds,
      }),
    });
  }

  /**
   * Update a trail group (rename or change trail IDs)
   * @param oldGroupName - The current name of the trail group
   * @param newGroupName - Optional new name for the trail group
   * @param trailIds - Optional array of trail IDs to update in the group
   */
  async function updateTrailGroup(oldGroupName: string, newGroupName?: string, trailIds?: number[]) {
    return await request(`${API_URL}/trail_groups`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        old_group_name: oldGroupName,
        new_group_name: newGroupName,
        trail_ids: trailIds,
      }),
    });
  }

  /**
   * Delete a trail group
   * @param groupName - The name of the trail group to delete
   */
  async function deleteTrailGroup(groupName: string) {
    return await request(`${API_URL}/trail_groups`, {
      method: "DELETE",
      headers: authHeaders(),
      body: JSON.stringify({
        group_name: groupName,
      }),
    });
  }

  /**
   * Gets csv thats created from the database
   * @param trailIdList - Optional List of trail IDs to include in the csv
   * @param startDate - Optional ISO format date for earliest date to include in the csv
   * @param endDate - Optional ISO format date for latest date to include in the csv
   */
  async function exportCSV(trailIdList: number[], startDate?: string, endDate?: string) {
    return await request(`${API_URL}/csv`, {
      method: "GET",
      headers: authHeaders(),
      body: JSON.stringify({
        trail_id_list: trailIdList,
        start_date: startDate,
        end_date: endDate,
      }),
    });
  }

    /**
   * Takes in a .csv file and adds it to the database
   * @param csvFile - Csv file itself
   */
  async function importCSV(csvFile: File) {

    const { uploadUrl, s3FilePath } = await request(`${API_URL}/csv/csv-url`, {
      method: "GET",
      headers: authHeaders(),
    });

    await fetch(uploadUrl, {
      method: "PUT",
      body: csvFile
    })

    return await request(`${API_URL}/csv`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        csv_file_path: s3FilePath,
      }),
    });
  }

  return {
    getTrailMetadata,
    getTrailGroups,
    getDeviceMetadata,
    getTrailLogsBetweenDates,
    getAllLogsBetweenDates,
    updateTrailMetadata,
    createTrail,
    updateDeviceTrailAssociation,
    deleteTrail,
    createTrailGroup,
    updateTrailGroup,
    deleteTrailGroup,
    exportCSV,
    importCSV,
  };
}

function authHeaders() {
  return {
    Authorization: `Bearer ${sessionStorage.getItem("idToken")}`,
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