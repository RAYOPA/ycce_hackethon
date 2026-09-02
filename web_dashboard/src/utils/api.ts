export const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  let token = localStorage.getItem('manrakshak_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  let response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Attempt token refresh if refresh_token exists
    const refreshToken = localStorage.getItem('manrakshak_refresh_token');
    if (refreshToken) {
      try {
        const refreshResp = await fetch(`${API_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${refreshToken}` },
        });
        if (refreshResp.ok) {
          const data = await refreshResp.json();
          localStorage.setItem('manrakshak_token', data.access_token);
          // Retry original request
          headers['Authorization'] = `Bearer ${data.access_token}`;
          response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers,
          });
          return response;
        }
      } catch (e) {
        // Fallthrough to logout
      }
    }
    
    // Unauthorized, maybe clear token and redirect to login
    localStorage.removeItem('manrakshak_token');
    localStorage.removeItem('manrakshak_refresh_token');
    localStorage.removeItem('manrakshak_auth_user');
    window.location.href = '/login';
  }

  return response;
};
