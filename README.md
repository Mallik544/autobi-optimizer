# AutoBI Optimizer

AutoBI Optimizer is an open-source starter framework for AI-powered business intelligence optimization. It helps analytics teams detect query anti-patterns, surface data quality issues, track performance trends, and generate practical recommendations for improving enterprise BI workloads.

## Why this project matters

Modern BI environments often rely on manual tuning, ad hoc troubleshooting, and fragmented monitoring. This project provides a reusable foundation for building more autonomous analytics systems with:

- SQL query quality analysis
- Data quality profiling
- Performance trend analysis
- Recommendation generation for BI and data engineering teams
- Optional Streamlit interface for demos and review

## Core capabilities

### 1) Query optimization analysis
The query analysis engine inspects SQL and flags common anti-patterns such as:

- `SELECT *`
- joins without explicit `ON`
- missing `WHERE` clauses in large scans
- excessive nested subqueries
- repeated `ORDER BY` or `DISTINCT` usage concerns

It also generates practical recommendations.

### 2) Data quality profiling
The data quality engine computes:

- row and column counts
- null percentages
- duplicate row percentages
- uniqueness ratios
- outlier counts for numeric columns using IQR
- simple schema summaries

### 3) Performance monitoring
The performance module helps track execution-time history and identifies:

- regressions
- improving trends
- latency spikes
- average and percentile-like summaries

### 4) Recommendation engine
A rule-based + ML-assisted recommender proposes actions such as:

- avoid full scans
- reduce `SELECT *`
- improve filtering
- review indexing and partitioning
- inspect skew and duplicates
- validate schema drift

## Project structure

```text
autobi-optimizer/
├── ai_engine/
│   ├── __init__.py
│   └── recommendation_model.py
├── data/
│   └── sample_sales.csv
├── examples/
│   ├── performance_history.csv
│   └── sample_queries.sql
├── optimizer/
│   ├── __init__.py
│   ├── data_quality.py
│   ├── performance.py
│   └── query_optimizer.py
├── app.py
├── demo.py
├── requirements.txt
└── README.md
```

## Quick start

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# or
.venv\Scripts\activate      # Windows
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the command-line demo

```bash
python demo.py
```

### 4) Run the Streamlit app

```bash
streamlit run app.py
```

## Example usage

```python
from optimizer.query_optimizer import QueryAnalyzer
from optimizer.data_quality import DataQualityAnalyzer
from optimizer.performance import PerformanceAnalyzer

query = "SELECT * FROM sales"
qa = QueryAnalyzer()
result = qa.analyze(query)
print(result)
```

## Sample EB1A positioning

This project demonstrates a reusable open-source contribution in the area of AI-driven BI optimization. It addresses a real enterprise problem space by combining query analysis, data quality intelligence, and performance recommendations into a public, extensible framework that can be adopted by analytics engineers, BI developers, and enterprise data teams.

## Roadmap

- warehouse-specific SQL rules for Snowflake, BigQuery, Redshift, and Synapse
- historical learning from execution plans
- dashboard metadata ingestion
- anomaly detection on pipeline timing metrics
- API endpoints for CI/CD integration
- plugin system for BI platforms

## License

You can publish this under the MIT License if you want broad adoption.
