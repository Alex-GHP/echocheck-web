import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ThemeProvider } from "@/components/providers/theme-provider"
import { AuthProvider } from "@/components/providers/auth-provider"
import { Toaster } from "@/components/ui/toaster"
import { Header } from "@/components/layout/header"
import { HomePage } from "@/pages/home"
import { AuthPage } from "@/pages/auth"
import { AboutPage } from "@/pages/about"

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <Header />
      <main>{children}</main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="dark" storageKey="echocheck-theme">
        <AuthProvider>
          <AppLayout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </AppLayout>
          <Toaster />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}

export default App
