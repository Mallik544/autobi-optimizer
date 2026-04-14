from __future__ import annotations

from pathlib import Path
import pandas as pd

from optimizer.query_optimizer import QueryAnalyzer
from optimizer.data_quality import DataQualityAnalyzer
from optimizer.performance import PerformanceAnalyzer
from ai_engine.recommendation_model import RecommendationEngine


BASE_DIR = Path(__file__).parent


def main() -> None:
    query = "SELECT * FROM sales ORDER BY region"
    df = pd.read_csv(BASE_DIR / "data" / "sample_sales.csv")
    perf = pd.read_csv(BASE_DIR / "examples" / "performance_history.csv")

    query_analyzer = QueryAnalyzer()
    quality_analyzer = DataQualityAnalyzer()
    perf_analyzer = PerformanceAnalyzer()
    recommender = RecommendationEngine()

    query_result = query_analyzer.analyze(query)
    quality_result = quality_analyzer.analyze(df)
    performance_result = perf_analyzer.analyze(perf["duration_ms"].tolist())
    recommendations = recommender.recommend(query_result, quality_result, performance_result)

    print("=== Query Analysis ===")
    print(query_result)
    print("\n=== Data Quality Analysis ===")
    print(quality_result)
    print("\n=== Performance Analysis ===")
    print(performance_result)
    print("\n=== Recommendation Engine ===")
    print(recommendations)


if __name__ == "__main__":
    main()
