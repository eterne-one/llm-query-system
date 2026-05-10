import openai
from typing import List, Dict, Generator
# 설정 파일에서 N개 이력 제한 및 모델명 등을 가져온다고 가정
from src.app.core.config import MAX_HISTORY_COUNT

"""
[기술적 정의]
본 모듈은 로컬에서 실행 중인 Ollama API를 통해 Gemma 모델과 통신합니다.
- Ollama의 OpenAI 호환 엔드포인트(http://localhost:11434/v1)를 사용합니다.
- HTTP 스트리밍을 통해 로컬 추론 결과를 실시간으로 사용자에게 전달합니다.

[기능적 정의]
영문으로 번역된 질문을 받아 로컬 LLM(Gemma)에게 전달하며, 
설계 문서에 명시된 대로 이전 대화 문맥(Context)을 포함하여 답변을 생성합니다.
"""

class LLMClient:
    def __init__(self, model_name: str = "gemma4:e4b"):
        """
        Ollama 전용 클라이언트 초기화
        :param model_name: Ollama에 로드된 모델명 (예: gemma2:2b)
        """
        # Ollama는 기본적으로 API Key를 체크하지 않지만, 형식상 'ollama'를 넣습니다.
        # base_url은 Ollama의 로컬 API 주소를 가리킵니다.
        self.client = openai.OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama" 
        )
        self.model_name = model_name
        # 세션별 대화 이력을 보관할 메모리 저장소
        self.session_histories: Dict[str, List[Dict[str, str]]] = {}

    def _get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        특정 세션의 대화 이력을 가져오고 상수에 정의된 N개까지만 유지합니다.
        """
        if session_id not in self.session_histories:
            self.session_histories[session_id] = []
        return self.session_histories[session_id][-MAX_HISTORY_COUNT:]

    def ask_question_stream(self, session_id: str, prompt: str) -> Generator[str, None, None]:
        """
        [기능] Gemma 모델에게 스트리밍 방식으로 질문하고 답변 조각을 반환합니다.
        """
        # 1. 이전 대화 문맥 구성 (History + Current Prompt)
        history = self._get_session_history(session_id)
        # messages = history + [{"role": "user", "content": prompt}]

        # 질문 뒤에 한글 답변 요청 메시지 추가
        # 영문으로 생각(Reasoning)하되, 출력(Output)은 한글로 하도록 유도
        refined_prompt = f"{prompt}\n\nPlease respond in Korean."
        current_messages = history + [{"role": "user", "content": refined_prompt}]

        try:
            # 2. Ollama API 호출 (Gemma 모델 사용)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=current_messages,
                stream=True,
                # 필요시 로컬 모델의 창의성 조절을 위해 temperature 등을 추가할 수 있습니다.
                temperature=0.7 
            )

            full_response = ""
            for chunk in response:
                # Ollama로부터 오는 스트리밍 조각 처리
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    yield content

            # 3. 답변이 모두 완료된 후 대화 이력 갱신
            # 설계 문서 요구사항: 대화 컨텍스트 유지를 위해 히스토리에 추가
            self.session_histories[session_id].append({"role": "user", "content": prompt})
            self.session_histories[session_id].append({"role": "assistant", "content": full_response})

        except Exception as e:
            # 예외 상황 발생 시 (Ollama 미구동 등) 에러 메시지 반환
            print(f"[Ollama Error] 로컬 모델 호출 실패: {e}")
            yield "죄송합니다. 로컬 LLM 서비스를 일시적으로 사용할 수 없습니다."

# 싱글톤 인스턴스 생성 (사용자가 지정한 gemma 모델명으로 설정)
llm_client = LLMClient(model_name="gemma4:e4b")