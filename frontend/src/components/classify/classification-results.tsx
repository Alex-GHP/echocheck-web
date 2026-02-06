import { BarChart3, ThumbsDown, ThumbsUp } from "lucide-react"
import { useRef, useState } from "react"
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import { useAuth } from "@/components/providers/auth-provider"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { cn } from "@/lib/utils"
import { feedbackService } from "@/services/feedback.service"

export interface ClassificationResult {
  prediction: "LEFT" | "CENTER" | "RIGHT"
  confidence: number
  probabilities: {
    left: number
    center: number
    right: number
  }
  text?: string
}

interface ClassificationResultsProps {
  result: ClassificationResult | null
}

const COLORS = {
  left: "hsl(0, 70%, 55%)",
  center: "hsl(45, 85%, 55%)",
  right: "hsl(220, 70%, 55%)",
}

const LABELS = {
  LEFT: { label: "Left", color: COLORS.left },
  CENTER: { label: "Center", color: COLORS.center },
  RIGHT: { label: "Right", color: COLORS.right },
}

export function ClassificationResults({ result }: ClassificationResultsProps) {
  const { user } = useAuth()
  const { toast } = useToast()
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const [showCorrection, setShowCorrection] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const prevResultRef = useRef<string | null>(null)

  // Reset feedback state when result changes
  const resultKey = result ? `${result.prediction}-${result.confidence}` : null
  if (resultKey !== prevResultRef.current) {
    prevResultRef.current = resultKey
    if (feedbackGiven) setFeedbackGiven(false)
    if (showCorrection) setShowCorrection(false)
  }

  if (!result) {
    return (
      <Card className="h-full flex items-center justify-center border-dashed">
        <CardContent className="text-center py-16">
          <div className="h-16 w-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium text-foreground mb-2">No Results Yet</h3>
          <p className="text-sm text-muted-foreground max-w-[280px]">
            Enter text or upload a file to see classification results
          </p>
        </CardContent>
      </Card>
    )
  }

  const chartData = [
    { name: "Left", value: result.probabilities.left, color: COLORS.left },
    { name: "Center", value: result.probabilities.center, color: COLORS.center },
    { name: "Right", value: result.probabilities.right, color: COLORS.right },
  ]

  const predictionInfo = LABELS[result.prediction]
  const otherOptions = (["LEFT", "CENTER", "RIGHT"] as const).filter(
    (option) => option !== result.prediction,
  )

  const submitFeedback = async (isCorrect: boolean, actualLabel: "left" | "center" | "right") => {
    if (!result.text) return

    setIsSubmitting(true)
    try {
      await feedbackService.submitFeedback({
        text: result.text,
        model_prediction: result.prediction.toLowerCase() as "left" | "center" | "right",
        model_confidence: result.confidence,
        is_correct: isCorrect,
        actual_label: actualLabel,
      })
      setFeedbackGiven(true)
      setShowCorrection(false)
      toast({
        title: "Thank you!",
        description: "Your feedback helps improve our model.",
        variant: "default",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: feedbackService.getErrorMessage(error),
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePositiveFeedback = () => {
    submitFeedback(true, result.prediction.toLowerCase() as "left" | "center" | "right")
  }

  const handleNegativeFeedback = () => {
    setShowCorrection(true)
  }

  const handleCorrection = (correctLabel: "LEFT" | "CENTER" | "RIGHT") => {
    submitFeedback(false, correctLabel.toLowerCase() as "left" | "center" | "right")
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">Probability Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[240px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                  strokeWidth={2}
                  stroke="hsl(var(--background))"
                >
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="bg-popover border border-border rounded-lg px-3 py-2 shadow-lg">
                          <p className="text-sm font-medium text-foreground">{data.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {(data.value * 100).toFixed(1)}%
                          </p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  content={({ payload }) => (
                    <div className="flex items-center justify-center gap-4 mt-4">
                      {payload?.map((entry) => (
                        <div key={String(entry.value)} className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: entry.color }}
                          />
                          <span className="text-xs text-muted-foreground">{entry.value}</span>
                        </div>
                      ))}
                    </div>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-3">Predicted Classification</p>
            <Badge
              className={cn(
                "text-lg px-6 py-2 font-semibold",
                result.prediction === "LEFT" &&
                  "bg-red-500/15 text-red-500 hover:bg-red-500/20 border-red-500/30",
                result.prediction === "CENTER" &&
                  "bg-yellow-500/15 text-yellow-600 hover:bg-yellow-500/20 border-yellow-500/30",
                result.prediction === "RIGHT" &&
                  "bg-blue-500/15 text-blue-500 hover:bg-blue-500/20 border-blue-500/30",
              )}
              variant="outline"
            >
              {predictionInfo.label.toUpperCase()}
            </Badge>
            <p className="text-2xl font-bold text-foreground mt-3">
              {(result.confidence * 100).toFixed(1)}%
            </p>
            <p className="text-xs text-muted-foreground">confidence</p>
          </div>
        </CardContent>
      </Card>

      {user && !feedbackGiven && result.text && (
        <Card>
          <CardContent className="pt-6">
            {!showCorrection ? (
              <div className="text-center">
                <p className="text-sm text-foreground mb-4">Was this classification correct?</p>
                <div className="flex items-center justify-center gap-3">
                  <Button
                    variant="outline"
                    onClick={handlePositiveFeedback}
                    disabled={isSubmitting}
                    className="gap-2 border-green-500/30 text-green-500 hover:bg-green-500/10 hover:text-green-500 bg-transparent"
                  >
                    <ThumbsUp className="h-4 w-4" />
                    Yes
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleNegativeFeedback}
                    disabled={isSubmitting}
                    className="gap-2 border-red-500/30 text-red-500 hover:bg-red-500/10 hover:text-red-500 bg-transparent"
                  >
                    <ThumbsDown className="h-4 w-4" />
                    No
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-sm text-foreground mb-4">
                  {"What's the correct classification?"}
                </p>
                <div className="flex items-center justify-center gap-3">
                  {otherOptions.map((option) => (
                    <Button
                      key={option}
                      variant="outline"
                      onClick={() => handleCorrection(option)}
                      disabled={isSubmitting}
                      className={cn(
                        "gap-2 bg-transparent",
                        option === "LEFT" &&
                          "border-red-500/30 text-red-500 hover:bg-red-500/10 hover:text-red-500",
                        option === "CENTER" &&
                          "border-yellow-500/30 text-yellow-600 hover:bg-yellow-500/10 hover:text-yellow-600",
                        option === "RIGHT" &&
                          "border-blue-500/30 text-blue-500 hover:bg-blue-500/10 hover:text-blue-500",
                      )}
                    >
                      {LABELS[option].label}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
