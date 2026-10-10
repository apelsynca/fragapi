from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomEmoji:
    emoji_id: str
    fallback: str

    @property
    def html(self) -> str:
        return f'<tg-emoji emoji-id="{self.emoji_id}">{self.fallback}</tg-emoji>'


FRAGMENT_ANIMATED = CustomEmoji(emoji_id="5179285789342697079", fallback="💠")
GRAM = CustomEmoji(emoji_id="5296742257146241213", fallback="💎")

TELEGRAM_STAR_ANIMATED = CustomEmoji(emoji_id="5001452277609793720", fallback="⭐️")
GIFT_ANIMATED = CustomEmoji(emoji_id="5203996991054432397", fallback="🎁")

PLUS_ANIMATED = CustomEmoji(emoji_id="5397916757333654639", fallback="➕")
