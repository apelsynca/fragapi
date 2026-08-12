from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CustomEmoji:
    emoji_id: str
    fallback: str

    @property
    def html(self) -> str:
        return f'<tg-emoji emoji-id="{self.emoji_id}">{self.fallback}</tg-emoji>'


FRAGMENT_ANIMATED = CustomEmoji(emoji_id="5179285789342697079", fallback="💠")
