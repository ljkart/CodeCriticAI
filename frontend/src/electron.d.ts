interface FileData {
    data: number[]; // Array of bytes that will be converted to Uint8Array
    type: string; // MIME type of the file
  }

interface ElectronAPI {
    saveToken: (token: string) => Promise<void>;
    saveRefreshToken(token: string): Promise<void>;
    getToken: () => Promise<string | null>;
    getRefreshToken: () => Promise<string | null>;
    deleteToken: () => Promise<void>;
    selectPath: () => Promise<string>;
    readFileStream: (filepath: string) => Promise<FileData>;

  }
  

  declare global {
    interface Window {
      electronAPI: ElectronAPI;
    }
  }

  

export {};

