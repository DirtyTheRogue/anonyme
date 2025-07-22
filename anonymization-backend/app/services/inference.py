import numpy as np
import pandas as pd
from utils import encode_target, encode_features, plot_performance
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, mean_squared_error


class Inference:
    def __init__(self, anon_table, original_table, group_cols, count_cols, target, exp_features, k=10, r=0.2, l=100):
        self.anon_table = anon_table
        self.original_table = original_table
        self.group_cols = group_cols
        self.count_cols = count_cols
        self.target = target
        self.exp_features = exp_features
        self.k = k
        self.r = r
        self.l = l

    def count_unique_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Count unique values and their ratios in specified columns after grouping.

        Args:
            df (pd.DataFrame): The input dataframe.

        Returns:
            pd.DataFrame: A dataframe with unique value counts and ratios for each group.
        """
        unique_counts = df.groupby(self.group_cols)[self.count_cols].agg(['nunique', 'count'])
        unique_counts.columns = [f'{col}_{agg}' for col, agg in unique_counts.columns]
        unique_counts = unique_counts.reset_index()

        for col in self.count_cols:
            unique_counts[f'{col}_ratio'] = (unique_counts[f'{col}_nunique'] / unique_counts[f'{col}_count']).round(4)

        return unique_counts

    def analyze_unique_counts(self, df: pd.DataFrame) -> dict:
        """
        Analyze the output of count_unique_values function and flag potentially problematic groups.

        Args:
            df (pd.DataFrame): The output dataframe from count_unique_values.

        Returns:
            dict: A dictionary containing analysis results and problematic groups.
        """
        total_rows = df[f'{self.count_cols[0]}_count'].sum()
        total_groups = len(df)
        analysis_results = {}
        problematic_groups = set()

        for col in self.count_cols:
            problematic_df = df[
                (df[f'{col}_nunique'] < self.k) |
                (df[f'{col}_count'] > self.l) |
                (df[f'{col}_ratio'] > self.r)
            ]

            problematic_rows = problematic_df[f'{col}_count'].sum()
            problematic_groups.update(tuple(row) for row in problematic_df[self.group_cols].values)

            analysis_results[col] = {
                'problematic_rows': problematic_rows,
                'problematic_groups': len(problematic_df),
                'proportion_rows': (problematic_rows / total_rows),
                'proportion_groups': (len(problematic_df) / total_groups)
            }

        analysis_results['total_rows'] = total_rows
        analysis_results['total_groups'] = total_groups
        analysis_results['problematic_groups'] = list(problematic_groups)

        return analysis_results

    def compare_problematic_groups(self) -> pd.DataFrame:
        """
        Compare the common values in specified columns for the problematic groups
        between two dataframes.

        Returns:
            pd.DataFrame: A comparison of common values between the two dataframes for problematic groups.
        """
        anon_counts = self.count_unique_values(self.anon_table)
        analysis_results = self.analyze_unique_counts(anon_counts)
        problematic_groups = analysis_results['problematic_groups']

        mask_real = self.original_table[self.group_cols].apply(tuple, axis=1).isin(problematic_groups)
        mask_anon = self.anon_table[self.group_cols].apply(tuple, axis=1).isin(problematic_groups)

        real_filtered = self.original_table[mask_real].copy()
        anon_filtered = self.anon_table[mask_anon].copy()

        real_filtered.loc[:, 'group_key'] = real_filtered[self.group_cols].apply(tuple, axis=1)
        anon_filtered.loc[:, 'group_key'] = anon_filtered[self.group_cols].apply(tuple, axis=1)

        comparison = pd.DataFrame(problematic_groups, columns=self.group_cols)
        comparison['group_key'] = comparison[self.group_cols].apply(tuple, axis=1)

        for col in self.count_cols:
            real_unique = real_filtered.groupby('group_key')[col].apply(set).reindex(comparison['group_key'])
            anon_unique = anon_filtered.groupby('group_key')[col].apply(set).reindex(comparison['group_key'])

            common_values = real_unique.combine(anon_unique, lambda x, y: set() if pd.isna(x) or pd.isna(y) else x & y)
            comparison[f'{col}_common_count'] = common_values.apply(lambda x: len(x) if isinstance(x, set) else 0).values
            comparison[f'{col}_real_count'] = real_unique.apply(lambda x: len(x) if isinstance(x, set) else 0).values
            comparison[f'{col}_anon_count'] = anon_unique.apply(lambda x: len(x) if isinstance(x, set) else 0).values
            comparison[f'{col}_common_ratio'] = comparison[f'{col}_common_count'] / comparison[f'{col}_real_count']

        comparison = comparison.drop('group_key', axis=1)
        return comparison

    def summarize_comparison(self, comparison, t: float = 0.5) -> dict:
        """
        Summarize the comparison results.

        Args:
            comparison (pd.DataFrame): The output from compare_problematic_groups.
            t (float): Threshold for the common ratio. Default is 0.5.

        Returns:
            dict: A summary of the comparison results.
        """
        total_rows = len(self.anon_table)
        summary = {}

        for col in self.count_cols:
            high_ratio_rows = (comparison[f'{col}_common_ratio'] > t) * comparison[f'{col}_anon_count']
            summary[col] = {
                'high_ratio_rows': high_ratio_rows.sum(),
                'percentage_of_total': (high_ratio_rows.sum() / total_rows)
            }

        return summary

    def modelize_inference(self, table, output_path, table_type):
        """
        Performs machine learning inference on the provided data, selecting the model type based on the target variable.

        Args:
            table (pd.DataFrame): A dataframe containing the features and target variable to be used for training and evaluation.

        Returns:
            dict: A dictionary containing either a classification report or the Mean Squared Error (MSE).
        """
        y = encode_target(self.target, table)
        X = encode_features(self.exp_features, table)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42) if len(np.unique(y)) <= 12 else RandomForestRegressor(n_estimators=100, random_state=42)

        pipeline = Pipeline(steps=[('model', model)])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        plot_performance(X_test, y_test, y_pred, model, output_path, table_type)

        if isinstance(model, RandomForestClassifier):
            return classification_report(y_test, y_pred)
        else:
            return mean_squared_error(y_test, y_pred)

    def run_test(self, output_path):
        res = {}
        res["metrics_anon"] = self.modelize_inference(self.anon_table, output_path, "anon")
        res["metrics_og"] = self.modelize_inference(self.original_table, output_path, "og")
        comparison = self.compare_problematic_groups()
        return comparison, res
