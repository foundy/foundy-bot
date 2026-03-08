"""
foundy-bot 메인 진입점

매일 오전 9시(KST)에 GitHub Actions를 통해 실행됩니다.
IT/AI 뉴스를 수집하여 Slack으로 전송하고 히스토리를 관리합니다.
"""

import logging
import sys

from src.history_manager import add_to_history, is_duplicate, load_and_clean_history, save_history
from src.news_collector import collect_news
from src.slack_notifier import send_news

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 하루에 전송할 최대 뉴스 수
MAX_NEWS_ITEMS = 10


def main() -> None:
    """메인 실행 함수."""
    logger.info("foundy-bot 시작")

    # 1. 히스토리 로드 및 오래된 항목 정리
    history = load_and_clean_history()
    logger.info("히스토리 로드 완료 (%d일)", len(history))

    # 2. 뉴스 수집 (넉넉하게 수집 후 필터링)
    candidates = collect_news(max_items=MAX_NEWS_ITEMS * 2)
    logger.info("후보 뉴스 %d개 수집", len(candidates))

    # 3. 중복 필터링
    new_items = [item for item in candidates if not is_duplicate(item, history)]
    logger.info("중복 제거 후 %d개 (제거: %d개)", len(new_items), len(candidates) - len(new_items))

    # 4. 최대 전송 수로 제한
    items_to_send = new_items[:MAX_NEWS_ITEMS]

    if not items_to_send:
        logger.info("오늘 전송할 새 뉴스가 없습니다.")
        return

    # 5. Slack 전송
    success = send_news(items_to_send)
    if not success:
        logger.error("Slack 전송 실패. 히스토리를 업데이트하지 않습니다.")
        sys.exit(1)

    # 6. 히스토리 업데이트 및 저장
    updated_history = add_to_history(items_to_send, history)
    save_history(updated_history)
    logger.info("완료: %d개 뉴스 전송 및 히스토리 업데이트", len(items_to_send))


if __name__ == "__main__":
    main()
