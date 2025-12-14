"""
LLM Parser - Parse mô tả nhà tiếng Việt thành features
======================================================
Sử dụng HuggingFace Inference API (FREE)

Usage:
    from llm_parser import LLMParser
    
    parser = LLMParser(token="hf_xxxxxxxxxx")
    features = parser.parse("Nhà 100m2, 3PN, 2WC, quận 7, sổ hồng")
    # Output: {'Area': 100, 'Bedrooms': 3, 'Bathrooms': 2, 'District': 'Quận 7', 'LegalStatus': 'Sổ hồng'}
"""

import json
import re
from typing import Dict, Any, List, Optional
from huggingface_hub import InferenceClient


class LLMParser:
    """
    Parse mô tả nhà tiếng Việt thành dictionary features sử dụng LLM
    
    Attributes:
        token: HuggingFace API token
        models: List models để thử
        
    Example:
        parser = LLMParser(token="hf_xxxxxxxxxx")
        features = parser.parse("Nhà 100m2, 3PN, quận 7")
    """
    
    # Models mặc định (đã test hoạt động)
    DEFAULT_MODELS = [
        "Qwen/Qwen2.5-72B-Instruct",
        "google/gemma-2-2b-it",
    ]
    
    def __init__(self, token: str = None, models: List[str] = None):
        """
        Khởi tạo LLM Parser
        
        Args:
            token: HuggingFace token (lấy tại https://huggingface.co/settings/tokens)
                   Token Type: "Read"
            models: List models để thử (None = dùng DEFAULT_MODELS)
            
        Raises:
            ValueError: Nếu token không hợp lệ
        """
        # Kiểm tra token
        if token is None or token == "SetTokenHere":
            raise ValueError(
                "\n" + "=" * 60 +
                "\n❌ CHƯA SET TOKEN!"
                "\n" + "-" * 60 +
                "\nCách lấy token:"
                "\n  1. Vào: https://huggingface.co/settings/tokens"
                "\n  2. Click 'Create new token'"
                "\n  3. Chọn Token Type: 'Read'"
                "\n  4. Copy token (bắt đầu bằng 'hf_')"
                "\n\nCách dùng:"
                "\n  parser = LLMParser(token='hf_xxxxxxxxxx')"
                "\n" + "=" * 60
            )
        
        if not token.startswith("hf_"):
            raise ValueError("Token phải bắt đầu bằng 'hf_'")
        
        self.token = token
        self.models = models or self.DEFAULT_MODELS
        self._client = InferenceClient(token=token)
    
    def parse(self, text: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Parse mô tả nhà thành dictionary features
        
        Args:
            text: Mô tả nhà, vd: "Nhà 100m2, 3PN, 2WC, quận 7, sổ hồng"
            verbose: In log hay không
            
        Returns:
            Dict với các features đã extract, vd:
            {
                'Area': 100,
                'Bedrooms': 3,
                'Bathrooms': 2,
                'District': 'Quận 7',
                'LegalStatus': 'Sổ hồng'
            }
            
        Các trường có thể trả về:
            - Area: diện tích (m2)
            - Bedrooms: số phòng ngủ
            - Bathrooms: số toilet/WC
            - Floors: số tầng
            - Frontage: mặt tiền (m)
            - AccessRoad: đường trước nhà (m)
            - Direction: hướng nhà
            - BalconyDirection: hướng ban công
            - District: quận/huyện
            - Ward: phường/xã
            - City: thành phố
            - LegalStatus: pháp lý
            - Furniture: nội thất
        """
        prompt = self._build_prompt(text)
        messages = [{"role": "user", "content": prompt}]
        
        for model in self.models:
            model_name = model.split('/')[-1]
            try:
                if verbose:
                    print(f"🔄 {model_name}...", end=" ")
                
                response = self._client.chat_completion(
                    model=model,
                    messages=messages,
                    max_tokens=300,
                    temperature=0.1,
                )
                
                result_text = response.choices[0].message.content.strip()
                parsed = self._extract_json(result_text)
                
                if parsed:
                    if verbose:
                        print("✅")
                    return parsed
                
                if verbose:
                    print("⚠️ JSON rỗng")
                    
            except Exception as e:
                if verbose:
                    print(f"❌ {str(e)[:40]}")
                continue
        
        if verbose:
            print("❌ Tất cả models đều thất bại!")
        return {}
    
    def _build_prompt(self, text: str) -> str:
        """Tạo prompt cho LLM"""
        return f"""Trích xuất thông tin bất động sản từ câu tiếng Việt sau thành JSON.

Câu: "{text}"

Các trường cần trích xuất (chỉ trả về những trường có trong câu):
- Area: diện tích (số, m2)
- Bedrooms: số phòng ngủ
- Bathrooms: số toilet/WC
- Floors: số tầng
- Frontage: mặt tiền (m)
- AccessRoad: đường trước nhà (m)
- Direction: hướng nhà
- BalconyDirection: hướng ban công
- District: quận/huyện
- Ward: phường/xã
- City: thành phố
- LegalStatus: pháp lý (sổ đỏ, sổ hồng...)
- Furniture: nội thất

CHỈ TRẢ VỀ JSON THUẦN TÚY, KHÔNG GIẢI THÍCH.
Ví dụ: {{"Area": 100, "Bedrooms": 3, "District": "Quận 7"}}"""
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON từ response text"""
        text = text.strip()
        
        # Thử parse trực tiếp
        try:
            return json.loads(text)
        except:
            pass
        
        # Tìm JSON trong text
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            r'\{.*?\}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group()
                    return json.loads(json_str.strip())
                except:
                    continue
        
        return {}


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🏠 LLM PARSER TEST")
    print("=" * 60)
     
    token = "set token here"  # Thay bằng token của bạn
    
    if not token:
        print("❌ Không có token!")
        sys.exit(1)
    
    # Khởi tạo parser
    try:
        parser = LLMParser(token=token)
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    # Test cases
    test_cases = [
        "Bán nhà 120m2, 3 phòng ngủ, 2 toilet, quận 7, sổ hồng, hướng đông nam",
        "Nhà phố 80m2 Bình Thạnh, 4 tầng, full nội thất cao cấp",
        "Bán gấp căn nhà 200m2, 5PN, 4WC, mặt tiền 6m, quận 1",
        "Nhà hẻm 5m, 60m2, 2 lầu, phường Tân Định, quận 1, giá 4 tỷ",
    ]
    
    for text in test_cases:
        print(f"\n📝 Input: {text}")
        features = parser.parse(text)
        print(f"📋 Output: {features}")
        print("-" * 60)