import { useState, useRef, type ChangeEvent, type DragEvent } from "react"
import { Upload, X, FileText, Lock, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useAuth } from "@/components/providers/auth-provider"
import { cn } from "@/lib/utils"

interface ClassificationFormProps {
  onClassifyText: (text: string) => Promise<void>
  onClassifyFile: (file: File) => Promise<void>
  isClassifying: boolean
}

export function ClassificationForm({
  onClassifyText,
  onClassifyFile,
  isClassifying,
}: ClassificationFormProps) {
  const { user } = useAuth()
  const [text, setText] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const isAuthenticated = !!user
  const canClassify = text.trim().length > 0 || file !== null

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    if (isAuthenticated) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    if (!isAuthenticated) return

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && isValidFileType(droppedFile)) {
      setFile(droppedFile)
    }
  }

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && isValidFileType(selectedFile)) {
      setFile(selectedFile)
    }
  }

  const isValidFileType = (file: File) => {
    const validTypes = [
      "text/plain",
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    return (
      validTypes.includes(file.type) ||
      file.name.endsWith(".txt") ||
      file.name.endsWith(".pdf") ||
      file.name.endsWith(".docx")
    )
  }

  const handleClassify = async () => {
    if (file) {
      await onClassifyFile(file)
    } else {
      await onClassifyText(text)
    }
  }

  const removeFile = () => {
    setFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="text-input" className="text-sm font-medium text-foreground mb-2 block">
          Text to Analyze
        </label>
        <Textarea
          id="text-input"
          placeholder="Enter political text to analyze (recommended: ~500 words)..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="min-h-[240px] resize-none bg-background border-input focus:ring-2 focus:ring-primary/20"
          disabled={isClassifying}
        />
        <p className="text-xs text-muted-foreground mt-1">
          {text.trim().split(/\s+/).filter(Boolean).length} words
        </p>
      </div>

      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            {/* biome-ignore lint/a11y/useSemanticElements: Drop zone needs div for drag/drop events */}
            <div
              role="button"
              tabIndex={isAuthenticated ? 0 : -1}
              className={cn(
                "relative border-2 border-dashed rounded-lg p-6 transition-all",
                isAuthenticated
                  ? isDragging
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-accent/30 cursor-pointer"
                  : "border-border/50 bg-muted/30 cursor-not-allowed opacity-60",
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => isAuthenticated && fileInputRef.current?.click()}
              onKeyDown={(e) => {
                if (isAuthenticated && (e.key === "Enter" || e.key === " ")) {
                  e.preventDefault()
                  fileInputRef.current?.click()
                }
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.pdf,.docx"
                onChange={handleFileSelect}
                className="hidden"
                disabled={!isAuthenticated || isClassifying}
              />

              {file ? (
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">{file.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation()
                      removeFile()
                    }}
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    disabled={isClassifying}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2 text-center">
                  {isAuthenticated ? (
                    <>
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Upload className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          Drop a file here or click to upload
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Supports .txt, .pdf, .docx files
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="h-10 w-10 rounded-full bg-muted/50 flex items-center justify-center">
                        <Lock className="h-5 w-5 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">
                          File upload requires authentication
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Sign in to upload files
                        </p>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </TooltipTrigger>
          {!isAuthenticated && (
            <TooltipContent>
              <p>Sign in to upload files</p>
            </TooltipContent>
          )}
        </Tooltip>
      </TooltipProvider>

      <Button
        className="w-full h-11"
        onClick={handleClassify}
        disabled={!canClassify || isClassifying}
      >
        {isClassifying ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Classifying...
          </>
        ) : (
          "Classify"
        )}
      </Button>
    </div>
  )
}
