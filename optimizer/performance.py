from __future__ import annotations

from typing import Dict, Any, List
import statistics


class PerformanceAnalyzer:
    """Analyze query or pipeline runtime history to identify regressions and trends."""

    def analyze(self, durations_ms: List[float]) -> Dict[str, Any]:
        if not durations_ms:
            raise ValueError("durations_ms cannot be empty.")

        if any(d < 0 for d in durations_ms):
            raise ValueError("durations_ms cannot contain negative values.")

        avg = round(statistics.mean(durations_ms), 2)
        median = round(statistics.median(durations_ms), 2)
        best = round(min(durations_ms), 2)
        worst = round(max(durations_ms), 2)
        latest = round(durations_ms[-1], 2)

        trend = self._trend(durations_ms)
        regression_pct = self._regression_pct(durations_ms)
        recommendations = self._recommendations(avg, latest, trend, regression_pct)

        return {
            "count": len(durations_ms),
            "average_ms": avg,
            "median_ms": median,
            "best_ms": best,
            "worst_ms": worst,
            "latest_ms": latest,
            "trend": trend,
            "regression_pct": regression_pct,
            "recommendations": recommendations,
        }

    def _trend(self, durations_ms: List[float]) -> str:
        if len(durations_ms) < 2:
            return "insufficient data"

        first_half = statistics.mean(durations_ms[: max(1, len(durations_ms)//2)])
        second_half = statistics.mean(durations_ms[max(1, len(durations_ms)//2):])

        if second_half > first_half * 1.1:
            return "degrading"
        if second_half < first_half * 0.9:
            return "improving"
        return "stable"

    def _regression_pct(self, durations_ms: List[float]) -> float:
        baseline = min(durations_ms)
        latest = durations_ms[-1]
        if baseline == 0:
            return 0.0
        return round(((latest - baseline) / baseline) * 100, 2)

    def _recommendations(self, avg: float, latest: float, trend: str, regression_pct: float) -> List[str]:
        recs = []
        if trend == "degrading":
            recs.append("Runtime trend is degrading. Review recent query changes, data volume growth, and warehouse scaling behavior.")
        if regression_pct > 30:
            recs.append("Latest runtime shows material regression. Inspect execution plan and partition pruning opportunities.")
        if latest > avg * 1.25:
            recs.append("Latest run is significantly above average. Check for data skew, concurrency, or resource contention.")
        if not recs:
            recs.append("Performance appears stable. Continue monitoring and validate with workload-specific benchmarks.")
        return recs
