const API_URL = import.meta.env.VITE_API_URL

export function TrailData(){
  async function getAll(){
    return await request(API_URL + '/trail_data/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('idToken')}`,
        'Content-Type': 'application/json',
      },
      body: null,
    });
  }

  return {
    getAll
  }
}

type RequestResult = {
  json: object;
  success: boolean;
};

/**
 * Fetch helper method.
 * @param url Url to Reach
 * @param options CRUD options
 * @returns
 */
async function request(
    url: string,
    options?: RequestInit
  ): Promise<RequestResult> {
    try {
      const response = await fetch(url, options);
      const data = await response.json();
      return {
        json: data,
        success: true,
      };
    } catch (e) {
      console.error(e);
      return {
        json: {},
        success: false,
      };
    }
  }