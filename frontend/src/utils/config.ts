// API URL configuration
export const API_BASE_URL =
  import.meta.env.MODE === 'production' ? 'https://chronixly.com/api' : 'http://localhost:5000/api'
