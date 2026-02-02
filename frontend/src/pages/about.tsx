import { Radio, Brain, BarChart3, AlertTriangle, Github, Twitter } from "lucide-react"
import { Link } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function AboutPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative border-b border-border/40 bg-gradient-to-b from-primary/5 to-background">
        <div className="container px-4 py-16 md:py-24">
          <div className="max-w-3xl mx-auto text-center">
            <div className="flex justify-center mb-6">
              <div className="h-16 w-16 rounded-2xl bg-primary flex items-center justify-center">
                <Radio className="h-8 w-8 text-primary-foreground" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground mb-4">
              EchoCheck
            </h1>
            <p className="text-xl text-muted-foreground text-balance">
              AI-powered political stance detection
            </p>
            <div className="flex items-center justify-center gap-2 mt-6">
              <Badge variant="secondary" className="text-xs">
                Machine Learning
              </Badge>
              <Badge variant="secondary" className="text-xs">
                NLP
              </Badge>
              <Badge variant="secondary" className="text-xs">
                Political Analysis
              </Badge>
            </div>
          </div>
        </div>
      </section>

      {/* What it does */}
      <section className="border-b border-border/40">
        <div className="container px-4 py-16">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-foreground mb-4">What is EchoCheck?</h2>
            <p className="text-muted-foreground leading-relaxed mb-6">
              EchoCheck is an advanced text analysis tool that uses machine learning to determine
              the political leaning of written content. Whether you are analyzing news articles,
              social media posts, or political speeches, EchoCheck provides objective insights into
              the ideological stance of the text.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              Our goal is to promote media literacy and help users understand the political
              perspectives present in the content they consume. By identifying potential biases, we
              empower readers to seek out diverse viewpoints and make more informed decisions.
            </p>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-b border-border/40 bg-muted/30">
        <div className="container px-4 py-16">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-foreground mb-8 text-center">How It Works</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <Card className="bg-background">
                <CardHeader className="pb-2">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
                    <Brain className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">ML Model</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Our classifier is trained on a diverse dataset of politically labeled text,
                    using state-of-the-art natural language processing techniques.
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-background">
                <CardHeader className="pb-2">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">Classification</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Text is analyzed across three categories: Left, Center, and Right. Each
                    classification comes with a confidence score for transparency.
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-background">
                <CardHeader className="pb-2">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
                    <Radio className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">Feedback Loop</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    User feedback helps improve our model over time. When you correct a
                    classification, you are contributing to better accuracy for everyone.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="border-b border-border/40">
        <div className="container px-4 py-16">
          <div className="max-w-3xl mx-auto">
            <Card className="border-yellow-500/30 bg-yellow-500/5">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  </div>
                  <CardTitle className="text-lg">Important Disclaimer</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  EchoCheck is an AI-powered tool and, like all AI systems, has limitations.
                  Classifications should be considered as one data point among many, not as
                  definitive truth.
                </p>
                <ul className="text-sm text-muted-foreground space-y-2 list-disc list-inside">
                  <li>Political spectrums are complex and vary by country and context</li>
                  <li>The model may not accurately capture nuance or satire</li>
                  <li>Results can be influenced by training data biases</li>
                  <li>Short texts may produce less reliable results</li>
                </ul>
                <p className="text-sm text-muted-foreground">
                  We encourage users to think critically about all content, including our
                  classifications. This tool is meant to supplement, not replace, your own judgment
                  and research.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted/30">
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
                  href="https://github.com/Alex-GHP/echocheck-web"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Github className="h-5 w-5" />
                  <span className="sr-only">GitHub</span>
                </a>
                <a
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Twitter className="h-5 w-5" />
                  <span className="sr-only">Twitter</span>
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
    </div>
  )
}
