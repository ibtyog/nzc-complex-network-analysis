"""ETL data pipeline modules for the medallion architecture (Bronze -> Silver -> Gold)."""

from web_edu_complex_network.etl.silver import run_silver_pipeline

__all__ = ["run_silver_pipeline"]
