import type { AxiosError } from "axios"
import api from "@/lib/api"

export interface ClassificationResult {
  prediction: "LEFT" | "CENTER" | "RIGHT"
  confidence: number
  probabilities: {
    left: number
    center: number
    right: number
  }
}

export interface ClassifyTextRequest {
  text: string
}

export interface ClassifyTextResponse {
  prediction: string
  confidence: number
  probabilities: {
    left: number
    center: number
    right: number
  }
}

export interface ApiError {
  detail: string
}

class ClassifyService {
  async classifyText(text: string): Promise<ClassificationResult> {
    const response = await api.post<ClassifyTextResponse>("/api/classify", { text })

    return {
      prediction: response.data.prediction.toUpperCase() as "LEFT" | "CENTER" | "RIGHT",
      confidence: response.data.confidence,
      probabilities: response.data.probabilities,
    }
  }

  async classifyFile(file: File): Promise<ClassificationResult> {
    const formData = new FormData()
    formData.append("file", file)

    const response = await api.post<ClassifyTextResponse>("/api/classify/file", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    return {
      prediction: response.data.prediction.toUpperCase() as "LEFT" | "CENTER" | "RIGHT",
      confidence: response.data.confidence,
      probabilities: response.data.probabilities,
    }
  }

  getErrorMessage(error: unknown): string {
    const axiosError = error as AxiosError<ApiError>
    return axiosError.response?.data?.detail || "Classification failed. Please try again."
  }
}

export const classifyService = new ClassifyService()
export default classifyService
