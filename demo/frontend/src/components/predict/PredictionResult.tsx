import { motion } from 'framer-motion'
import { TrendingUp, CheckCircle, BarChart3, RotateCcw, MapPin } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { PredictionResponse, EnsemblePredictionResponse } from '@/types'
import { formatPrice, formatNumber } from '@/lib/utils'

interface PredictionResultProps {
  result: PredictionResponse | EnsemblePredictionResponse
  onReset: () => void
}

export function PredictionResult({ result, onReset }: PredictionResultProps) {
  // Debug logging
  console.log('PredictionResult received:', result)

  const isEnsemble = 'ensemble_prediction' in result
  console.log('Is ensemble:', isEnsemble)

  const ensembleResult = isEnsemble ? (result as EnsemblePredictionResponse) : null
  const singleResult = !isEnsemble ? (result as PredictionResponse) : null

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Main Price Card */}
      <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-purple-50/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-2xl">
              <TrendingUp className="w-6 h-6 text-primary" />
              Dự đoán giá nhà
            </CardTitle>
            {isEnsemble && (
              <Badge variant="secondary" className="text-xs">
                <BarChart3 className="w-3 h-3 mr-1" />
                Ensemble
              </Badge>
            )}
          </div>
          <CardDescription>
            {isEnsemble && ensembleResult
              ? `Kết quả từ ${ensembleResult.models_used.length} mô hình AI`
              : singleResult ? `Mô hình: ${singleResult.model_used}` : ''
            }
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Price Display */}
          <div className="text-center space-y-2 py-4">
            <div className="text-5xl font-bold text-primary">
              {ensembleResult ? ensembleResult.ensemble_prediction_formatted : singleResult?.prediction_formatted}
            </div>
            <div className="text-sm text-muted-foreground">
              {ensembleResult
                ? `≈ ${(ensembleResult.ensemble_prediction * 1_000_000_000).toLocaleString('vi-VN')} VND`
                : singleResult ? `≈ ${(singleResult.prediction * 1_000_000_000).toLocaleString('vi-VN')} VND` : ''
              }
            </div>
          </div>

          {/* Confidence */}
          <div className="flex items-center justify-center gap-2 text-sm">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span className="text-muted-foreground">Độ tin cậy:</span>
            <span className="font-semibold">{result.confidence.toFixed(1)}%</span>
          </div>

          {/* Ensemble Details */}
          {ensembleResult && (
            <div className="space-y-3 pt-4 border-t">
              <div className="text-sm font-medium">Chi tiết từng mô hình:</div>
              <div className="grid grid-cols-1 gap-2">
                {Object.entries(ensembleResult.individual_predictions).map(([model, pred]) => (
                  <div
                    key={model}
                    className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-primary" />
                      <span className="text-sm font-medium capitalize">
                        {model.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">
                        {formatPrice(pred.prediction)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {pred.confidence.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="text-xs text-muted-foreground text-center pt-2">
                Độ lệch chuẩn: ±{formatPrice(ensembleResult.ensemble_std)}
              </div>
            </div>
          )}

          {/* Features Used */}
          <div className="space-y-3 pt-4 border-t">
            <div className="text-sm font-medium">Thông tin đã sử dụng:</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(result.features_used)
                .filter(([_, value]) => value !== null && value !== undefined && value !== '')
                .map(([key, value]) => (
                  <div key={key} className="flex justify-between p-2 rounded bg-muted/30">
                    <span className="text-muted-foreground">{key}:</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* Location indicator */}
          {result.features_used.District && (
            <div className="flex items-center justify-center gap-2 pt-4 border-t text-sm">
              <MapPin className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">Khu vực:</span>
              <span className="font-medium">{result.features_used.District}</span>
              {result.features_used.Ward && (
                <span className="text-muted-foreground">• {result.features_used.Ward}</span>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={onReset}
              className="flex-1"
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Dự đoán mới
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Lưu ý</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>• Giá dự đoán chỉ mang tính chất tham khảo</p>
          <p>• Giá thực tế có thể dao động tùy thuộc vào nhiều yếu tố khác</p>
          <p>• Nên tham khảo thêm giá thị trường thực tế trong khu vực</p>
          {isEnsemble && (
            <p>• Dự đoán Ensemble kết hợp nhiều mô hình để tăng độ chính xác</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
