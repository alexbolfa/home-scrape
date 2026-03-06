from playwright.async_api import Page

from scraper.base import BaseScraper
from scraper.models import Listing


class RoofzScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "roofz"

    @property
    def url(self) -> str:
        return "https://roofz.eu/huur/woningen"

    async def _parse_cards(self, page: Page) -> list[dict]:
        return await page.evaluate("""() => {
            const cards = document.querySelectorAll('.offer-card.box-shadow');
            return Array.from(cards).map(c => {
                const content = c.querySelector('.offer-card__content');
                const title = c.querySelector('.offer-card__title');
                const text = c.querySelector('.offer-card__text');
                const details = c.querySelectorAll('.property__details--item');
                const children = Array.from(text?.children || []);
                const address = children.find(e => e.tagName === 'DIV' && !e.className);
                const price = children.find(e => e.tagName === 'B');
                return {
                    href: content?.getAttribute('href') || '',
                    title: title?.textContent?.trim() || '',
                    address: address?.textContent?.trim() || '',
                    price: price?.textContent?.trim() || '',
                    details: Array.from(details).map(d => d.textContent?.trim() || '')
                };
            });
        }""")

    async def parse(self, page: Page) -> list[Listing]:
        await page.wait_for_selector(".offer-card.box-shadow", timeout=15000)
        raw = await self._parse_cards(page)

        # Dismiss cookie wall if present
        cookie_btn = await page.query_selector('.cookie-wall button')
        if cookie_btn:
            await cookie_btn.click()
            await page.wait_for_timeout(500)

        # Handle pagination: click through remaining pages
        while True:
            next_btn = await page.query_selector(
                '.pagination-item button[aria-label="Go to next page"]:not([disabled])'
            )
            if not next_btn:
                break
            await next_btn.click()
            await page.wait_for_timeout(1000)
            await page.wait_for_selector(".offer-card.box-shadow", timeout=15000)
            raw.extend(await self._parse_cards(page))

        listings: list[Listing] = []
        for item in raw:
            href = item["href"]
            if not href:
                continue
            listing_id = href.rstrip("/").split("/")[-1]

            area = None
            bedrooms = None
            for detail in item["details"]:
                if "m²" in detail:
                    area = detail
                elif detail.isdigit():
                    bedrooms = int(detail)

            listings.append(Listing(
                id=listing_id,
                title=item["title"],
                price=item["price"],
                address=item["address"],
                url=f"https://roofz.eu{href}",
                area=area,
                bedrooms=bedrooms,
            ))

        return listings
