"""
히스토리 관리 모듈

data/news_history.md 파일을 사용하여:
- 이미 전송된 뉴스의 중복 여부를 확인합니다.
- 새 뉴스를 기록에 추가합니다.
- 10일 이상 된 기록을 자동으로 삭제합니다.
"""

import logging
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.news_collector import NewsItem

logger = logging.getLogger(__name__)

HISTORY_FILE = Path(__file__).parent.parent / "data" / "news_history.md"
HISTORY_RETENTION_DAYS = 10


def _normalize_title(title: str) -> str:
    """제목을 정규화하여 비교에 사용합니다 (소문자, 특수문자 제거)."""
    return re.sub(r"[^a-z0-9가-힣]", "", title.lower())


def _parse_history() -> dict[str, list[dict[str, str]]]:
    """
    news_history.md를 파싱하여 {날짜: [{title, url, summary}, ...]} 형태로 반환합니다.
    """
    if not HISTORY_FILE.exists():
        return {}

    content = HISTORY_FILE.read_text(encoding="utf-8")
    result: dict[str, list[dict[str, str]]] = {}
    current_date: str = ""

    for line in content.splitlines():
        # "## 2025-01-15" 형식의 날짜 섹션 감지
        date_match = re.match(r"^## (\d{4}-\d{2}-\d{2})\s*$", line)
        if date_match:
            current_date = date_match.group(1)
            result[current_date] = []
            continue

        # "- [제목](URL) — 요약" 형식의 항목 감지
        if current_date and line.startswith("- ["):
            item_match = re.match(
                r"^- \[(.+?)\]\((.+?)\)(?:\s+—\s+(.*))?$", line
            )
            if item_match:
                result[current_date].append(
                    {
                        "title": item_match.group(1),
                        "url": item_match.group(2),
                        "summary": item_match.group(3) or "",
                    }
                )

    return result


def _write_history(history: dict[str, list[dict[str, str]]]) -> None:
    """히스토리 딕셔너리를 news_history.md 파일로 저장합니다."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# 뉴스 히스토리\n\n"]
    # 날짜 내림차순 정렬
    for date_str in sorted(history.keys(), reverse=True):
        lines.append(f"## {date_str}\n\n")
        for item in history[date_str]:
            summary_part = f" — {item['summary']}" if item.get("summary") else ""
            lines.append(f"- [{item['title']}]({item['url']}){summary_part}\n")
        lines.append("\n")

    HISTORY_FILE.write_text("".join(lines), encoding="utf-8")


def cleanup_old_entries(history: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    """10일 이상 된 히스토리 항목을 삭제하고 정리된 딕셔너리를 반환합니다."""
    cutoff = date.today() - timedelta(days=HISTORY_RETENTION_DAYS)
    cleaned = {
        date_str: items
        for date_str, items in history.items()
        if datetime.strptime(date_str, "%Y-%m-%d").date() > cutoff
    }
    removed = len(history) - len(cleaned)
    if removed > 0:
        logger.info("오래된 히스토리 %d개 섹션 삭제", removed)
    return cleaned


def is_duplicate(item: "NewsItem", history: dict[str, list[dict[str, str]]]) -> bool:
    """
    뉴스 항목이 히스토리에 이미 존재하는지 확인합니다.

    URL 완전 일치 또는 정규화된 제목 일치 시 중복으로 판단합니다.
    """
    normalized_title = _normalize_title(item.title)

    for items in history.values():
        for entry in items:
            if entry["url"] == item.url:
                return True
            if _normalize_title(entry["title"]) == normalized_title:
                return True
    return False


def add_to_history(
    items: list["NewsItem"],
    history: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    """
    전송된 뉴스 항목을 오늘 날짜로 히스토리에 추가합니다.

    Args:
        items: 전송된 뉴스 목록
        history: 현재 히스토리 딕셔너리

    Returns:
        업데이트된 히스토리 딕셔너리
    """
    today = date.today().isoformat()
    if today not in history:
        history[today] = []

    for item in items:
        history[today].append(
            {
                "title": item.title,
                "url": item.url,
                "summary": item.summary,
            }
        )
        logger.debug("히스토리에 추가: %s", item.title)

    return history


def load_and_clean_history() -> dict[str, list[dict[str, str]]]:
    """히스토리를 로드하고 오래된 항목을 정리하여 반환합니다."""
    history = _parse_history()
    history = cleanup_old_entries(history)
    return history


def save_history(history: dict[str, list[dict[str, str]]]) -> None:
    """히스토리를 파일에 저장합니다."""
    _write_history(history)
    logger.info("히스토리 저장 완료: %s", HISTORY_FILE)
