from dataclasses import dataclass

@dataclass(frozen=True)
class CountryTemplate:
    key: str
    name: str
    emoji: str
    economy: int
    industry: int
    population: int
    power: int
    territory: int

COUNTRIES = [
    CountryTemplate("ireland", "ایرلند", "🇮🇪", 85, 70, 5_300_000, 90, 4),
    CountryTemplate("france", "فرانسه", "🇫🇷", 260, 230, 68_000_000, 320, 22),
    CountryTemplate("germany", "آلمان", "🇩🇪", 280, 270, 84_000_000, 350, 20),
    CountryTemplate("italy", "ایتالیا", "🇮🇹", 190, 170, 59_000_000, 230, 18),
    CountryTemplate("spain", "اسپانیا", "🇪🇸", 180, 150, 48_000_000, 190, 18),
    CountryTemplate("japan", "ژاپن", "🇯🇵", 250, 240, 124_000_000, 300, 24),
    CountryTemplate("turkey", "ترکیه", "🇹🇷", 175, 145, 86_000_000, 210, 18),
    CountryTemplate("iran", "ایران", "🇮🇷", 160, 125, 89_000_000, 205, 20),
    CountryTemplate("egypt", "مصر", "🇪🇬", 120, 90, 114_000_000, 145, 16),
    CountryTemplate("brazil", "برزیل", "🇧🇷", 210, 180, 216_000_000, 220, 70),
    CountryTemplate("canada", "کانادا", "🇨🇦", 230, 210, 41_000_000, 210, 60),
    CountryTemplate("india", "هند", "🇮🇳", 300, 220, 1_440_000_000, 330, 65),
]

COUNTRY_BY_KEY = {c.key: c for c in COUNTRIES}
