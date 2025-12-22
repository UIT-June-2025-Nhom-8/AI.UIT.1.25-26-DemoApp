import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, ExternalLink, Search } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface LocationMapProps {
  district?: string
  ward?: string
  street?: string
}

interface LocationInfo {
  lat: number
  lng: number
  address: string
  district?: string
}

export function LocationMap({ district, ward, street }: LocationMapProps) {
  const [location, setLocation] = useState<LocationInfo | null>(null)
  const [loading, setLoading] = useState(false)

  // Ho Chi Minh City center as default
  const defaultLocation: LocationInfo = {
    lat: 10.8231,
    lng: 106.6297,
    address: 'TP. Hồ Chí Minh',
  }

  useEffect(() => {
    if (district) {
      geocodeAddress()
    }
  }, [district, ward, street])

  const geocodeAddress = async () => {
    setLoading(true)
    try {
      // Build address string
      const addressParts = [street, ward, district, 'Ho Chi Minh City, Vietnam']
        .filter(Boolean)
        .join(', ')

      // Use Nominatim (OpenStreetMap) for geocoding
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(addressParts)}&limit=1`
      )
      const data = await response.json()

      if (data && data.length > 0) {
        setLocation({
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon),
          address: data[0].display_name,
          district: district,
        })
      } else {
        // Fallback to district only
        const districtResponse = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
            `${district}, Ho Chi Minh City, Vietnam`
          )}&limit=1`
        )
        const districtData = await districtResponse.json()

        if (districtData && districtData.length > 0) {
          setLocation({
            lat: parseFloat(districtData[0].lat),
            lng: parseFloat(districtData[0].lon),
            address: districtData[0].display_name,
            district: district,
          })
        } else {
          setLocation(defaultLocation)
        }
      }
    } catch (error) {
      console.error('Geocoding error:', error)
      setLocation(defaultLocation)
    } finally {
      setLoading(false)
    }
  }

  const currentLocation = location || defaultLocation

  const searchOnGoogle = () => {
    const query = [street, ward, district, 'Ho Chi Minh City']
      .filter(Boolean)
      .join(', ')
    window.open(`https://www.google.com/search?q=${encodeURIComponent(query + ' nhà đất')}`, '_blank')
  }

  const searchOnGoogleMaps = () => {
    const query = [street, ward, district, 'Ho Chi Minh City']
      .filter(Boolean)
      .join(', ')
    window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`, '_blank')
  }

  // OpenStreetMap iframe URL
  const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${currentLocation.lng - 0.01},${currentLocation.lat - 0.01},${currentLocation.lng + 0.01},${currentLocation.lat + 0.01}&layer=mapnik&marker=${currentLocation.lat},${currentLocation.lng}`

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-primary" />
            Vị trí & Tìm kiếm
          </CardTitle>
          <CardDescription>
            {location?.address || 'TP. Hồ Chí Minh'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Map */}
          <div className="h-64 rounded-lg overflow-hidden border">
            {loading ? (
              <div className="w-full h-full flex items-center justify-center bg-muted">
                <span className="animate-pulse">Đang tải bản đồ...</span>
              </div>
            ) : (
              <iframe
                width="100%"
                height="100%"
                frameBorder="0"
                scrolling="no"
                marginHeight={0}
                marginWidth={0}
                src={mapUrl}
                style={{ border: 0 }}
              />
            )}
          </div>

          {/* Search Buttons */}
          <div className="space-y-2">
            <div className="text-sm font-medium">Tìm kiếm nhà đất tương tự:</div>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={searchOnGoogle}
                className="w-full"
              >
                <Search className="w-4 h-4 mr-2" />
                Tìm trên Google
                <ExternalLink className="w-3 h-3 ml-auto" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={searchOnGoogleMaps}
                className="w-full"
              >
                <MapPin className="w-4 h-4 mr-2" />
                Google Maps
                <ExternalLink className="w-3 h-3 ml-auto" />
              </Button>
            </div>
          </div>

          {/* Location Details */}
          {(district || ward || street) && (
            <div className="pt-4 border-t space-y-2 text-sm">
              {district && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Quận/Huyện:</span>
                  <span className="font-medium">{district}</span>
                </div>
              )}
              {ward && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Phường/Xã:</span>
                  <span className="font-medium">{ward}</span>
                </div>
              )}
              {street && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Đường:</span>
                  <span className="font-medium">{street}</span>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
