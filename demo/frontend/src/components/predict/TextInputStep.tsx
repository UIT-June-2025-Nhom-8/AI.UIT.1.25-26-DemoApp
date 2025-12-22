import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { parseAPI, getErrorMessage } from '@/lib/api'
import type { HouseFeatures } from '@/types'

interface TextInputStepProps {
  onParseComplete: (features: HouseFeatures) => void
}

export function TextInputStep({ onParseComplete }: TextInputStepProps) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleParse = async () => {
    if (!text.trim()) {
      setError('Vui lòng nhập mô tả nhà')
      return
    }

    setError(null)
    setLoading(true)

    try {
      const response = await parseAPI.parseText({ text })
      if (response.success && response.features) {
        onParseComplete(response.features)
      } else {
        setError('Không thể phân tích mô tả. Vui lòng thử lại.')
      }
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const exampleTexts = [
    'Nhà 120m2, 3 phòng ngủ, 2 toilet, quận 7, sổ hồng, hướng đông nam',
    'Bán nhà mặt tiền đường Nguyễn Thị Minh Khai, Quận 1, DT: 150m2, 4PN, 3WC, 2 tầng, nội thất đầy đủ',
    'Nhà phố cao cấp 200m2, 5 phòng ngủ, 4 WC, 3 lầu, quận Bình Thạnh, sổ đỏ chính chủ',
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            Nhập mô tả nhà
          </CardTitle>
          <CardDescription>
            Nhập hoặc dán mô tả quảng cáo nhà từ bản tin. AI sẽ tự động phân tích và điền thông tin.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="description">Mô tả nhà (Tiếng Việt)</Label>
            <Textarea
              id="description"
              placeholder="Ví dụ: Nhà 120m2, 3 phòng ngủ, 2 toilet, quận 7, sổ hồng, hướng đông nam..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
              rows={6}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Ví dụ (click để dùng):</Label>
            <div className="space-y-2">
              {exampleTexts.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setText(example)}
                  disabled={loading}
                  className="text-xs text-left w-full p-2 rounded-md bg-muted/50 hover:bg-muted transition-colors disabled:opacity-50"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          <Button
            onClick={handleParse}
            disabled={loading || !text.trim()}
            size="lg"
            className="w-full"
          >
            {loading ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Đang phân tích...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Phân tích với AI
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}
