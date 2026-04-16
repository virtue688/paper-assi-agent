from __future__ import annotations

from typing import Iterable

from agent.paper_agent import PaperAssistantAgent


class DailyMonitorScheduler:
    def __init__(self, agent: PaperAssistantAgent) -> None:
        self.agent = agent
        self.scheduler = None

    def start(self, keywords: Iterable[str], hour: int = 9, minute: int = 0) -> None:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
        except ImportError as exc:
            raise RuntimeError("APScheduler is not installed. Run `pip install -r requirements.txt`.") from exc
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.scheduler.add_job(
            self.run_once,
            "cron",
            hour=hour,
            minute=minute,
            args=[list(keywords)],
            id="daily_paper_monitor",
            replace_existing=True,
        )
        self.scheduler.start()

    def run_once(self, keywords: Iterable[str]):
        return self.agent.run({"intent": "daily_monitor", "keywords": list(keywords)})

    def stop(self) -> None:
        if self.scheduler:
            self.scheduler.shutdown()
