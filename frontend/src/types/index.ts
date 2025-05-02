interface Review {
    code: string;
    line_number: number;
    review: string;
}

interface ReviewResponse {
    created_at: string;
    filename: string;
    language: string;
    refactored_code: string;
    reviews: Review[];
    version: number;

}

interface FileVersion {
    id: number;
    version: number;
    created_at: string;
    has_previous: boolean;
  }

interface ToastDataMessage {
    message: string;
    type: string;
}
  

interface FileData {
    filename: string;
    version: number;
  }
