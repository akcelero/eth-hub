from __future__ import annotations

from pydantic import Field

from eth_hub.base_key import BaseKey


class AwsKey(BaseKey):
    aliases: list[str] = Field(default_factory=list)
