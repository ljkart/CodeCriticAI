import api from "./axiosInstanceService";


export interface LoginCredentials {
    username: string;
    password: string;
}


export interface AuthResponse {
    token: string;
    user: {
        id: string;
        name: string;
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
        console.log(response)
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
    return await window.electronAPI.getToken();
}


export const logoutUser = async () => {
    localStorage.removeItem("user");
    await window.electronAPI.deleteToken();
    console.log("Token deletion einvodke from front")
}
