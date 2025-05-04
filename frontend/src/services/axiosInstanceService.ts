import axios from "axios";

let isRefreshing = false;
type FailedQueueItem = { resolve: (token: string | null) => void; reject: (error: unknown) => void };
let failedQueue: FailedQueueItem[] = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const api = axios.create({
    baseURL: "/api",
    headers: {
        "Content-Type" : "application/json",
    },

});

// api.interceptors.request.use(
//     (config) => {
//         const token = localStorage.getItem('token');
//         if (token) {
//             config.headers.Authorization = `Bearer ${token}`
//         }
//         return config;
//     }, 
//     (error) => Promise.reject(error)
// );

// Attach token to every request
api.interceptors.request.use(
    async (config) => {
      const token = await window.electronAPI.getToken(); // fetch from secure storage
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  api.interceptors.response.use(
    (response) => response,
    async (error: any) => {
      const originalRequest = error.config || error;

      // Handle both 401 and 422 as possible auth/token errors
      if ((error.response?.status === 401 || error.response?.status === 422) && !originalRequest._retry) {
        originalRequest._retry = true;

        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          }).then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          });
        }

        isRefreshing = true;

        try {
          const refreshToken = await window.electronAPI.getRefreshToken();
          const response = await api.post("/auth/refresh", {}, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });
          const newToken = response.data?.token;
          if (!newToken) {
            throw new Error("No token received on refresh.");
          }
          await window.electronAPI.saveToken(newToken);
          api.defaults.headers.common["Authorization"] = `Bearer ${newToken}`;
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          processQueue(null, newToken);
          return api(originalRequest);
        } catch (err) {
          processQueue(err, null);
          localStorage.removeItem("user");
          await window.electronAPI.deleteToken(); // Clean up secure token
          window.location.href = "/login";        // Redirect to login
          return Promise.reject(err);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    }
  );
  

export default api;
