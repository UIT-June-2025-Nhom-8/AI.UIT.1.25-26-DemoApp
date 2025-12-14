/**
 * Utility functions to extract categorical values from model metadata
 */

export interface CategoricalValues {
  directions: string[]
  balconyDirections: string[]
  legalStatuses: string[]
  districts: string[]
  furniture: string[]
}

/**
 * Extract categorical values from model metadata feature_names
 */
export function extractCategoricalValues(featureNames: string[]): CategoricalValues {
  const directions = new Set<string>()
  const balconyDirections = new Set<string>()
  const legalStatuses = new Set<string>()
  const districts = new Set<string>()
  const furniture = new Set<string>()

  featureNames.forEach((name) => {
    // Extract House direction
    if (name.startsWith('House direction_')) {
      const value = name.replace('House direction_', '')
      directions.add(value)
    }
    // Extract Balcony direction
    else if (name.startsWith('Balcony direction_')) {
      const value = name.replace('Balcony direction_', '')
      if (value !== 'Unknown') {
        balconyDirections.add(value)
      }
    }
    // Extract Legal status
    else if (name.startsWith('Legal status_')) {
      const value = name.replace('Legal status_', '')
      legalStatuses.add(value)
    }
    // Extract Districts
    else if (name.startsWith('new_district_')) {
      const value = name.replace('new_district_', '')
      if (value !== 'Unknown') {
        districts.add(value)
      }
    }
  })

  // Add common furniture states (not in feature names, but commonly used)
  furniture.add('Đầy đủ')
  furniture.add('Cơ bản')
  furniture.add('Không nội thất')
  furniture.add('Cao cấp')

  return {
    directions: Array.from(directions).sort(),
    balconyDirections: Array.from(balconyDirections).sort(),
    legalStatuses: Array.from(legalStatuses).sort(),
    districts: Array.from(districts).sort(),
    furniture: Array.from(furniture).sort(),
  }
}

/**
 * Map frontend field names to display names
 */
export const fieldDisplayNames: Record<string, string> = {
  Area: 'Diện tích (m²)',
  Bedrooms: 'Số phòng ngủ',
  Bathrooms: 'Số toilet',
  Floors: 'Số tầng',
  Frontage: 'Mặt tiền (m)',
  AccessRoad: 'Đường vào (m)',
  District: 'Quận/Huyện',
  Ward: 'Phường/Xã',
  Street: 'Đường',
  Direction: 'Hướng nhà',
  BalconyDirection: 'Hướng ban công',
  LegalStatus: 'Giấy tờ pháp lý',
  Furniture: 'Nội thất',
}

/**
 * Map backend feature names to frontend field names
 */
export const backendToFrontendFieldMap: Record<string, string> = {
  'House direction': 'Direction',
  'Balcony direction': 'BalconyDirection',
  'Legal status': 'LegalStatus',
  'new_district': 'District',
}
