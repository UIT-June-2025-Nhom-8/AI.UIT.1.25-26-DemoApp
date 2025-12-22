/**
 * Valid values for categorical features
 * Hardcoded to ensure prediction accuracy
 */

export const HOUSE_DIRECTIONS = [
  'Đông',
  'Tây',
  'Nam',
  'Bắc',
  'Đông Nam',
  'Đông Bắc',
  'Tây Nam',
  'Tây Bắc',
]

export const BALCONY_DIRECTIONS = [
  'Đông',
  'Tây',
  'Nam',
  'Bắc',
  'Đông Nam',
  'Đông Bắc',
  'Tây Nam',
  'Tây Bắc',
]

export const LEGAL_STATUSES = [
  'Sổ đỏ',
  'Sổ hồng',
  'Hợp đồng',
  'Đang chờ sổ',
  'Không rõ',
]

export const FURNITURE_STATES = [
  'Cao cấp',
  'Đầy đủ',
  'Cơ bản',
  'Không nội thất',
  'Không rõ',
]

// Major districts in Vietnam cities
export const DISTRICTS = {
  'Hồ Chí Minh': [
    'Quận 1',
    'Quận 2',
    'Quận 3',
    'Quận 4',
    'Quận 5',
    'Quận 6',
    'Quận 7',
    'Quận 8',
    'Quận 9',
    'Quận 10',
    'Quận 11',
    'Quận 12',
    'Thủ Đức',
    'Bình Thạnh',
    'Tân Bình',
    'Tân Phú',
    'Phú Nhuận',
    'Gò Vấp',
    'Bình Tân',
    'Bình Chánh',
    'Hóc Môn',
    'Củ Chi',
    'Nhà Bè',
    'Cần Giờ',
  ],
  'Hà Nội': [
    'Ba Đình',
    'Hoàn Kiếm',
    'Hai Bà Trưng',
    'Đống Đa',
    'Tây Hồ',
    'Cầu Giấy',
    'Thanh Xuân',
    'Hoàng Mai',
    'Long Biên',
    'Nam Từ Liêm',
    'Bắc Từ Liêm',
    'Hà Đông',
  ],
  'Đà Nẵng': [
    'Hải Châu',
    'Thanh Khê',
    'Sơn Trà',
    'Ngũ Hành Sơn',
    'Liên Chiểu',
    'Cẩm Lệ',
    'Hòa Vang',
  ],
  'Bình Dương': [
    'Thủ Dầu Một',
    'Dĩ An',
    'Thuận An',
    'Tân Uyên',
    'Bến Cát',
    'Bàu Bàng',
    'Dầu Tiếng',
    'Phú Giáo',
  ],
}

export const CITIES = ['Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Bình Dương']

// Get all districts (flattened)
export const ALL_DISTRICTS = Object.values(DISTRICTS).flat()
