interface ElectronAPI {
    saveToken: (token: string) => Promise<void>;
    saveRefreshToken(token: string): Promise<void>;
    getToken: () => Promise<string | null>;
    getRefreshToken: () => Promise<string | null>;
    deleteToken: () => Promise<void>;
    selectPath: () => Promise<string> | null;
  }
  
  declare global {
    interface Window {
      electronAPI: ElectronAPI;
    }
  }

  