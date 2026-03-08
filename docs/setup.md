# 설정 가이드

## 사전 요구사항

- Python 3.11 이상
- GitHub 저장소 (Actions 활성화)
- Slack 워크스페이스 (Incoming Webhook 생성 권한)
- OpenAI API 계정

## 1. Slack Incoming Webhook 설정

1. [Slack API 앱 관리 페이지](https://api.slack.com/apps)에 접속합니다.
2. **Create New App** → **From scratch** 선택
3. 앱 이름 입력 후 워크스페이스 선택
4. 왼쪽 메뉴에서 **Incoming Webhooks** 클릭
5. **Activate Incoming Webhooks** 토글 ON
6. **Add New Webhook to Workspace** 클릭
7. 알림을 받을 채널 선택 후 허용
8. 생성된 Webhook URL 복사 (예: `https://hooks.slack.com/services/T.../B.../...`)

## 2. OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/)에 로그인합니다.
2. 우측 상단 계정 → **API keys** 클릭
3. **Create new secret key** 클릭
4. 키 이름 입력 후 생성
5. 생성된 API 키 복사 (다시 확인 불가)

## 3. GitHub Secrets 설정

1. GitHub 저장소 페이지에서 **Settings** → **Secrets and variables** → **Actions** 클릭
2. **New repository secret** 클릭하여 아래 두 가지 추가:

| Secret 이름 | 값 |
|-------------|-----|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL |
| `OPENAI_API_KEY` | OpenAI API 키 |

## 4. GitHub Actions 권한 설정

히스토리 파일을 자동으로 커밋하려면 Actions 쓰기 권한이 필요합니다.

1. **Settings** → **Actions** → **General** 이동
2. **Workflow permissions** 섹션에서 **Read and write permissions** 선택
3. **Save** 클릭

## 5. 로컬 실행 (테스트용)

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export OPENAI_API_KEY="sk-..."

# 실행
python main.py
```

## 6. 워크플로우 수동 실행

GitHub Actions 탭에서 **IT News Slack Notification** 워크플로우를 선택하고
**Run workflow** 버튼으로 수동 실행할 수 있습니다.

## 7. 뉴스 소스 커스터마이징

`src/news_collector.py`의 `NEWS_SOURCES` 리스트를 수정하여 뉴스 소스를 변경할 수 있습니다.

```python
NEWS_SOURCES = [
    # AI 관련 소스 (is_ai_source=True)
    {"url": "https://...", "name": "소스명", "is_ai_source": True},
    # 일반 IT 소스
    {"url": "https://...", "name": "소스명", "is_ai_source": False},
]
```

## 8. 알림 수신 개수 조정

`main.py`의 `MAX_NEWS_ITEMS` 상수를 변경하여 하루에 전송할 최대 뉴스 수를 조정할 수 있습니다.

```python
MAX_NEWS_ITEMS = 10  # 기본값: 10개
```

## 트러블슈팅

### Slack 알림이 오지 않을 때
- `SLACK_WEBHOOK_URL` Secret이 올바르게 설정되었는지 확인
- GitHub Actions 로그에서 오류 메시지 확인

### 요약이 영어로 나올 때
- `OPENAI_API_KEY`가 유효한지 확인
- OpenAI 계정의 크레딧이 남아있는지 확인
- 크레딧 부족 시 RSS 원본 description을 fallback으로 사용합니다

### 히스토리 파일이 업데이트되지 않을 때
- GitHub Actions 워크플로우 권한에서 **Read and write permissions** 설정 확인
- (참고: 4번 단계)
