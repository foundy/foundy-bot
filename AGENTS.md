# AGENTS.md

AI 에이전트(Copilot, Codex, Claude 등)가 이 저장소에서 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

`foundy-bot`은 GitHub Actions 기반의 자동화 봇입니다. Python으로 작성되어 있으며,
매일 오전 9시(KST)에 IT/AI 뉴스를 수집하여 Slack으로 알림을 전송합니다.

## 디렉토리 구조

```
src/               # 핵심 모듈
  news_collector.py    # RSS 피드 수집 및 AI/IT 필터링
  slack_notifier.py    # Slack 웹훅 전송
  history_manager.py   # 10일 히스토리 및 중복 방지
data/              # 런타임 데이터
  news_history.md      # 전송된 뉴스 기록 (GitHub Actions가 커밋)
docs/              # 문서
.github/workflows/ # GitHub Actions 워크플로우
main.py            # 진입점
requirements.txt   # Python 의존성
```

## 코딩 컨벤션

- **언어**: Python 3.11+
- **스타일**: PEP 8 준수
- **타입 힌트**: 모든 함수에 타입 힌트 사용
- **인코딩**: UTF-8 (한국어 주석 허용)
- **에러 처리**: 외부 API 호출은 반드시 예외 처리
- **로깅**: `print()` 대신 `logging` 모듈 사용

## 환경 변수 / Secrets

| 이름 | 설명 | 필수 |
|------|------|------|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 (뉴스 요약, 미설정 시 요약을 건너뛰고 RSS description을 그대로 사용) | ⚪ |

## 작업 시 주의사항

1. `data/news_history.md`는 GitHub Actions에서 자동으로 커밋됩니다. 직접 수정 시 충돌에 주의하세요.
2. 새로운 뉴스 소스를 추가할 때는 `src/news_collector.py`의 `NEWS_SOURCES` 리스트를 수정하세요.
3. AI 관련 키워드는 `src/news_collector.py`의 `AI_KEYWORDS` 리스트에 정의되어 있습니다.
4. Slack 메시지 포맷 변경 시 `src/slack_notifier.py`를 수정하세요.

## 테스트

```bash
pip install -r requirements.txt
# 환경 변수 설정 후
python main.py
```

## 관련 문서

- [아키텍처](docs/architecture.md)
- [설정 가이드](docs/setup.md)
