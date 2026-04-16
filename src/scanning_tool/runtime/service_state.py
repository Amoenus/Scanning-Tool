from dataclasses import dataclass, field
from typing import Callable, Optional, Pattern
import re
import subprocess

import ollama

from scanning_tool.domain.models import RegionDepositTables, RockData

@dataclass
class ServiceState:
    ollama_client: Optional[ollama.Client] = None
    ollama_client_host: str = ""
    ollama_server_process: Optional[subprocess.Popen] = field(default=None, repr=False)
    code_re: Pattern[str] = field(default_factory=lambda: re.compile(
        r"(?:[A-Za-z]?-?\d[\d,\.]{1,10}|\d{2,10})",
        re.IGNORECASE,
    ))
    host_scheme_re: Pattern[str] = field(default_factory=lambda: re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://"))
    rock_data: RockData = field(default_factory=dict)
    deposit_tables: RegionDepositTables = field(default_factory=dict)
    gui_status_callback: Optional[Callable[[str], None]] = None
