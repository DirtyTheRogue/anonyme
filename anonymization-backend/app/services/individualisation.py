import pandas as pd
import itertools

class Individualisation:
    def __init__(self, anon_table, original_table, columns_to_combine, id_column, group_var, k=10):
        self.anon_table = anon_table
        self.original_table = original_table
        self.columns_to_combine = columns_to_combine
        self.group_var = group_var
        self.k = k
        self.id_column = id_column

    def analyze_unique_combinations(self, df: pd.DataFrame, table_name) -> pd.DataFrame:
        """
        Analyze unique row counts for all combinations of specified columns.

        Args:
            df (pd.DataFrame): Input DataFrame.
            table_name (str): Name of the input DataFrame.

        Returns:
            pd.DataFrame: Dataframe of (column combination, unique count, percentage) tuples.
        """
        results = []
        total_rows = len(df)

        if total_rows == 0:
            return []

        if not self.columns_to_combine:
            return []

        max_combination_length = min(5, len(self.columns_to_combine))

        for r in range(1, max_combination_length + 1):
            for combo in itertools.combinations(self.columns_to_combine, r):
                group_counts = df.groupby(list(combo), dropna=False)[self.group_var].nunique()

                unique_individuals = (group_counts == 1).sum()
                small_groups = ((group_counts > 1) & (group_counts <= self.k)).sum()

                percentage_unique = (unique_individuals / total_rows) * 100 if total_rows > 0 else 0
                percentage_small = (small_groups / total_rows) * 100 if total_rows > 0 else 0

                results.append((table_name, combo, unique_individuals, percentage_unique, small_groups, percentage_small))

        return pd.DataFrame(
            sorted(results, key=lambda x: (-x[2], -x[4], len(x[1]), x[1])),
            columns=["table_name", "columns", "unique_count", "unique_percentage", "small_groups_count", "small_groups_percentage"]
        )

    def compare_tables(self) -> pd.DataFrame:
        """
        Compare the original and the anonymized dataframe and count exact matches for combinations of comparison columns,
        merging the tables based on ID column.

        Returns:
            pd.DataFrame: Dataframe of (column combination, match count, percentage) tuples.
        """
        if self.id_column not in self.original_table.columns:
            raise ValueError("ID columns not found in original DataFrames")

        if self.anon_table[self.id_column].isna().all():
            self.anon_table[self.id_column] = self.original_table[self.id_column]

        merged = pd.merge(
            self.original_table,
            self.anon_table,
            left_on=self.id_column,
            right_on=self.id_column,
            suffixes=("_1", "_2")
        )

        results = []
        total_rows = len(merged)

        if total_rows == 0:
            return []

        for r in range(1, len(self.columns_to_combine) + 1):
            for combo in itertools.combinations(self.columns_to_combine, r):
                match_mask = pd.Series(True, index=merged.index)
                for col in combo:
                    col_match = (
                        merged[f"{col}_1"] == merged[f"{col}_2"]
                    ) | (
                        merged[f"{col}_1"].isna() & merged[f"{col}_2"].isna()
                    )
                    match_mask = match_mask & col_match

                match_count = match_mask.sum()
                percentage = (match_count / total_rows) * 100 if total_rows > 0 else 0

                results.append(("Merge Table", combo, match_count, percentage))

        return pd.DataFrame(
            sorted(results, key=lambda x: (-x[2], -x[3], len(x[1]), x[1])),
            columns=["Table_Name", "Combo", "Match_Count", "Percentage"]
        )

    def run_test(self):
        compare_output = self.compare_tables()
        output_original = self.analyze_unique_combinations(self.original_table, "originale")
        output_anon = self.analyze_unique_combinations(self.anon_table, "anon")

        return {
            "Comparison": compare_output,
            "Original_Unique_Count": output_original,
            "Anon_Unique_Count": output_anon
        }
