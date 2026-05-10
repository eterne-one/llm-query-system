# src/app/core/config.py

# 설계 문서 4번: 컨텍스트를 유지할 대화 이력의 갯수 (초기값 10)
MAX_HISTORY_COUNT = 10

# 나중에 로그 삭제 스케줄링 시 사용할 설정 (예: 30일)
LOG_RETENTION_DAYS = 30

# 번역용 LLM
TRANSLATION_MODEL = "gemma4:e2b"