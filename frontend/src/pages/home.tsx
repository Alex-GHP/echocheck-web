import { AlertTriangle } from "lucide-react"
import { useState } from "react"
import { Link } from "react-router-dom"
import { ClassificationForm } from "@/components/classify/classification-form"
import {
  type ClassificationResult,
  ClassificationResults,
} from "@/components/classify/classification-results"
import { Footer } from "@/components/layout/footer"
import { useToast } from "@/components/ui/use-toast"
import { classifyService } from "@/services/classify.service"

export function HomePage() {
  const [result, setResult] = useState<ClassificationResult | null>(null)
  const [isClassifying, setIsClassifying] = useState(false)
  const { toast } = useToast()

  const handleClassifyText = async (text: string) => {
    setIsClassifying(true)

    try {
      const classificationResult = await classifyService.classifyText(text)
      setResult({
        ...classificationResult,
        text,
      })
    } catch (error) {
      toast({
        title: "Classification Failed",
        description: classifyService.getErrorMessage(error),
        variant: "destructive",
      })
      setResult(null)
    } finally {
      setIsClassifying(false)
    }
  }

  const handleClassifyFile = async (file: File) => {
    setIsClassifying(true)

    try {
      const classificationResult = await classifyService.classifyFile(file)
      setResult({
        ...classificationResult,
        text: `[Content from: ${file.name}]`,
      })
    } catch (error) {
      toast({
        title: "Classification Failed",
        description: classifyService.getErrorMessage(error),
        variant: "destructive",
      })
      setResult(null)
    } finally {
      setIsClassifying(false)
    }
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="container px-4 py-8 md:py-12 flex-1">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8 md:mb-12">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground mb-3">
              AI-Powered Political Stance Classifier
            </h1>
            <p className="text-muted-foreground max-w-2xl mx-auto text-balance">
              Analyze text to determine its political leaning. Our AI model classifies content as
              Left, Center, or Right with confidence scores.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-6 lg:gap-8">
            <div>
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Input
              </h2>
              <ClassificationForm
                onClassifyText={handleClassifyText}
                onClassifyFile={handleClassifyFile}
                isClassifying={isClassifying}
              />
            </div>

            <div>
              <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
                Results
              </h2>
              <ClassificationResults result={result} />
            </div>
          </div>

          {/* Disclaimer Link */}
          <div className="mt-16 pt-6 border-t border-border/40">
            <Link
              to="/about#disclaimer"
              className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group"
            >
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <span>
                Read our{" "}
                <span className="text-primary underline underline-offset-4 decoration-primary/50 group-hover:decoration-primary">
                  important disclaimer
                </span>{" "}
                about AI limitations
              </span>
            </Link>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}
