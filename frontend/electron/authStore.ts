import keytar from 'keytar';

const SERVICE_NAME = "ai-code-reviewer";
const ACCOUNT_NAME = "auth-token";
const REFRESH_ACCOUNT_NAME = "refresh-auth-token";


interface AuthStore {
    saveToken(token: string): Promise<void>;
    saveRefreshToken(token: string): Promise<void>;
    getToken(): Promise<string | null>;
    getRefreshToken(): Promise<string | null>;
    removeToken(): Promise<void>;
}


export const saveToken = async function(token: string): Promise<void> {
    console.log("Token saved!")
    await keytar.setPassword(SERVICE_NAME, ACCOUNT_NAME, token);
};

export const saveRefreshToken = async function(token: string): Promise<void> {
    console.log("refresh-Token saved!")
    await keytar.setPassword(SERVICE_NAME, REFRESH_ACCOUNT_NAME, token);
};


export const getToken = async function(): Promise<string | null> {
    console.log("Token asked!")
    return await keytar.getPassword(SERVICE_NAME, ACCOUNT_NAME);
};

export const getRefreshToken = async function(): Promise<string | null> {
    console.log("Refresh-Token asked!")
    return await keytar.getPassword(SERVICE_NAME, REFRESH_ACCOUNT_NAME);
};


export const deleteToken = async function(): Promise<void> {
    console.log("token deleted..")
    await keytar.deletePassword(SERVICE_NAME, ACCOUNT_NAME);
    await keytar.deletePassword(SERVICE_NAME, REFRESH_ACCOUNT_NAME);
};



