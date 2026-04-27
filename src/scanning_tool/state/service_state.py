from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from re import Pattern

import ollama

from scanning_tool.domain.ore import RockData, RockDataCollection


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scanning_tool.domain.common import RegionDepositTables
def _default_region_deposit_tables() -> RegionDepositTables:
    return {}


@dataclass
class OllamaClientState:
    client: ollama.Client | None = None
    client_host: str = ""
    server_process: subprocess.Popen[bytes] | None = field(default=None, repr=False)


@dataclass
class CodePatterns:
    code_re: Pattern[str] = field(
        default_factory=lambda: re.compile(
            r"(?:[A-Za-z]?-?\d[\d,\.]{1,10}|\d{2,10})",
            re.IGNORECASE,
        ),
    )
    host_scheme_re: Pattern[str] = field(
        default_factory=lambda: re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://"),
    )


@dataclass
class RockDataCache:
    rock_data: RockData = field(default_factory=RockDataCollection)
    deposit_tables: RegionDepositTables = field(
        default_factory=_default_region_deposit_tables,
    )


@dataclass
class ServiceState:
    ollama_state: OllamaClientState = field(default_factory=OllamaClientState)
    patterns: CodePatterns = field(default_factory=CodePatterns)
    rocks: RockDataCache = field(default_factory=RockDataCache)

    # Convenience accessors for migration — keeps existing attribute paths working
    @property
    def ollama_client(self) -> ollama.Client | None:
        return self.ollama_state.client

    @ollama_client.setter
    def ollama_client(self, value: ollama.Client | None) -> None:
        self.ollama_state.client = value

    @property
    def ollama_client_host(self) -> str:
        return self.ollama_state.client_host

    @ollama_client_host.setter
    def ollama_client_host(self, value: str) -> None:
        self.ollama_state.client_host = value

    @property
    def ollama_server_process(self) -> subprocess.Popen[bytes] | None:
        return self.ollama_state.server_process

    @ollama_server_process.setter
    def ollama_server_process(self, value: subprocess.Popen[bytes] | None) -> None:
        self.ollama_state.server_process = value

    @property
    def code_re(self) -> Pattern[str]:
        return self.patterns.code_re

    @property
    def host_scheme_re(self) -> Pattern[str]:
        return self.patterns.host_scheme_re
