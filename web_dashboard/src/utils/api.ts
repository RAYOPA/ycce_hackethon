export const API_URL = 'http://127.0.0.1:8000/api/v1';

export const fetchWithAuth = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('manrakshak_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Unauthorized, maybe clear token and redirect to login
    localStorage.removeItem('manrakshak_token');
    localStorage.removeItem('manrakshak_auth_user');
    window.location.href = '/login';
  }

  return response;
};
