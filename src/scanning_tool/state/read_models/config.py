from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigReadModel:
    """Read model for the Configuration concern."""

    # Placeholders, will be expanded as needed
    auto_alignment: bool = True
