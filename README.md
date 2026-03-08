# foundy-bot

나만의 GitHub Actions 기반 자동화 봇입니다.

## 소개

`foundy-bot`은 GitHub Actions를 통해 스케줄링된 작업을 자동으로 실행하는 봇입니다.
AI 및 IT 관련 최신 소식을 수집하여 Slack으로 알림을 전송합니다.

## 기능

### IT 뉴스 알림 (`it-news`)
- **스케줄**: 매일 오전 9시 (KST) 자동 실행
- **소식 수집**: AI 관련 내용 비중을 높게, 그 외 개발자 참고 IT 뉴스 수집
- **요약**: 각 소식을 200자 이내로 요약
- **Slack 알림**: 수집된 소식을 Slack 채널로 전송
- **중복 방지**: 이미 전송한 소식은 재전송하지 않음
- **히스토리 관리**: `data/news_history.md`에 최근 10일간의 기록 유지

## 프로젝트 구조

```
foundy-bot/
├── README.md                   # 프로젝트 소개
├── AGENTS.md                   # AI 에이전트 가이드
├── CLAUDE.md                   # Claude 전용 지시사항
├── requirements.txt            # Python 의존성
├── main.py                     # 메인 실행 파일
├── src/
│   ├── news_collector.py       # 뉴스 수집 모듈
│   ├── slack_notifier.py       # Slack 알림 모듈
│   └── history_manager.py      # 히스토리 관리 모듈
├── data/
│   └── news_history.md         # 전송된 뉴스 히스토리 (최근 10일)
├── docs/
│   ├── architecture.md         # 아키텍처 문서
│   └── setup.md                # 설정 가이드
└── .github/
    └── workflows/
        └── it-news.yml         # GitHub Actions 워크플로우
```

## 설정

자세한 설정 방법은 [docs/setup.md](docs/setup.md)를 참고하세요.

필요한 GitHub Secrets:
- `SLACK_WEBHOOK_URL`: Slack Incoming Webhook URL
- `OPENAI_API_KEY`: OpenAI API 키 (뉴스 요약에 사용)

## 문서

- [아키텍처 문서](docs/architecture.md)
- [설정 가이드](docs/setup.md)

