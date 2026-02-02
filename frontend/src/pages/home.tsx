import { useState } from "react"
import { ClassificationForm } from "@/components/classify/classification-form"
import {
  ClassificationResults,
  type ClassificationResult,
} from "@/components/classify/classification-results"
import { classifyService } from "@/services/classify.service"
import { useToast } from "@/components/ui/use-toast"

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
    <div className="container px-4 py-8 md:py-12">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground mb-3">
            Political Stance Classifier
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
      </div>
    </div>
  )
}
