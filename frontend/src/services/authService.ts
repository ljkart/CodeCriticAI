import api from "./axiosInstanceService";
import { jwtDecode } from "jwt-decode";
export interface LoginCredentials {
    username: string;
    password: string;
}


export interface AuthResponse {
    token: string;
    refreshToken?: string;
    user: {
        id: string;
        name: string;
    }
}

function isTokenExpired(token: string | null): boolean {
    if (!token) return true;
    try {
        // For CommonJS interop, jwt_decode may be a module with a default export
        const decode = typeof jwtDecode === 'function' ? jwtDecode : (jwtDecode as any).default;
        const { exp } = decode(token) as { exp: number };
        if (!exp) return true;
        return Date.now() >= exp * 1000;
    } catch {
        return true;
    }
}

export const loginUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    
    try {
        const response = await api.post<AuthResponse>(
           "/auth/login",
           credentials
        );
        // save token to OS secure storage
        await window.electronAPI.saveToken(response.data.token);
        if ('refreshToken' in response.data && response.data.refreshToken) {
            await window.electronAPI.saveRefreshToken(response.data.refreshToken);
        }
        return response.data;
    } catch (error: unknown) {
        if (typeof error === 'object' && error && 'response' in error) {
            const err = error as { response?: { data?: { message?: string; error?: string } } };
            if (err.response?.data?.message) {
                throw new Error(err.response.data.message);
            } else if (err.response?.data?.error) {
                throw new Error(err.response.data.error);
            }
        }
        throw new Error("Unexpected error, Login failed ");
    }
}

export const registerUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    
    try {
        const response = await api.post<AuthResponse>(
           "/auth/register",
           credentials
        );
        return response.data;

    } catch (error: unknown) {
        if (typeof error === 'object' && error && 'response' in error) {
            const err = error as { response?: { data?: { message?: string; error?: string } } };
            const message = err.response?.data?.message || err.response?.data?.error;
            throw new Error(message || 'Registration failed');
        }
        throw new Error('Registration failed');
    }
}

export const tryAutoLogin = async (): Promise<string | null> => {
    const accessToken = await window.electronAPI.getToken();
    if (accessToken && !isTokenExpired(accessToken)) {
        return accessToken;
    }
    // Try refresh token
    const refreshToken = await window.electronAPI.getRefreshToken?.();
    if (refreshToken && !isTokenExpired(refreshToken)) {
        try {
            // Send refresh token in the Authorization header, not in the body
            const response = await api.post("/auth/refresh", {}, {
                headers: { Authorization: `Bearer ${refreshToken}` },
            });
            const { token: newAccessToken, refreshToken: newRefreshToken } = response.data;
            await window.electronAPI.saveToken(newAccessToken);
            if (newRefreshToken) {
                await window.electronAPI.saveRefreshToken(newRefreshToken);
            }
            return newAccessToken;
        } catch (err) {
            // Refresh failed, treat as logged out
            return null;
        }
    }
    return null;
}


export const logoutUser = async () => {
    localStorage.removeItem("user");
    await window.electronAPI.deleteToken();
}
