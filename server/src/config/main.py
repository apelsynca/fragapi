import os
import tomllib
from pathlib import Path

from .models import Settings
from .models.environment import Environment


def load_settings(config_path: Path, secrets_path: Path) -> Settings:
    config_data = {}
    if config_path.exists():
        with config_path.open("rb") as f:
            config_data = tomllib.load(f)

    secrets_data = {}
    if secrets_path.exists():
        with secrets_path.open("rb") as f:
            secrets_data = tomllib.load(f)
    else:
        # just create it for fun...
        secrets_path.touch()

    combined = config_data | secrets_data

    return Settings.model_validate(combined)


env = Environment(os.getenv("FRAG_ENV", Environment.development))

config_path = Path("settings.toml")

default_secrets_file = (
    ".test-secrets.toml" if env == Environment.testing else ".secrets.toml"
)
secrets_path = Path(os.getenv("SECRETS_PATH", default_secrets_file))

settings = load_settings(config_path, secrets_path)
