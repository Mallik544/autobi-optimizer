from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import re
import sqlparse


@dataclass
class QueryIssue:
    severity: str
    issue: str
    recommendation: str


class QueryAnalyzer:
    """Analyze SQL queries for common BI performance and maintainability issues."""

    def __init__(self) -> None:
        self.large_scan_keywords = ["FROM", "JOIN"]

    def analyze(self, query: str) -> Dict[str, Any]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        normalized = self._normalize(query)
        parsed = sqlparse.parse(query)
        if not parsed:
            raise ValueError("Unable to parse query.")

        issues: List[QueryIssue] = []

        if re.search(r"SELECT\s+\*", normalized, flags=re.IGNORECASE):
            issues.append(QueryIssue(
                severity="high",
                issue="Uses SELECT *",
                recommendation="Select only required columns to reduce scan cost and improve maintainability.",
            ))

        join_count = len(re.findall(r"\bJOIN\b", normalized, flags=re.IGNORECASE))
        on_count = len(re.findall(r"\bON\b", normalized, flags=re.IGNORECASE))
        if join_count > on_count:
            issues.append(QueryIssue(
                severity="high",
                issue="One or more JOIN clauses may be missing ON conditions",
                recommendation="Validate all joins and ensure each JOIN has an explicit ON condition.",
            ))

        if re.search(r"\bFROM\b", normalized, flags=re.IGNORECASE) and not re.search(
            r"\bWHERE\b", normalized, flags=re.IGNORECASE
        ):
            issues.append(QueryIssue(
                severity="medium",
                issue="No WHERE clause detected",
                recommendation="Consider adding filters to reduce full table scans when possible.",
            ))

        subquery_count = len(re.findall(r"\(\s*SELECT\b", normalized, flags=re.IGNORECASE))
        if subquery_count >= 2:
            issues.append(QueryIssue(
                severity="medium",
                issue="Multiple nested subqueries detected",
                recommendation="Review whether CTEs, staging tables, or pre-aggregation would improve readability and performance.",
            ))

        if len(re.findall(r"\bDISTINCT\b", normalized, flags=re.IGNORECASE)) >= 1:
            issues.append(QueryIssue(
                severity="low",
                issue="DISTINCT detected",
                recommendation="Confirm DISTINCT is necessary and not masking upstream duplication issues.",
            ))

        if len(re.findall(r"\bORDER\s+BY\b", normalized, flags=re.IGNORECASE)) >= 1 and not re.search(
            r"\bLIMIT\b|\bTOP\b", normalized, flags=re.IGNORECASE
        ):
            issues.append(QueryIssue(
                severity="low",
                issue="ORDER BY without LIMIT/TOP",
                recommendation="Consider whether sorting the full result set is necessary or if limiting rows would be more efficient.",
            ))

        recommendations = self._prioritized_recommendations(issues)

        return {
            "query": query,
            "normalized_query": normalized,
            "issue_count": len(issues),
            "issues": [asdict(issue) for issue in issues],
            "recommendations": recommendations,
            "complexity_score": self._complexity_score(join_count, subquery_count, len(issues)),
        }

    def _normalize(self, query: str) -> str:
        formatted = sqlparse.format(query, reindent=True, keyword_case="upper")
        return re.sub(r"\s+", " ", formatted).strip()

    def _complexity_score(self, join_count: int, subquery_count: int, issue_count: int) -> int:
        score = 10
        score += join_count * 5
        score += subquery_count * 7
        score += issue_count * 4
        return min(score, 100)

    def _prioritized_recommendations(self, issues: List[QueryIssue]) -> List[str]:
        seen = set()
        ordered: List[str] = []
        for issue in sorted(issues, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.severity]):
            if issue.recommendation not in seen:
                ordered.append(issue.recommendation)
                seen.add(issue.recommendation)

        if not ordered:
            ordered.append("No major anti-patterns detected. Validate indexes, partitions, and execution plan for final tuning.")
        return ordered
