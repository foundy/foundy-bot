"""
뉴스 수집 모듈

RSS 피드에서 IT/AI 뉴스를 수집하고 OpenAI API로 요약합니다.
AI 관련 뉴스에 더 높은 우선순위를 부여합니다.
"""

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import feedparser
from openai import OpenAI

logger = logging.getLogger(__name__)

# AI 관련 키워드 (우선순위 판단에 사용)
AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "large language model", "gpt", "chatgpt", "claude", "gemini",
    "openai", "anthropic", "google deepmind", "meta ai",
    "neural network", "transformer", "generative ai", "gen ai",
    "diffusion model", "stable diffusion", "midjourney",
    "autonomous", "robot", "자율", "인공지능", "머신러닝", "딥러닝",
    "rag", "fine-tuning", "fine tuning", "prompt engineering",
    "multimodal", "text-to-image", "text to image",
]

# 뉴스 소스 목록
# is_ai_source=True 인 소스는 AI 관련 가중치를 기본으로 부여
NEWS_SOURCES = [
    # AI 전용 소스 (높은 우선순위)
    {
        "url": "https://feeds.feedburner.com/venturebeat/SZYF",
        "name": "VentureBeat AI",
        "is_ai_source": True,
    },
    {
        "url": "https://www.technologyreview.com/feed/",
        "name": "MIT Technology Review",
        "is_ai_source": True,
    },
    {
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "name": "TechCrunch AI",
        "is_ai_source": True,
    },
    # 일반 IT 소스
    {
        "url": "https://techcrunch.com/feed/",
        "name": "TechCrunch",
        "is_ai_source": False,
    },
    {
        "url": "https://www.theverge.com/rss/index.xml",
        "name": "The Verge",
        "is_ai_source": False,
    },
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "name": "Ars Technica",
        "is_ai_source": False,
    },
    {
        "url": "https://hnrss.org/frontpage",
        "name": "Hacker News",
        "is_ai_source": False,
    },
]

# 요약 최대 길이 (글자 수)
SUMMARY_MAX_LENGTH = 200

# 소스당 최대 수집 기사 수
MAX_ITEMS_PER_SOURCE = 5


@dataclass
class NewsItem:
    """개별 뉴스 항목을 나타내는 데이터 클래스."""

    title: str
    url: str
    source: str
    summary: str = ""
    is_ai_related: bool = False
    priority: int = 0  # 높을수록 먼저 표시
    raw_description: str = field(default="", repr=False)


def _is_ai_related(text: str) -> bool:
    """텍스트가 AI 관련 내용인지 키워드 기반으로 판단합니다."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in AI_KEYWORDS)


def _clean_html(text: str) -> str:
    """HTML 태그를 제거하고 텍스트를 정리합니다."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _summarize_with_openai(title: str, description: str, client: OpenAI) -> Optional[str]:
    """OpenAI API를 사용하여 뉴스를 200자 이내로 요약합니다."""
    prompt = (
        f"다음 뉴스를 한국어로 200자 이내로 핵심만 요약해주세요. "
        f"마침표로 끝내주세요.\n\n"
        f"제목: {title}\n내용: {description[:500]}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        # 200자 초과 시 자르기
        if len(summary) > SUMMARY_MAX_LENGTH:
            summary = summary[:SUMMARY_MAX_LENGTH - 1] + "…"
        return summary
    except Exception as exc:
        logger.warning("OpenAI 요약 실패: %s", exc)
        return None


def _fallback_summary(description: str) -> str:
    """OpenAI 실패 시 RSS description을 잘라 사용합니다."""
    cleaned = _clean_html(description)
    if len(cleaned) > SUMMARY_MAX_LENGTH:
        return cleaned[:SUMMARY_MAX_LENGTH - 1] + "…"
    return cleaned


def _fetch_from_source(source: dict) -> list[NewsItem]:
    """단일 RSS 소스에서 뉴스를 가져옵니다."""
    items: list[NewsItem] = []
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            logger.warning("피드 파싱 오류: %s", source["name"])
            return items

        for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
            title = _clean_html(getattr(entry, "title", ""))
            url = getattr(entry, "link", "")
            description = _clean_html(
                getattr(entry, "summary", "") or getattr(entry, "description", "")
            )

            if not title or not url:
                continue

            combined_text = f"{title} {description}"
            is_ai = source["is_ai_source"] or _is_ai_related(combined_text)
            priority = 10 if source["is_ai_source"] else (5 if is_ai else 0)

            items.append(
                NewsItem(
                    title=title,
                    url=url,
                    source=source["name"],
                    is_ai_related=is_ai,
                    priority=priority,
                    raw_description=description,
                )
            )
    except Exception as exc:
        logger.error("소스 '%s' 수집 오류: %s", source["name"], exc)
    return items


def collect_news(max_items: int = 10) -> list[NewsItem]:
    """
    모든 소스에서 뉴스를 수집하고, AI 관련 뉴스를 상위에 정렬하여 반환합니다.

    Args:
        max_items: 반환할 최대 뉴스 수

    Returns:
        우선순위 순으로 정렬된 NewsItem 목록
    """
    all_items: list[NewsItem] = []

    for source in NEWS_SOURCES:
        fetched = _fetch_from_source(source)
        logger.info("'%s'에서 %d개 수집", source["name"], len(fetched))
        all_items.extend(fetched)

    # 중복 URL 제거 (먼저 나온 것 우선)
    seen_urls: set[str] = set()
    unique_items: list[NewsItem] = []
    for item in all_items:
        if item.url not in seen_urls:
            seen_urls.add(item.url)
            unique_items.append(item)

    # AI 관련 → 일반 순으로 정렬 (priority 높은 것 먼저)
    unique_items.sort(key=lambda x: x.priority, reverse=True)

    # OpenAI 클라이언트를 한 번만 생성 (API 키 없으면 fallback 사용)
    openai_client: Optional[OpenAI] = None
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        openai_client = OpenAI(api_key=api_key)
    else:
        logger.warning("OPENAI_API_KEY가 설정되지 않았습니다. RSS description을 요약으로 사용합니다.")

    # 요약 생성
    selected = unique_items[:max_items]
    for item in selected:
        summary = _summarize_with_openai(item.title, item.raw_description, openai_client) if openai_client else None
        if summary:
            item.summary = summary
        else:
            item.summary = _fallback_summary(item.raw_description) or item.title

    logger.info("총 %d개 뉴스 수집 완료", len(selected))
    return selected
