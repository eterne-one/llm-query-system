# translator.py test command:
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -c "
from src.app.services.translator import translator
ko_query = '서울의 맛집 3곳만 추천해줘'
en_query = translator.translate_ko_to_en(ko_query)
print(f'\n[한글 입력]: {ko_query}')
print(f'[Gemma 번역]: {en_query}')
"

# llm-client.py test command:
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -c "
from src.app.services.llm_client import llm_client
import sys

print('\n[LLM Test Start - Model: gemma2:2b]')
print('질문: What is the capital of South Korea?')
print('답변: ', end='', flush=True)

## 스트리밍 응답 출력 테스트
for chunk in llm_client.ask_question_stream('test_session_01', 'What is the capital of South Korea?'):
    print(chunk, end='', flush=True)

print('\n\n[Test 완료] 대화 이력이 저장되었는지 확인합니다...')
history = llm_client._get_session_history('test_session_01')
print(f'현재 세션에 저장된 메시지 개수: {len(history)}개')
"

# translator.py + llm_client.py test command:
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -c "
from src.app.services.translator import translator
from src.app.services.llm_client import llm_client

ko_query = '서울의 맛집 3곳만 추천해줘'
en_query = translator.translate_ko_to_en(ko_query)
print(f'\n[한글 입력]: {ko_query}')
print(f'[번역 결과]: {en_query}\n')
print('[Gemma 답변]: ', end='', flush=True)

for chunk in llm_client.ask_question_stream('integrated_test', en_query):
    print(chunk, end='', flush=True)
print(\"\n\")
"