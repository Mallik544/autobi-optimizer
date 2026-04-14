from __future__ import annotations

from io import StringIO
from pathlib import Path
import pandas as pd
import streamlit as st

from optimizer.query_optimizer import QueryAnalyzer
from optimizer.data_quality import DataQualityAnalyzer
from optimizer.performance import PerformanceAnalyzer
from ai_engine.recommendation_model import RecommendationEngine


st.set_page_config(page_title="AutoBI Optimizer", layout="wide")
st.title("AutoBI Optimizer")
st.caption("AI-powered BI performance, data quality, and recommendation starter framework")

query_analyzer = QueryAnalyzer()
quality_analyzer = DataQualityAnalyzer()
performance_analyzer = PerformanceAnalyzer()
recommender = RecommendationEngine()

base_dir = Path(__file__).parent

with st.sidebar:
    st.header("Inputs")
    sample_query = "SELECT * FROM sales ORDER BY region"
    query_text = st.text_area("SQL Query", value=sample_query, height=160)

    uploaded_csv = st.file_uploader("Upload CSV for data quality analysis", type=["csv"])
    perf_text = st.text_area(
        "Performance history (comma-separated ms)",
        value="230,240,250,265,280,305",
        height=80,
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("Query Analysis")
    try:
        query_result = query_analyzer.analyze(query_text)
        st.json(query_result)
    except Exception as exc:
        st.error(f"Query analysis failed: {exc}")
        query_result = {"issue_count": 0, "recommendations": []}

    st.subheader("Data Quality")
    try:
        if uploaded_csv is not None:
            df = pd.read_csv(uploaded_csv)
        else:
            df = pd.read_csv(base_dir / "data" / "sample_sales.csv")
        quality_result = quality_analyzer.analyze(df)
        st.json(quality_result)
        st.dataframe(df.head(20), use_container_width=True)
    except Exception as exc:
        st.error(f"Data quality analysis failed: {exc}")
        quality_result = {"quality_score": 100, "duplicate_pct": 0, "issues": []}

with col2:
    st.subheader("Performance")
    try:
        durations = [float(x.strip()) for x in perf_text.split(",") if x.strip()]
        performance_result = performance_analyzer.analyze(durations)
        st.json(performance_result)
    except Exception as exc:
        st.error(f"Performance analysis failed: {exc}")
        performance_result = {"trend": "unknown", "recommendations": []}

    st.subheader("Recommendations")
    try:
        recs = recommender.recommend(query_result, quality_result, performance_result)
        st.success(recs["summary"])
        for idx, action in enumerate(recs["recommended_actions"], start=1):
            st.write(f"{idx}. {action}")
    except Exception as exc:
        st.error(f"Recommendation generation failed: {exc}")
