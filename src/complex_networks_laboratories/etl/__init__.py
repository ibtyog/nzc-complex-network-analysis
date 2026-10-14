"""ETL data pipeline modules for the medallion architecture (Bronze -> Silver -> Gold)."""

from complex_networks_laboratories.etl.silver import run_silver_pipeline

__all__ = ["run_silver_pipeline"]
