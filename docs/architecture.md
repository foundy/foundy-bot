# 아키텍처

## 시스템 개요

```
GitHub Actions (cron: 0 0 * * *)
        │
        ▼
    main.py
        │
        ├── news_collector.py ──► RSS 피드 (TechCrunch, The Verge, Hacker News 등)
        │                         OpenAI API (뉴스 요약)
        │
        ├── history_manager.py ──► data/news_history.md (중복 확인)
        │
        └── slack_notifier.py ──► Slack Incoming Webhook
                │
                ▼
        history_manager.py ──► data/news_history.md (히스토리 갱신)
                │
                ▼
        GitHub Actions ──► git commit & push (news_history.md 업데이트)
```

## 모듈 설명

### `src/news_collector.py`

RSS 피드를 통해 IT/AI 뉴스를 수집합니다.

**뉴스 소스 (우선순위 순)**:
1. AI 전용 소스 (가중치 높음)
   - MIT Technology Review - AI
   - VentureBeat - AI
2. 일반 IT 소스 (가중치 낮음)
   - Hacker News (상위 30개)
   - TechCrunch
   - The Verge

**AI 관련성 판단**:
- `AI_KEYWORDS` 리스트의 키워드 포함 여부 확인
- AI 소스에서 수집된 뉴스는 자동으로 높은 우선순위 부여

**요약**:
- OpenAI GPT-4o-mini를 사용하여 200자 이내로 요약
- API 호출 실패 시 RSS 피드의 원본 description 사용 (fallback)

### `src/history_manager.py`

`data/news_history.md` 파일을 통해 히스토리를 관리합니다.

**파일 형식**:
```markdown
## 2025-01-15

- [제목](URL) — 요약 내용 (200자 이내)
- [제목](URL) — 요약 내용 (200자 이내)

## 2025-01-14

- [제목](URL) — 요약 내용 (200자 이내)
```

**중복 감지**:
- URL 완전 일치 확인
- 제목 정규화 후 비교 (소문자, 특수문자 제거)

**정리 정책**:
- 10일 이상 된 섹션 자동 삭제
- 실행마다 `cleanup_old_entries()` 호출

### `src/slack_notifier.py`

Slack Block Kit을 사용하여 구조화된 메시지를 전송합니다.

**메시지 구조**:
```
📰 오늘의 IT/AI 뉴스 (2025-01-15)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI 소식
• 제목 — 요약
• 제목 — 요약

💻 IT 소식
• 제목 — 요약
• 제목 — 요약
```

## 데이터 흐름

1. GitHub Actions가 매일 00:00 UTC (09:00 KST)에 워크플로우 시작
2. `main.py` 실행
3. `news_collector.py`가 RSS 피드에서 최신 뉴스 수집 (최대 20개)
4. `history_manager.py`가 `data/news_history.md` 로드
5. 이미 전송된 뉴스 필터링 (중복 제거)
6. 새 뉴스에 대해 OpenAI로 200자 이내 요약 생성
7. `slack_notifier.py`가 Slack으로 메시지 전송
8. `history_manager.py`가 전송된 뉴스를 `data/news_history.md`에 추가
9. 10일 이상 된 기록 자동 정리
10. GitHub Actions가 `data/news_history.md` 변경사항을 커밋 & 푸시

## 보안

- API 키 및 Webhook URL은 GitHub Secrets에만 저장
- `data/news_history.md`에는 제목, URL, 요약만 저장 (민감 정보 없음)
- GitHub Actions 워크플로우의 `contents: write` 권한은 히스토리 파일 커밋에만 사용
