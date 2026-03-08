"""
Slack 알림 모듈

Slack Incoming Webhook을 사용하여 IT/AI 뉴스를 전송합니다.
"""

import json
import logging
import os
from datetime import date
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from src.news_collector import NewsItem

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_ENV = "SLACK_WEBHOOK_URL"
REQUEST_TIMEOUT = 10  # seconds


def _build_blocks(items: "list[NewsItem]", today: str) -> list[dict]:
    """Slack Block Kit 형식으로 메시지 블록을 구성합니다."""
    ai_items = [i for i in items if i.is_ai_related]
    it_items = [i for i in items if not i.is_ai_related]

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📰 오늘의 IT/AI 뉴스 ({today})",
                "emoji": True,
            },
        },
        {"type": "divider"},
    ]

    if ai_items:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*🤖 AI 소식*"},
            }
        )
        for item in ai_items:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• *<{item.url}|{item.title}>*\n  {item.summary}",
                    },
                }
            )

    if it_items:
        if ai_items:
            blocks.append({"type": "divider"})
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*💻 IT 소식*"},
            }
        )
        for item in it_items:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"• *<{item.url}|{item.title}>*\n  {item.summary}",
                    },
                }
            )

    blocks.append({"type": "divider"})
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"총 {len(items)}개 | foundy-bot 자동 수집",
                }
            ],
        }
    )

    return blocks


def send_news(items: "list[NewsItem]") -> bool:
    """
    수집된 뉴스 항목을 Slack으로 전송합니다.

    Args:
        items: 전송할 뉴스 목록

    Returns:
        전송 성공 여부
    """
    webhook_url = os.environ.get(SLACK_WEBHOOK_ENV)
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return False

    if not items:
        logger.info("전송할 뉴스가 없습니다.")
        return True

    today = date.today().isoformat()
    blocks = _build_blocks(items, today)

    payload = {
        "text": f"📰 오늘의 IT/AI 뉴스 ({today})",  # 알림 텍스트 (fallback)
        "blocks": blocks,
    }

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        logger.info("Slack 전송 성공 (%d개 뉴스)", len(items))
        return True
    except requests.exceptions.HTTPError as exc:
        logger.error("Slack HTTP 오류: %s", exc)
        return False
    except requests.exceptions.RequestException as exc:
        logger.error("Slack 전송 실패: %s", exc)
        return False
