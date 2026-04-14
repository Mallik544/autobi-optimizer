from __future__ import annotations

from typing import Dict, Any, List
import pandas as pd
from sklearn.tree import DecisionTreeClassifier


class RecommendationEngine:
    """A lightweight ML-assisted recommendation engine.

    This starter version uses a tiny synthetic training set to classify workload risk
    and combine that result with rule-based recommendations.
    """

    def __init__(self) -> None:
        self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
        self._train_synthetic_model()

    def _train_synthetic_model(self) -> None:
        training = pd.DataFrame(
            [
                [1, 0, 0, 90, 0],
                [3, 1, 10, 75, 1],
                [4, 1, 25, 55, 1],
                [6, 2, 35, 40, 2],
                [2, 0, 5, 95, 0],
                [5, 3, 30, 35, 2],
            ],
            columns=["query_issues", "degrading_flag", "duplicate_pct", "quality_score", "risk_label"],
        )
        X = training[["query_issues", "degrading_flag", "duplicate_pct", "quality_score"]]
        y = training["risk_label"]
        self.model.fit(X, y)

    def recommend(
        self,
        query_result: Dict[str, Any],
        quality_result: Dict[str, Any],
        performance_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        degrading_flag = 1 if performance_result.get("trend") == "degrading" else 0
        features = pd.DataFrame(
            [[
                query_result.get("issue_count", 0),
                degrading_flag,
                quality_result.get("duplicate_pct", 0),
                quality_result.get("quality_score", 100),
            ]],
            columns=["query_issues", "degrading_flag", "duplicate_pct", "quality_score"],
        )

        risk_label = int(self.model.predict(features)[0])
        risk_map = {0: "low", 1: "medium", 2: "high"}

        actions: List[str] = []
        actions.extend(query_result.get("recommendations", []))
        actions.extend(performance_result.get("recommendations", []))

        for issue in quality_result.get("issues", []):
            if "null" in issue.lower() or "duplicate" in issue.lower() or "outlier" in issue.lower():
                actions.append(f"Data quality follow-up: {issue}")

        deduped_actions = []
        seen = set()
        for action in actions:
            if action not in seen:
                deduped_actions.append(action)
                seen.add(action)

        return {
            "risk_level": risk_map[risk_label],
            "recommended_actions": deduped_actions[:10],
            "summary": self._summary(risk_map[risk_label], query_result, quality_result, performance_result),
        }

    def _summary(
        self,
        risk_level: str,
        query_result: Dict[str, Any],
        quality_result: Dict[str, Any],
        performance_result: Dict[str, Any],
    ) -> str:
        return (
            f"Overall workload risk is {risk_level}. "
            f"Detected {query_result.get('issue_count', 0)} query issue(s), "
            f"quality score {quality_result.get('quality_score', 0)}, and "
            f"performance trend '{performance_result.get('trend', 'unknown')}'."
        )
