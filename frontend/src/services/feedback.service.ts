import api from "@/lib/api"
import type { AxiosError } from "axios"

export interface FeedbackRequest {
  text: string
  model_prediction: "left" | "center" | "right"
  model_confidence: number
  is_correct: boolean
  actual_label: "left" | "center" | "right"
}

export interface FeedbackResponse {
  id: string
  text: string
  model_prediction: string
  is_correct: boolean
  actual_label: string
  user_id: string
  created_at: string
}

export interface ApiError {
  detail: string
}

class FeedbackService {
  async submitFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
    const response = await api.post<FeedbackResponse>("/api/feedback", feedback)
    return response.data
  }

  getErrorMessage(error: unknown): string {
    const axiosError = error as AxiosError<ApiError>
    return axiosError.response?.data?.detail || "Failed to submit feedback. Please try again."
  }
}

export const feedbackService = new FeedbackService()
export default feedbackService
