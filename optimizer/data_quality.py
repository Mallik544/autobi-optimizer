from __future__ import annotations

from typing import Dict, Any
import pandas as pd


class DataQualityAnalyzer:
    """Profile a dataset and surface data quality issues relevant to BI workloads."""

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or df.empty:
            raise ValueError("DataFrame cannot be empty.")

        row_count = len(df)
        column_count = len(df.columns)
        duplicate_rows = int(df.duplicated().sum())
        duplicate_pct = round((duplicate_rows / row_count) * 100, 2)

        column_metrics = {}
        for col in df.columns:
            series = df[col]
            null_count = int(series.isna().sum())
            null_pct = round((null_count / row_count) * 100, 2)
            unique_count = int(series.nunique(dropna=True))
            uniqueness_ratio = round((unique_count / row_count) * 100, 2)

            metric = {
                "dtype": str(series.dtype),
                "null_count": null_count,
                "null_pct": null_pct,
                "unique_count": unique_count,
                "uniqueness_ratio_pct": uniqueness_ratio,
            }

            if pd.api.types.is_numeric_dtype(series):
                clean = series.dropna()
                if not clean.empty:
                    q1 = clean.quantile(0.25)
                    q3 = clean.quantile(0.75)
                    iqr = q3 - q1
                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr
                    outliers = int(((clean < lower) | (clean > upper)).sum())
                else:
                    outliers = 0
                metric["outlier_count"] = outliers

            column_metrics[col] = metric

        issues = self._generate_issues(column_metrics, duplicate_pct)
        score = self._quality_score(column_metrics, duplicate_pct)

        return {
            "row_count": row_count,
            "column_count": column_count,
            "duplicate_rows": duplicate_rows,
            "duplicate_pct": duplicate_pct,
            "column_metrics": column_metrics,
            "issues": issues,
            "quality_score": score,
        }

    def _generate_issues(self, column_metrics: Dict[str, Any], duplicate_pct: float) -> list[str]:
        issues = []
        if duplicate_pct > 5:
            issues.append(f"Duplicate row percentage is high at {duplicate_pct}%.")

        for col, metric in column_metrics.items():
            if metric["null_pct"] > 20:
                issues.append(f"Column '{col}' has a high null percentage ({metric['null_pct']}%).")
            if metric["uniqueness_ratio_pct"] < 1 and metric["dtype"] != "object":
                issues.append(f"Column '{col}' has very low uniqueness and may need validation.")
            if metric.get("outlier_count", 0) > 0:
                issues.append(f"Column '{col}' contains {metric['outlier_count']} potential outliers.")

        if not issues:
            issues.append("No critical data quality issues detected in the sample.")
        return issues

    def _quality_score(self, column_metrics: Dict[str, Any], duplicate_pct: float) -> int:
        score = 100
        score -= min(int(duplicate_pct * 2), 25)
        for metric in column_metrics.values():
            score -= min(int(metric["null_pct"] / 5), 10)
            score -= min(metric.get("outlier_count", 0), 10)
        return max(score, 0)
