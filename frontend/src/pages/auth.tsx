import { Eye, EyeOff, Loader2, Radio } from "lucide-react"
import { type FormEvent, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "@/components/providers/auth-provider"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/components/ui/use-toast"
import { authService } from "@/services/auth.service"

export function AuthPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const { signIn, signUp, verify, resendCode, isLoading, user } = useAuth()

  const [activeTab, setActiveTab] = useState<"signin" | "signup">("signin")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [verificationCode, setVerificationCode] = useState("")
  const [step, setStep] = useState<"credentials" | "verification">("credentials")
  const [error, setError] = useState("")

  useEffect(() => {
    if (user) {
      navigate("/")
    }
  }, [user, navigate])

  const handleCredentialsSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError("")

    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters")
      return
    }

    try {
      const authFn = activeTab === "signin" ? signIn : signUp
      const result = await authFn(email, password)

      if (result.needsVerification) {
        setStep("verification")
        toast({
          title: "Verification code sent",
          description: "Please check your email for the 6-digit code",
        })
      }
    } catch (err) {
      const errorMessage = authService.getErrorMessage(err)
      setError(errorMessage)
    }
  }

  const handleVerification = async (e: FormEvent) => {
    e.preventDefault()
    setError("")

    if (verificationCode.length !== 6) {
      setError("Please enter a valid 6-digit code")
      return
    }

    try {
      await verify(verificationCode)
      toast({
        title: "Welcome!",
        description: "You have successfully signed in",
      })
      navigate("/")
    } catch (err) {
      const errorMessage = authService.getErrorMessage(err)
      setError(errorMessage || "Invalid verification code. Please try again.")
    }
  }

  const handleResendCode = async () => {
    try {
      await resendCode()
      toast({
        title: "Code resent",
        description: "A new verification code has been sent to your email",
      })
    } catch (err) {
      toast({
        title: "Failed to resend code",
        description: authService.getErrorMessage(err),
        variant: "destructive",
      })
    }
  }

  const resetForm = () => {
    setEmail("")
    setPassword("")
    setVerificationCode("")
    setStep("credentials")
    setError("")
  }

  return (
    <div className="flex flex-1 items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center">
              <Radio className="h-6 w-6 text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl">Welcome to EchoCheck</CardTitle>
          <CardDescription>
            {step === "credentials"
              ? "Sign in or create an account to continue"
              : "Enter the verification code sent to your email"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step === "credentials" ? (
            <Tabs
              value={activeTab}
              onValueChange={(v) => {
                setActiveTab(v as "signin" | "signup")
                resetForm()
              }}
            >
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="signin">Sign In</TabsTrigger>
                <TabsTrigger value="signup">Sign Up</TabsTrigger>
              </TabsList>

              <TabsContent value="signin">
                <form onSubmit={handleCredentialsSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signin-email">Email</Label>
                    <Input
                      id="signin-email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signin-password">Password</Label>
                    <div className="relative">
                      <Input
                        id="signin-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={isLoading}
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                  </div>

                  {error && <p className="text-sm text-destructive">{error}</p>}

                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      "Continue"
                    )}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="signup">
                <form onSubmit={handleCredentialsSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={isLoading}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Password</Label>
                    <div className="relative">
                      <Input
                        id="signup-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Create a password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={isLoading}
                        className="pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4 text-muted-foreground" />
                        ) : (
                          <Eye className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Must be at least 6 characters</p>
                  </div>

                  {error && <p className="text-sm text-destructive">{error}</p>}

                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating account...
                      </>
                    ) : (
                      "Continue"
                    )}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          ) : (
            <form onSubmit={handleVerification} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="verification-code">Verification Code</Label>
                <Input
                  id="verification-code"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={6}
                  placeholder="000000"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ""))}
                  disabled={isLoading}
                  className="text-center text-2xl tracking-[0.5em] font-mono"
                />
                <p className="text-xs text-muted-foreground text-center">
                  Enter the 6-digit code sent to {email}
                </p>
              </div>

              {error && <p className="text-sm text-destructive text-center">{error}</p>}

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  "Verify"
                )}
              </Button>

              <div className="flex flex-col items-center gap-2">
                <Button
                  type="button"
                  variant="link"
                  onClick={handleResendCode}
                  disabled={isLoading}
                  className="text-sm"
                >
                  Resend code
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setStep("credentials")}
                  disabled={isLoading}
                  className="text-sm"
                >
                  Back to {activeTab === "signin" ? "sign in" : "sign up"}
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
