import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Edit3, TrendingUp, AlertCircle, RotateCcw, Layers, FormInput } from 'lucide-react'
import { Layout } from '@/components/layout/Layout'
import { LocationMap } from '@/components/predict/LocationMap'
import { PredictionResult } from '@/components/predict/PredictionResult'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { HouseFeatures, PredictionResponse, EnsemblePredictionResponse } from '@/types'
import { parseAPI, predictAPI, getErrorMessage } from '@/lib/api'
import {
  HOUSE_DIRECTIONS,
  BALCONY_DIRECTIONS,
  LEGAL_STATUSES,
  FURNITURE_STATES,
  ALL_DISTRICTS,
} from '@/constants/validValues'

export function PredictPage() {
  const [activeTab, setActiveTab] = useState('text-parse')
  const [text, setText] = useState('')
  const [features, setFeatures] = useState<HouseFeatures>({})
  const [prediction, setPrediction] = useState<PredictionResponse | EnsemblePredictionResponse | null>(null)
  const [parseLoading, setParseLoading] = useState(false)
  const [predictLoading, setPredictLoading] = useState(false)
  const [parseError, setParseError] = useState<string | null>(null)
  const [predictError, setPredictError] = useState<string | null>(null)
  const [useEnsemble, setUseEnsemble] = useState(true)

  const exampleTexts = [
    'Nhà 120m2, 3 phòng ngủ, 2 toilet, quận 7, sổ hồng, hướng đông nam',
    'Bán nhà mặt tiền đường Nguyễn Thị Minh Khai, Quận 1, DT: 150m2, 4PN, 3WC, 2 tầng, nội thất đầy đủ',
    'Nhà phố cao cấp 200m2, 5 phòng ngủ, 4 WC, 3 lầu, quận Bình Thạnh, sổ đỏ chính chủ',
  ]

  const handleParse = async () => {
    if (!text.trim()) {
      setParseError('Vui lòng nhập mô tả nhà')
      return
    }

    setParseError(null)
    setParseLoading(true)

    try {
      const response = await parseAPI.parseText({ text })
      if (response.success && response.features) {
        // Fill features into manual form
        setFeatures(response.features)

        // Switch to manual input tab
        setActiveTab('form-input')

        // Auto-trigger prediction after a short delay (to let UI update)
        setTimeout(() => {
          autoPredictAfterParse(response.features)
        }, 300)
      } else {
        setParseError('Không thể phân tích mô tả. Vui lòng thử lại.')
      }
    } catch (err) {
      setParseError(getErrorMessage(err))
    } finally {
      setParseLoading(false)
    }
  }

  const autoPredictAfterParse = async (parsedFeatures: HouseFeatures) => {
    if (!parsedFeatures.Area) {
      // Don't auto-predict if Area is missing (required field)
      return
    }

    setPredictError(null)
    setPredictLoading(true)

    try {
      const response = await predictAPI.predict({
        features: parsedFeatures,
        use_ensemble: useEnsemble,
      })
      setPrediction(response)
    } catch (err) {
      setPredictError(getErrorMessage(err))
    } finally {
      setPredictLoading(false)
    }
  }

  const handleChange = (key: string, value: string | number) => {
    setFeatures((prev: HouseFeatures) => ({ ...prev, [key]: value }))
  }

  const handlePredict = async () => {
    setPredictError(null)
    setPredictLoading(true)

    try {
      const response = await predictAPI.predict({
        features,
        use_ensemble: useEnsemble,
      })
      setPrediction(response)
    } catch (err) {
      setPredictError(getErrorMessage(err))
    } finally {
      setPredictLoading(false)
    }
  }

  const handleReset = () => {
    setText('')
    setFeatures({})
    setPrediction(null)
    setParseError(null)
    setPredictError(null)
    setActiveTab('text-parse')
  }

  const formFields = [
    { key: 'Area', label: 'Diện tích (m²)', type: 'number', required: true },
    { key: 'Bedrooms', label: 'Số phòng ngủ', type: 'number', required: false },
    { key: 'Bathrooms', label: 'Số toilet', type: 'number', required: false },
    { key: 'Floors', label: 'Số tầng', type: 'number', required: false },
    { key: 'Frontage', label: 'Mặt tiền (m)', type: 'number', required: false },
    { key: 'AccessRoad', label: 'Đường vào (m)', type: 'number', required: false },
    { key: 'District', label: 'Quận/Huyện', type: 'select', required: false, options: ALL_DISTRICTS },
    { key: 'Ward', label: 'Phường/Xã', type: 'text', required: false },
    { key: 'Street', label: 'Đường', type: 'text', required: false },
    { key: 'Direction', label: 'Hướng nhà', type: 'select', required: false, options: HOUSE_DIRECTIONS },
    { key: 'BalconyDirection', label: 'Hướng ban công', type: 'select', required: false, options: BALCONY_DIRECTIONS },
    { key: 'LegalStatus', label: 'Giấy tờ pháp lý', type: 'select', required: false, options: LEGAL_STATUSES },
    { key: 'Furniture', label: 'Nội thất', type: 'select', required: false, options: FURNITURE_STATES },
  ]

  return (
    <Layout>
      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Left Panel - Input Form */}
        <div className="space-y-6">
          {/* Tabs for Text Parse and Form Input */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 rounded-2xl bg-muted/50 p-1 h-12">
              <TabsTrigger value="text-parse" className="rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-sm font-semibold">
                <Sparkles className="w-4 h-4 mr-2" />
                Phân tích văn bản
              </TabsTrigger>
              <TabsTrigger value="form-input" className="rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-sm font-semibold">
                <FormInput className="w-4 h-4 mr-2" />
                Nhập thủ công
              </TabsTrigger>
            </TabsList>

            {/* Text Parse Tab */}
            <TabsContent value="text-parse" className="mt-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
              >
                <Card className="border shadow-md hover:shadow-lg transition-all duration-300 rounded-3xl">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3 mb-1">
                      <div className="w-10 h-10 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl flex items-center justify-center">
                        <Layers className="w-5 h-5 text-primary stroke-[2.5]" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-xl">Nhập mô tả nhà</CardTitle>
                      </div>
                    </div>
                    <CardDescription className="text-sm">
                      AI sẽ tự động phân tích và điền thông tin
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3 pt-0">
                    {parseError && (
                      <Alert variant="destructive" className="rounded-xl">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{parseError}</AlertDescription>
                      </Alert>
                    )}

                    <div className="space-y-1.5">
                      <Label htmlFor="description" className="text-sm font-semibold">
                        Mô tả nhà (Tiếng Việt)
                      </Label>
                      <Textarea
                        id="description"
                        placeholder="Ví dụ: Nhà 120m2, 3PN, 2WC, quận 7, sổ hồng..."
                        value={text}
                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setText(e.target.value)}
                        disabled={parseLoading}
                        rows={4}
                        className="resize-none bg-muted/30 border-2 focus:border-primary rounded-xl text-sm transition-colors"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <Label className="text-xs text-muted-foreground font-semibold">
                        Ví dụ (click để dùng):
                      </Label>
                      <div className="space-y-1.5">
                        {exampleTexts.map((example, index) => (
                          <button
                            key={index}
                            onClick={() => setText(example)}
                            disabled={parseLoading}
                            className="text-xs text-left w-full p-2 rounded-lg bg-muted/30 hover:bg-white hover:border-primary border border-transparent transition-all disabled:opacity-50 hover:translate-x-0.5 duration-200"
                          >
                            {example}
                          </button>
                        ))}
                      </div>
                    </div>

                    <Button
                      onClick={handleParse}
                      disabled={parseLoading || !text.trim()}
                      size="default"
                      className="w-full rounded-xl bg-gradient-to-r from-primary to-primary/80 hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 hover:-translate-y-0.5 font-semibold h-11"
                    >
                      {parseLoading ? (
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
            </TabsContent>

            {/* Form Input Tab */}
            <TabsContent value="form-input" className="mt-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
              >
                <Card className="border shadow-md rounded-3xl">
                  <CardHeader>
                    <div className="flex items-center gap-4 mb-2">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl flex items-center justify-center">
                        <Edit3 className="w-6 h-6 text-primary stroke-[2.5]" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-2xl">Nhập thủ công</CardTitle>
                        <CardDescription className="text-[15px]">
                          Nhập trực tiếp các thông tin về căn nhà
                        </CardDescription>
                      </div>
                      {Object.keys(features).length > 0 && (
                        <Badge variant="secondary" className="rounded-lg px-3 py-1">
                          AI Parsed
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {predictError && (
                      <Alert variant="destructive" className="rounded-xl">
                        <AlertDescription>{predictError}</AlertDescription>
                      </Alert>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {formFields.map((field) => {
                        const isSelect = field.type === 'select'

                        return (
                          <div key={field.key} className="space-y-2">
                            <Label htmlFor={field.key} className="text-[15px] font-semibold">
                              {field.label}
                              {field.required && <span className="text-destructive ml-1">*</span>}
                            </Label>
                            {isSelect ? (
                              <Select
                                value={features[field.key]?.toString() ?? ''}
                                onValueChange={(value: string) => handleChange(field.key, value)}
                                disabled={predictLoading}
                              >
                                <SelectTrigger className="bg-muted/30 border-2 focus:border-primary rounded-xl h-11">
                                  <SelectValue placeholder={`Chọn ${field.label.toLowerCase()}`} />
                                </SelectTrigger>
                                <SelectContent>
                                  {(field.options || []).map((option: string) => (
                                    <SelectItem key={option} value={option}>
                                      {option}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            ) : (
                              <Input
                                id={field.key}
                                type={field.type}
                                value={features[field.key] ?? ''}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                  handleChange(
                                    field.key,
                                    field.type === 'number' ? parseFloat(e.target.value) || '' : e.target.value
                                  )
                                }
                                disabled={predictLoading}
                                placeholder={field.label}
                                className="bg-muted/30 border-2 focus:border-primary rounded-xl h-11 text-[15px]"
                              />
                            )}
                          </div>
                        )
                      })}
                    </div>

                    <div className="flex items-center gap-4 pt-4 border-t">
                      <input
                        type="checkbox"
                        id="ensemble-manual"
                        checked={useEnsemble}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUseEnsemble(e.target.checked)}
                        className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
                      />
                      <Label htmlFor="ensemble-manual" className="cursor-pointer text-[15px] font-medium">
                        Sử dụng Ensemble (kết hợp nhiều mô hình để tăng độ chính xác)
                      </Label>
                    </div>

                    <div className="flex gap-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={handleReset}
                        disabled={predictLoading}
                        className="flex-1 rounded-xl border-2 font-semibold h-12"
                      >
                        <RotateCcw className="mr-2 h-4 w-4" />
                        Xóa form
                      </Button>
                      <Button
                        onClick={handlePredict}
                        disabled={predictLoading || !features.Area}
                        size="lg"
                        className="flex-1 rounded-xl bg-gradient-to-r from-primary to-primary/80 hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 font-bold h-12"
                      >
                        {predictLoading ? (
                          <>
                            <span className="animate-spin mr-2">⏳</span>
                            Đang dự đoán...
                          </>
                        ) : (
                          <>
                            <TrendingUp className="mr-2 h-5 w-5" />
                            Dự đoán giá
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Panel - Results */}
        <div className="space-y-6 lg:sticky lg:top-24">
          <AnimatePresence mode="wait">
            {prediction ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.4 }}
                className="space-y-6"
              >
                <PredictionResult result={prediction} onReset={handleReset} />
                <LocationMap
                  district={prediction.features_used.District}
                  ward={prediction.features_used.Ward}
                  street={prediction.features_used.Street}
                />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex items-center justify-center"
              >
                <Card className="w-full min-h-[500px] flex items-center justify-center border shadow-md rounded-3xl">
                  <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-32 h-32 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-full flex items-center justify-center mb-6 animate-float">
                      <TrendingUp className="w-16 h-16 text-primary/60 stroke-[2]" />
                    </div>
                    <h3 className="text-2xl font-bold mb-3">Kết quả dự đoán sẽ hiển thị ở đây</h3>
                    <p className="text-muted-foreground text-base max-w-md leading-relaxed">
                      Nhập mô tả nhà hoặc điền form để bắt đầu dự đoán giá
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Layout>
  )
}
