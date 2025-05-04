import keytar from 'keytar';

const SERVICE_NAME = "ai-code-reviewer";
const ACCOUNT_NAME = "auth-token";
const REFRESH_ACCOUNT_NAME = "refresh-auth-token";


export const saveToken = async function(token: string): Promise<void> {
    await keytar.setPassword(SERVICE_NAME, ACCOUNT_NAME, token);
};

export const saveRefreshToken = async function(token: string): Promise<void> {
    await keytar.setPassword(SERVICE_NAME, REFRESH_ACCOUNT_NAME, token);
};


export const getToken = async function(): Promise<string | null> {
    return await keytar.getPassword(SERVICE_NAME, ACCOUNT_NAME);
};

export const getRefreshToken = async function(): Promise<string | null> {
    return await keytar.getPassword(SERVICE_NAME, REFRESH_ACCOUNT_NAME);
};


export const deleteToken = async function(): Promise<void> {
    await keytar.deletePassword(SERVICE_NAME, ACCOUNT_NAME);
    await keytar.deletePassword(SERVICE_NAME, REFRESH_ACCOUNT_NAME);
};



