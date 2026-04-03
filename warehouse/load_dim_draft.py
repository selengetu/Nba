from warehouse.snowflake_loader import load_parquet_to_table


def load_draft():
    load_parquet_to_table(
        parquet_path="data/raw/draft.parquet",
        table_name="RAW.DIM_DRAFT",
        create_table_sql="""
        CREATE TABLE IF NOT EXISTS RAW.DIM_DRAFT (
            player_id INTEGER,
            player_name VARCHAR,
            draft_year VARCHAR,
            round_number INTEGER,
            round_pick INTEGER,
            overall_pick INTEGER,
            draft_type VARCHAR,
            team_id INTEGER,
            team_city VARCHAR,
            team_name VARCHAR,
            team_abbreviation VARCHAR,
            organization VARCHAR,
            organization_type VARCHAR,
            has_profile INTEGER,
            ingested_at TIMESTAMP
        )
        """,
        truncate_before_load=True,
    )


if __name__ == "__main__":
    load_draft()
    print("DIM_DRAFT loaded")
