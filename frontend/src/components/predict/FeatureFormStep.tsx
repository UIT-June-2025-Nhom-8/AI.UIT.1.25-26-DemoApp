import { useState } from 'react'
import { motion } from 'framer-motion'
import { Edit3, TrendingUp, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { HouseFeatures, PredictionResponse, EnsemblePredictionResponse } from '@/types'
import { predictAPI, getErrorMessage } from '@/lib/api'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface FeatureFormStepProps {
  initialFeatures: HouseFeatures
  onPredictionComplete: (result: PredictionResponse | EnsemblePredictionResponse) => void
  onBack: () => void
}

export function FeatureFormStep({ initialFeatures, onPredictionComplete, onBack }: FeatureFormStepProps) {
  const [features, setFeatures] = useState<HouseFeatures>(initialFeatures)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [useEnsemble, setUseEnsemble] = useState(true)

  const handleChange = (key: string, value: string | number) => {
    setFeatures((prev) => ({ ...prev, [key]: value }))
  }

  const handlePredict = async () => {
    setError(null)
    setLoading(true)

    try {
      const response = await predictAPI.predict({
        features,
        use_ensemble: useEnsemble,
      })
      onPredictionComplete(response)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const formFields = [
    { key: 'Area', label: 'Diện tích (m²)', type: 'number', required: true },
    { key: 'Bedrooms', label: 'Số phòng ngủ', type: 'number', required: false },
    { key: 'Bathrooms', label: 'Số toilet', type: 'number', required: false },
    { key: 'Floors', label: 'Số tầng', type: 'number', required: false },
    { key: 'Frontage', label: 'Mặt tiền (m)', type: 'number', required: false },
    { key: 'AccessRoad', label: 'Đường vào (m)', type: 'number', required: false },
    { key: 'District', label: 'Quận/Huyện', type: 'text', required: false },
    { key: 'Ward', label: 'Phường/Xã', type: 'text', required: false },
    { key: 'Street', label: 'Đường', type: 'text', required: false },
    { key: 'Direction', label: 'Hướng nhà', type: 'text', required: false },
    { key: 'BalconyDirection', label: 'Hướng ban công', type: 'text', required: false },
    { key: 'LegalStatus', label: 'Giấy tờ pháp lý', type: 'text', required: false },
    { key: 'Furniture', label: 'Nội thất', type: 'text', required: false },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-4"
    >
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-primary" />
                Thông tin nhà
              </CardTitle>
              <CardDescription>
                Kiểm tra và chỉnh sửa thông tin đã phân tích
              </CardDescription>
            </div>
            <Badge variant="secondary">AI Parsed</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {formFields.map((field) => (
              <div key={field.key} className="space-y-2">
                <Label htmlFor={field.key}>
                  {field.label}
                  {field.required && <span className="text-destructive ml-1">*</span>}
                </Label>
                <Input
                  id={field.key}
                  type={field.type}
                  value={features[field.key] ?? ''}
                  onChange={(e) => handleChange(field.key, field.type === 'number' ? parseFloat(e.target.value) || '' : e.target.value)}
                  disabled={loading}
                  placeholder={field.label}
                />
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 pt-4 border-t">
            <input
              type="checkbox"
              id="ensemble"
              checked={useEnsemble}
              onChange={(e) => setUseEnsemble(e.target.checked)}
              className="w-4 h-4 rounded border-gray-300"
            />
            <Label htmlFor="ensemble" className="cursor-pointer">
              Sử dụng Ensemble (kết hợp nhiều mô hình để tăng độ chính xác)
            </Label>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={onBack}
              disabled={loading}
              className="flex-1"
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Nhập lại
            </Button>
            <Button
              onClick={handlePredict}
              disabled={loading || !features.Area}
              size="lg"
              className="flex-1"
            >
              {loading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Đang dự đoán...
                </>
              ) : (
                <>
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Dự đoán giá
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
