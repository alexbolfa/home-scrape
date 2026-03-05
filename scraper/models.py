from dataclasses import dataclass


@dataclass
class Listing:
    id: str
    title: str
    price: str
    address: str
    url: str
    area: str | None = None
    bedrooms: int | None = None
