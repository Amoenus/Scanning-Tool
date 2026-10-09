from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OreProperties:
    density: float
    value: int


@dataclass(frozen=True)
class OreSample:
    density: float
    spectral_signature: str
    mass: float


@dataclass(frozen=True)
class OreAnalysisResult:
    ore_type: str
    confidence: float
    is_valuable: bool
    estimated_value: float
    density_match_error: float


class OreAnalyzer:
    MIN_VALUE_FOR_VALUABLE: int = 120
    MIN_CONFIDENCE_FOR_VALUABLE: float = 0.7

    def __init__(self) -> None:
        self.known_ores: dict[str, OreProperties] = {
            "quantanium": OreProperties(density=2.7, value=150),
            "bexalite": OreProperties(density=3.2, value=200),
            "tanite": OreProperties(density=2.1, value=100),
            "aranium": OreProperties(density=4.1, value=300),
        }

    def analyze_ore_sample(self, sample_data: OreSample) -> OreAnalysisResult:
        """Identify the closest known ore type for a scanned sample and score the match.

        Compares the sample density against all known ores, picks the closest match,
        and computes a confidence score and estimated value.

        Args:
            sample_data: Density, spectral signature, and mass of the scanned deposit.

        Returns:
            An OreAnalysisResult with ore type, confidence, value estimate, and match error.

        """
        best_match, min_density_diff = self._find_closest_match(sample_data.density)
        matched = self.known_ores[best_match]

        confidence = self._calculate_confidence(min_density_diff, matched.density, sample_data.density)
        is_valuable = self._is_sample_valuable(matched.value, confidence)

        return OreAnalysisResult(
            ore_type=best_match,
            confidence=round(confidence, 2),
            is_valuable=is_valuable,
            estimated_value=matched.value * sample_data.mass * confidence,
            density_match_error=round(min_density_diff, 3),
        )

    def _find_closest_match(self, sample_density: float) -> tuple[str, float]:
        best_match: str | None = None
        min_density_diff = float("inf")

        for ore_type, properties in self.known_ores.items():
            density_diff = abs(sample_density - properties.density)
            if density_diff < min_density_diff:
                min_density_diff = density_diff
                best_match = ore_type

        if best_match is None:
            msg = "No known ores to match against."
            raise ValueError(msg)

        return best_match, min_density_diff

    def _calculate_confidence(self, min_density_diff: float, matched_density: float, sample_density: float) -> float:
        return max(
            0.0,
            1.0 - (min_density_diff / max(matched_density, sample_density)),
        )

    def _is_sample_valuable(self, matched_value: int, confidence: float) -> bool:
        return matched_value > self.MIN_VALUE_FOR_VALUABLE and confidence > self.MIN_CONFIDENCE_FOR_VALUABLE
