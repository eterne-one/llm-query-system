# 1. LLM 질문 프로그램
## 프로그램 기능
- open webUI 형태의 웹 인터페이스를 사용한다.
- 웹사이트 접속 시 로그인 처리를 수행한다.
- 질문을 받은 웹 사이트가 내부 백엔드 프로그램을 호출한다.
- 한글로 질문을 입력하면 번역용 LLM(gemma4:e2b)을 사용하여 번역한다.
(Argos Translate 는 실제 수행 결과 번역 능력이 매우 열악하여 gemma4:e2b 를 사용하는것으로 대체하였다)
- 영어로 번역한 질문을 '처리용 LLM' 을 호출하여 질문하고 답변을 받는다.
  - 최근 N 개의 세션 대화 이력을 포함하여 컨텍스트를 유지한다.
  - 사용자 체감 속도 향상을 위해 한 글자씩 출력되는 스트리밍(Streaming) 응답 방식을 사용한다.
- 답변을 받은 후 비동기(Async) 백그라운드 작업으로 '로그인 ID', 'Session_ID', '질문 일시', '한글 질문 내용', '번역한 영문 질문 내용', '답변 내용' 을 데이터베이스에 저장한다.
  - 스트리밍 방식은 답변이 한 글자씩 오기 때문에, 답변이 **모두 완료된 시점**을 포착하여 최종 결과물 전체를 한 번에 비동기로 DB에 저장해야 한다.
  - 백그라운드 DB 저장 작업이 진행되는 동안 LLM 추론 자원을 뺏지 않도록, 파이썬의 `asyncio`나 `FastAPI`의 `BackgroundTasks`를 활용하여 CPU 점유율을 적절히 배분한다.
- 답변을 웹 사이트로 반환한다.
- LLM 호출 실패, 번역 오류, 혹은 외부 접속 시도 실패 등 예외 상황 발생 시 별도 로그 테이블에 저장한다.
- 로그 테이블의 자료는 N 일간 보관하며, 용량 관리를 위해 그 이후 삭제한다.

## 프로그램 목록
- 웹 사이트
- 로그인 처리 프로그램
- 백엔드 메인 프로그램
- 처리용 LLM 호출 모듈 프로그램
- 내용을 데이터베이스에 저장하는 프로그램
  - 스트리밍 응답 완료 포착 시 후처리 함수로 동작한다.
- 예외 상황 발생 로그 저장 프로그램
- 정해진 기간을 초과하여 보관된 로그 테이블 자료를 삭제하는 프로그램
  - 파이썬의 `apscheduler` 라이브러리를 사용하여 사용자가 적은 특정 시간에 주기적 자동 수행 필요.

## 추가 필요 기능
- 외부에서 웹 사이트에 접속해서 원격으로 질문할 수 있는 기능

# 2. 질문 내용 조회 프로그램
## 프로그램 기능
- 목록 조회용 웹 사이트를 사용한다.
- 웹사이트 접속 시 로그인 처리를 수행한다.
- 조회 조건은 조회 일시 및 질문 키워드 검색 등이 있다.
- 조회 요청을 받은 웹 사이트가 내부 백엔드 프로그램을 호출한다.
- 백엔드 프로그램에서 데이터베이스를 조회하여 '질문 일시' 역순으로 정렬한 조회 결과를 웹 사이트로 반환한다.
- 정해진 갯수만큼 반환하며 스크롤 페이징 처리를 통해 계속 데이터를 이어 조회할 수 있다.
- 웹 사이트에서도 스크롤 페이징 처리를 해야 한다.

## 프로그램 목록
- 웹 사이트
- 백엔드 메인 프로그램
- 질문 내용 목록 조회 모듈 프로그램 (스크롤 페이징 기능 필요)

# 3. 데이터베이스 설정
## 질문 내용 저장 테이블
- 질문ID:시스템에서 생성하는 UUID 또는 Auto-increment 정수
- FK:사용자 고유번호(로그인 테이블)
- Session ID
- 질문 일시
- 한글 질문 내용
- 영문 질문 내용
- 답변 내용

## 로그인 테이블
- PK:사용자 고유번호
- 로그인ID
- 비밀번호(BCrypt나 Argon2를 사용하여 SALT-HASH 암호화)
- 사용자 이메일 주소

## 로그 테이블
- PK:로그 고유 식별자
- 로그 기록 일시
- 로그 레벨
- 발생 영역
- FK:사용자 고유번호(로그인 테이블)
- Session ID
- 오류 내용
- 입력값
- 스택트레이스
- 타임아웃 시간
- 외부 접속 발신지 IP

