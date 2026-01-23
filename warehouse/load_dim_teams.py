from warehouse.snowflake_loader import load_parquet_to_table

def load_dim_teams():
    load_parquet_to_table(
        parquet_path="data/raw/teams.parquet",
        table_name="DIM_TEAMS",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS DIM_TEAMS (
            team_id INTEGER,
            team_name STRING,
            city STRING,
            abbreviation STRING,
            nickname STRING,
            year_founded INTEGER,
            ingested_at TIMESTAMP
        )
        """
    )

if __name__ == "__main__":
    load_dim_teams()
