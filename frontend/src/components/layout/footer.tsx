import { Github, Linkedin, Radio } from "lucide-react"
import { Link } from "react-router-dom"

export function Footer() {
  return (
    <footer className="bg-muted/30 border-t border-border/40">
      <div className="container px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <Radio className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-semibold">EchoCheck</span>
            </div>

            <nav className="flex items-center gap-6">
              <Link
                to="/"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Home
              </Link>
              <Link
                to="/about"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                About
              </Link>
              <Link
                to="/auth"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Sign In
              </Link>
            </nav>

            <div className="flex items-center gap-4">
              <a
                href="https://github.com/Alex-GHP/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="h-5 w-5" />
                <span className="sr-only">GitHub</span>
              </a>
              <a
                href="https://www.linkedin.com/in/alexandru-gabriel-morariu-8657b0289/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <Linkedin className="h-5 w-5" />
                <span className="sr-only">LinkedIn</span>
              </a>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-border/40 text-center">
            <p className="text-xs text-muted-foreground">
              © {new Date().getFullYear()} EchoCheck. Built for media literacy and informed
              citizenship.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
