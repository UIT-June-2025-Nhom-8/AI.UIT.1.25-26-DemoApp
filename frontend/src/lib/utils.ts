import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  if (price >= 1_000_000_000) {
    return `${(price / 1_000_000_000).toFixed(2)} tỷ`
  } else if (price >= 1_000_000) {
    return `${(price / 1_000_000).toFixed(0)} triệu`
  }
  return price.toLocaleString('vi-VN') + ' VND'
}

export function formatNumber(num: number): string {
  return num.toLocaleString('vi-VN')
}
