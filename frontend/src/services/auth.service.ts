import type { AxiosError } from "axios"
import api, { tokenStorage } from "@/lib/api"

export interface User {
  id: string
  email: string
  is_verified: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface AuthResponse {
  user: User
  tokens: TokenResponse
}

export interface VerificationResponse {
  message: string
  email: string
  expires_in_minutes: number
}

export interface ApiError {
  detail: string
}

class AuthService {
  private pendingEmail: string | null = null
  private isLogin: boolean = false

  setPendingCredentials(email: string, isLogin: boolean) {
    this.pendingEmail = email
    this.isLogin = isLogin
  }

  getPendingEmail() {
    return this.pendingEmail
  }

  clearPendingCredentials() {
    this.pendingEmail = null
    this.isLogin = false
  }

  async registerInit(email: string, password: string): Promise<VerificationResponse> {
    const response = await api.post<VerificationResponse>("/api/auth/register", {
      email,
      password,
    })
    return response.data
  }

  async registerVerify(email: string, code: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/api/auth/register/verify", {
      email,
      code,
    })
    tokenStorage.setTokens(response.data.tokens.access_token, response.data.tokens.refresh_token)
    return response.data
  }

  async loginInit(email: string, password: string): Promise<VerificationResponse> {
    const response = await api.post<VerificationResponse>("/api/auth/login", {
      email,
      password,
    })
    return response.data
  }

  async loginVerify(email: string, code: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>("/api/auth/login/verify", {
      email,
      code,
    })
    tokenStorage.setTokens(response.data.tokens.access_token, response.data.tokens.refresh_token)
    return response.data
  }

  async verify(code: string): Promise<AuthResponse> {
    if (!this.pendingEmail) {
      throw new Error("No pending verification")
    }

    if (this.isLogin) {
      return this.loginVerify(this.pendingEmail, code)
    } else {
      return this.registerVerify(this.pendingEmail, code)
    }
  }

  async resendCode(): Promise<void> {
    if (!this.pendingEmail) {
      throw new Error("No pending email for verification")
    }

    await api.post("/api/auth/resend-code", {
      email: this.pendingEmail,
    })
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>("/api/auth/me")
    return response.data
  }

  async logout(): Promise<void> {
    try {
      await api.post("/api/auth/logout")
    } finally {
      tokenStorage.clearTokens()
    }
  }

  isAuthenticated(): boolean {
    return !!tokenStorage.getAccessToken()
  }

  getErrorMessage(error: unknown): string {
    const axiosError = error as AxiosError<ApiError>
    return axiosError.response?.data?.detail || "An unexpected error occurred"
  }
}

export const authService = new AuthService()
export default authService
