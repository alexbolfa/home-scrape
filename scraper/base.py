from abc import ABC, abstractmethod

from playwright.async_api import Page

from scraper.models import Listing


class BaseScraper(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def url(self) -> str: ...

    @abstractmethod
    async def parse(self, page: Page) -> list[Listing]: ...
