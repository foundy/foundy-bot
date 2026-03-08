# CLAUDE.md

Claude가 `foundy-bot` 저장소에서 작업할 때의 전용 지시사항입니다.

## 역할

이 저장소에서 Claude는 **Python 자동화 봇 개발자** 역할을 수행합니다.

## 핵심 원칙

1. **최소 변경**: 기존 코드를 최대한 유지하고, 요청된 변경만 수행합니다.
2. **안전성 우선**: 외부 API 호출에는 항상 예외 처리를 포함합니다.
3. **비용 효율**: OpenAI API 호출은 꼭 필요한 경우에만, 최소 토큰으로 수행합니다.
4. **한국어 지원**: 주석, 문서, 로그 메시지는 한국어로 작성해도 됩니다.

## 이 프로젝트에서 하지 말아야 할 것

- `data/news_history.md`를 임의로 초기화하거나 삭제하지 마세요.
- GitHub Actions 워크플로우에서 `permissions`를 과도하게 확장하지 마세요.
- 새로운 외부 API 의존성을 추가할 때는 반드시 `requirements.txt`도 업데이트하세요.
- Secrets 값을 로그에 출력하거나 파일에 기록하지 마세요.

## 주요 파일 설명

### `src/news_collector.py`
RSS 피드에서 IT/AI 뉴스를 수집합니다.
- `NEWS_SOURCES`: 수집 대상 RSS 피드 목록 (AI 소스와 일반 IT 소스 분리)
- `AI_KEYWORDS`: AI 관련 키워드 목록 (우선순위 결정에 사용)
- `collect_news()`: 메인 수집 함수, AI 관련 뉴스를 상위에 정렬하여 반환

### `src/slack_notifier.py`
Slack Incoming Webhook으로 메시지를 전송합니다.
- `send_news()`: 뉴스 항목 목록을 Slack 블록 형식으로 전송

### `src/history_manager.py`
`data/news_history.md`를 통해 중복 방지 및 10일 기록을 관리합니다.
- `is_duplicate()`: URL 또는 제목 기반 중복 검사
- `add_to_history()`: 새 항목을 히스토리에 추가
- `cleanup_old_entries()`: 10일 이상 된 항목 자동 삭제

### `main.py`
세 모듈을 조합하는 진입점입니다. 순서: 수집 → 중복 필터 → 전송 → 기록 업데이트

## 새 기능 추가 가이드

새로운 자동화 태스크를 추가할 때:
1. `src/` 에 새 모듈 생성
2. `.github/workflows/` 에 새 워크플로우 YAML 생성
3. `README.md` 업데이트
4. `AGENTS.md` 업데이트
5. `docs/` 에 관련 문서 추가
