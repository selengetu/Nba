def check_not_null(df, column_name):
    if df[column_name].isnull().any():
        null_count = df[column_name].isnull().sum()
        raise ValueError(
            f"Data quality check failed: {column_name} has {null_count} NULL values"
        )


def check_unique(df, column_name):
    duplicates = df[column_name].duplicated().sum()
    if duplicates > 0:
        raise ValueError(
            f"Data quality check failed: {column_name} has {duplicates} duplicate values"
        )


def check_row_count(df, min_rows):
    if len(df) < min_rows:
        raise ValueError(
            f"Data quality check failed: expected at least {min_rows} rows, got {len(df)}"
        )
