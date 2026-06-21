import yaml
from pathlib import Path
from pydantic import BaseModel, field_validator, HttpUrl


class Artist(BaseModel):
    name: str
    url: HttpUrl


class Schedule(BaseModel):
    interval_hours: int = 24
    run_on_start: bool = True


class Output(BaseModel):
    format: str = "{artist}/{album}/{title}.{output-ext}"
    audio_format: str = "mp3"
    bitrate: str = "320k"


class Config(BaseModel):
    download_dir: Path
    artists: list[Artist]
    schedule: Schedule = Schedule()
    output: Output = Output()

    @field_validator("download_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str) -> Path:
        return Path(v).expanduser().resolve()


def load_config(path: Path = Path("config.yaml")) -> Config:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return Config(**raw)
