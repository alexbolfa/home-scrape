import asyncio

from dotenv import load_dotenv
from playwright.async_api import async_playwright

from notify import macos, telegram
from scraper.base import BaseScraper
from scraper.models import Listing
from scraper.roofz import RoofzScraper
from state import filter_new, load_seen, save_seen

SCRAPERS: list[BaseScraper] = [RoofzScraper()]


async def run() -> None:
    load_dotenv()
    seen = load_seen()
    new_by_scraper: dict[str, list[Listing]] = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        for scraper in SCRAPERS:
            page = await browser.new_page()
            try:
                await page.goto(scraper.url, wait_until="networkidle")
                listings = await scraper.parse(page)
                new = filter_new(scraper.name, listings, seen)
                if new:
                    new_by_scraper[scraper.name] = new
                # Update seen with all current listing IDs
                seen[scraper.name] = list({
                    *seen.get(scraper.name, []),
                    *(l.id for l in listings),
                })
                print(f"[{scraper.name}] {len(listings)} total, {len(new)} new")
            except Exception as e:
                print(f"[{scraper.name}] error: {e}")
            finally:
                await page.close()

        await browser.close()

    save_seen(seen)

    if new_by_scraper:
        total = sum(len(v) for v in new_by_scraper.values())
        try:
            await telegram.send(new_by_scraper)
            print(f"Telegram: sent {total} new listings")
        except Exception as e:
            print(f"Telegram error: {e}")
        macos.notify("Home Scraper", f"{total} new listings found")
    else:
        print("No new listings")


if __name__ == "__main__":
    asyncio.run(run())