# 4. 상수 관리
- 컨텍스트를 유지할 대화 이력의 갯수 : 초기값 10
- 예외 발생 로그를 저장할 일자 수 : 초기값 30
- 예와 발생 로그를 삭제하는 자동 프로그램이 수행되는 시각 : 초기값 0300 (새벽 3시)

# 5. 부가내용
- 외부 접속을 위해 Cloudflare Tunnel 을 사용한다.
  - 맥북이 절전 모드(Sleep)로 들어가면 터널이 끊길 수 있으므로 '카페인(Caffeine)' 같은 앱을 쓰거나 시스템 설정에서 **"네트워크 액세스 시 잠자기 해제"** 옵션을 설정한다.
  - 터널을 통해 외부로 개방할 때, Cloudflare 대시보드에서 **'Access'** 설정을 통해 특정 이메일 인증을 한 번 더 거쳐 로그인 페이지와 더불어 2중 보안 장치를 구성한다.

# 6. 추가 노트
- [웹 페이지 에서 별도 암호화 없이 TLS/SSL 을 사용하면 되는 이유](Additional_Notes/Analysis_of_Password_Transmission_Security.md)
- [LLM 호출 시 세션의 이전 대화 내용을 얼마나 불러와서 함께 던져줄 지 결정하는 법](Additional_Notes/Optimizing_LLM_Session_History.md)
- [LLM 스트리밍 출력 방식에서 답변의 끝을 포착하는 방법](Additional_Notes/Detect_LLM_Stream_End.md)

# 7. 향후 확장 예정 기능
- 컨텍스트를 유지할 대화 이력의 갯수를 N개로 정하는 대신 Tokenizer 라이브러리를 활용하여 정확한 길이를 계산해 보자.
  - **토큰 카운터 모듈** 추가 필요

# 8. 폴더 및 파일 구조
llm-query-system/
├── .github/                # GitHub Actions (CI/CD) 워크플로우
├── docs/                   # 문서 저장소
│   ├── architecture/       # 설계 관련 문서
│   │   └── v05_Architecture.md
│   └── additional_notes/   # 부가 분석 문서
│       ├── Analysis_of_Password_Transmission_Security.md
│       ├── Optimizing_LLM_Session_History.md
│       └── Detect_LLM_Stream_End.md
├── src/                    # 백엔드 소스 코드 (FastAPI 기반)
│   ├── app/
│   │   ├── api/            # API 엔드포인트 (Routes)
│   │   │   ├── auth.py     # 로그인 및 인증 처리
│   │   │   ├── chat.py     # LLM 질문 및 스트리밍 응답
│   │   │   └── history.py  # 질문 내용 조회 및 페이징
│   │   ├── core/           # 핵심 설정 및 공통 모듈
│   │   │   ├── config.py   # 환경 변수 및 상수 관리 (0300시, N일 등)
│   │   │   └── security.py # BCrypt 암호화 및 JWT/Session 처리
│   │   ├── db/             # 데이터베이스 관련
│   │   │   ├── base.py     # SQLAlchemy/Tortoise 연결 설정
│   │   │   ├── models.py   # 테이블 스키마 (User, Chat, Log)
│   │   │   └── repository.py # DB CRUD 로직
│   │   ├── services/       # 비즈니스 로직 (모듈화)
│   │   │   ├── translator.py # 번역용 LLM 연동
│   │   │   ├── llm_client.py # LLM 호출 및 세션 관리
│   │   │   └── tokenizer.py  # (향후 확장) 토큰 카운터
│   │   ├── tasks/          # 백그라운드 및 스케줄링 작업
│   │   │   ├── background.py # 비동기 DB 저장 (FastAPI BackgroundTasks)
│   │   │   └── scheduler.py  # 로그 삭제 자동화 (APScheduler)
│   │   └── main.py         # 애플리케이션 진입점
├── web/                    # 프론트엔드 리소스 (Open WebUI 스타일)
│   ├── static/             # CSS, JS, Images
│   └── templates/          # HTML 템플릿
├── tests/                  # 유닛 테스트 및 통합 테스트
├── scripts/                # 설치 및 배포 스크립트 (Cloudflare 설정 등)
├── .gitignore              # Git 제외 목록 (.env, __pycache__ 등)
├── README.md               # 프로젝트 개요 및 실행 방법
├── requirements.txt        # 의존성 패키지 목록
└── .env.example            # 환경 변수 샘플 (API Key, DB URL 등)