import api from "./axiosInstanceService";
import axios from "axios";

export const getFileHistories = async () => {
    const token = await window.electronAPI.getToken();
    try{
        const reviews = await api.get("/review/history",
            {
                headers : {Authorization: `Bearer ${token}`}
            }
        )
        return reviews.data

    } catch (error: unknown) {
        if (typeof error === 'object' && error && 'response' in error) {
            const err = error as { response?: { data?: { error?: string } } };
            throw new Error(err.response?.data?.error || "Failed to fetch file histories");
        }
        throw new Error("Failed to fetch file histories");
    }

}

export const getReviewByFilenameAndVersion = async (filename: string, version: number) => {
    const token = await window.electronAPI.getToken();

    try {
        const reviews = await api.get(`/review/file`,
            {
                headers : {Authorization: `Bearer ${token}`},
                params: {
                    filename,
                     version
                }
            },
        )
        return reviews.data

    } catch (error: any) {
        const message = error.response?.data?.message || error.response?.data?.error;
        throw new Error(message);
    }

}

export const removeReviewByFilenameVersion = async (filename: string, version: number) => {
    const token = await window.electronAPI.getToken();
    try {
        const response = await api.post(`/review/remove`,
            null,
            {
            
                headers : {Authorization: `Bearer ${token}`},
                params: {
                    filename,
                    version
                }
            }
        );
        
        return response.data
    } catch (error: any) {
        if (axios.isAxiosError(error) && error.response) {
            throw error
        }
    }
    

}

export const doFileReview = async (filepath: string) => {
    const token = await window.electronAPI.getToken();
    try {
        const fileData = await window.electronAPI.readFileStream(filepath);
        const fileBlob = new Blob([new Uint8Array(fileData.data)], {
            type: fileData.type
        });

        const filename = filepath.replace(/^.*[\\/]/, "")
        const formData = new FormData();
        formData.append("filepath", fileBlob, filename)
        const reviews = await api.post(`/review/upload`,
            formData,
            {
                headers : {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "file"
                },
            },
        )
        return reviews.data

    } catch (error: any) {
        throw new Error(error);
    }
    
}
