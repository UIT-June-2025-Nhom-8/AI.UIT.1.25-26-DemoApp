import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  // Model outputs price in BILLIONS (tỷ) - range 1-12
  // No conversion needed, just format
  if (price >= 1) {
    if (price >= 10) {
      return `${price.toFixed(1)} tỷ VND`
    } else {
      return `${price.toFixed(2)} tỷ VND`
    }
  } else {
    // Convert to millions for values < 1 billion (rare)
    const millions = price * 1000
    return `${millions.toFixed(0)} triệu VND`
  }
}

export function formatNumber(num: number): string {
  return num.toLocaleString('vi-VN')
}
