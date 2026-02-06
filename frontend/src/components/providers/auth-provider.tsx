import { createContext, type ReactNode, useCallback, useContext, useEffect, useState } from "react"
import { tokenStorage } from "@/lib/api"
import { authService, type User } from "@/services/auth.service"

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  pendingEmail: string | null
  signIn: (email: string, password: string) => Promise<{ needsVerification: boolean }>
  signUp: (email: string, password: string) => Promise<{ needsVerification: boolean }>
  verify: (code: string) => Promise<void>
  signOut: () => Promise<void>
  resendCode: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [pendingEmail, setPendingEmail] = useState<string | null>(null)

  const refreshUser = useCallback(async () => {
    if (!tokenStorage.getAccessToken()) {
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
    } catch {
      // Token invalid or expired
      tokenStorage.clearTokens()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  const signIn = async (
    email: string,
    password: string,
  ): Promise<{ needsVerification: boolean }> => {
    setIsLoading(true)
    try {
      const response = await authService.loginInit(email, password)
      // If we get a successful response with email, verification code was sent
      if (response.email) {
        authService.setPendingCredentials(email, true)
        setPendingEmail(email)
        return { needsVerification: true }
      }
      return { needsVerification: false }
    } finally {
      setIsLoading(false)
    }
  }

  const signUp = async (
    email: string,
    password: string,
  ): Promise<{ needsVerification: boolean }> => {
    setIsLoading(true)
    try {
      const response = await authService.registerInit(email, password)
      // If we get a successful response with email, verification code was sent
      if (response.email) {
        authService.setPendingCredentials(email, false)
        setPendingEmail(email)
        return { needsVerification: true }
      }
      return { needsVerification: false }
    } finally {
      setIsLoading(false)
    }
  }

  const verify = async (code: string): Promise<void> => {
    setIsLoading(true)
    try {
      const response = await authService.verify(code)
      setUser(response.user)
      authService.clearPendingCredentials()
      setPendingEmail(null)
    } finally {
      setIsLoading(false)
    }
  }

  const signOut = async (): Promise<void> => {
    setIsLoading(true)
    try {
      await authService.logout()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const resendCode = async (): Promise<void> => {
    await authService.resendCode()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        pendingEmail,
        signIn,
        signUp,
        verify,
        signOut,
        resendCode,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
