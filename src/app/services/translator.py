import openai
from src.app.core.config import TRANSLATION_MODEL

class LLMTranslator:
    def __init__(self, model_name: str = "gemma4:e2b"):
        self.client = openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.model_name = model_name

    def translate_ko_to_en(self, text: str) -> str:
        if not text or not text.strip():
            return ""
        
        try:
            # 의도 파악을 위한 강화된 시스템 프롬프트
            system_prompt = (
                "You are a helpful assistant that translates Korean user queries into natural English questions "
                "for a Large Language Model. Capture the user's intent (request, question, command). "
                "For example, if the user says '추천해줘', translate it as a request like 'Please recommend'. "
                "Respond ONLY with the translated English text."
            )
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate this: '{text}'"}
                ],
                temperature=0.1, # 일관성을 위해 온도를 더 낮춤
                stream=False
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[Translation Error] {e}")
            return text

translator = LLMTranslator()