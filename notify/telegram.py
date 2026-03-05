import os

import httpx

from scraper.models import Listing

MAX_MESSAGE_LENGTH = 4096


def _format_listing(listing: Listing) -> str:
    parts = [f"<b>{listing.title}</b>"]
    parts.append(f"{listing.price}")
    if listing.address:
        parts.append(f"{listing.address}")
    details = []
    if listing.area:
        details.append(listing.area)
    if listing.bedrooms is not None:
        details.append(f"{listing.bedrooms} bed")
    if details:
        parts.append(" | ".join(details))
    parts.append(f'<a href="{listing.url}">View</a>')
    return "\n".join(parts)


def _build_messages(new_by_scraper: dict[str, list[Listing]]) -> list[str]:
    sections: list[str] = []
    for scraper_name, listings in new_by_scraper.items():
        header = f"<b>{scraper_name}</b> — {len(listings)} new\n"
        formatted = [_format_listing(l) for l in listings]
        sections.append(header + "\n\n".join(formatted))

    full_text = "\n\n---\n\n".join(sections)
    if len(full_text) <= MAX_MESSAGE_LENGTH:
        return [full_text]

    # Split into chunks per listing
    messages: list[str] = []
    current = ""
    for section in sections:
        for block in section.split("\n\n"):
            candidate = (current + "\n\n" + block).strip()
            if len(candidate) > MAX_MESSAGE_LENGTH:
                if current:
                    messages.append(current)
                current = block
            else:
                current = candidate
    if current:
        messages.append(current)
    return messages


async def send(new_by_scraper: dict[str, list[Listing]]) -> None:
    token = os.environ["TELEGRAM_KEY"]
    chat_id = os.environ["TELEGRAM_CHANNEL_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    messages = _build_messages(new_by_scraper)
    async with httpx.AsyncClient() as client:
        for text in messages:
            resp = await client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            })
            resp.raise_for_status()
