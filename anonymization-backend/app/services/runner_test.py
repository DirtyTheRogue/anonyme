import os
import pickle
import re
import pandas as pd

from correlation import Correlation
from individualisation import Individualisation
from inference import Inference
from utils import make_unique_dir, save_figs

def run_reidentification_tests(params: dict) -> dict:
    """
    Lance les tests de réidentification à partir des paramètres passés sous forme de dictionnaire.
    
    Args:
        params (dict): dictionnaire contenant tous les paramètres nécessaires aux tests.

    Returns:
        dict: résumé des résultats, avec les chemins de sauvegarde.
    """

    results_summary = {}

    for (
        og_table_path,
        anon_table_path,
        group_cols,
        count_cols,
        exp_features,
        target,
        id_col,
        group_var,
        og_fusion_table,
        anon_fusion_table,
        fusion_group_cols
    ) in zip(
        params["og_tables"],
        params["anon_tables"],
        params["group_cols"],
        params["count_cols"],
        params["exp_features"],
        params["target"],
        params["ids"],
        params["group_var"],
        params["og_fusion_table"],
        params["anon_fusion_table"],
        params["fusion_columns_to_combine"]
    ):
        table_name = re.search(r'([^/]+)\.(csv|parquet)$', og_table_path).group(1)

        # Chargement des données
        og_table = pd.read_parquet(og_table_path) if og_table_path.endswith(".parquet") else pd.read_csv(og_table_path)
        anon_table = pd.read_parquet(anon_table_path) if anon_table_path.endswith(".parquet") else pd.read_csv(anon_table_path)
        og_fusion_table = pd.read_parquet(og_fusion_table) if og_fusion_table.endswith(".parquet") else pd.read_csv(og_fusion_table)
        anon_fusion_table = pd.read_parquet(anon_fusion_table) if anon_fusion_table.endswith(".parquet") else pd.read_csv(anon_fusion_table)

        output_path = make_unique_dir(f"./results/test_{table_name}")
        results_summary[table_name] = {"path": output_path}

        # --- Test Correlation ---
        os.makedirs(output_path + '/correlation', exist_ok=True)
        corr = Correlation(anon_table, og_table, og_fusion_table, anon_fusion_table, fusion_group_cols, id_col, group_var, k=10)
        try:
            corr_dic = corr.run_test()
        except KeyError as e:
            print(f"erreur correlation: {e}")
            corr_dic = {}
        for key, value in corr_dic.items():
            value.to_csv(f"{output_path}/correlation/{key}.csv")
        results_summary[table_name]["correlation"] = list(corr_dic.keys())

        # --- Test Individualisation ---
        os.makedirs(output_path + '/individualisation', exist_ok=True)
        indiv = Individualisation(anon_table, og_table, group_cols, id_col, group_var)
        indiv_dic = indiv.run_test()
        for key, value in indiv_dic.items():
            value.to_csv(f"{output_path}/individualisation/{key}.csv")
        results_summary[table_name]["individualisation"] = list(indiv_dic.keys())

        # --- Test Inférence ---
        os.makedirs(output_path + '/inference', exist_ok=True)
        inf = Inference(anon_table, og_table, group_cols, count_cols, target, exp_features)
        comparison_table, res_dic = inf.run_test(output_path + "/inference")
        comparison_table.to_csv(f"{output_path}/inference/comparison_table.csv")

        with open(f"{output_path}/inference/metrics.pickle", "wb") as f:
            pickle.dump(res_dic, f)
        results_summary[table_name]["inference"] = {
            "comparison_table": "comparison_table.csv",
            "metrics": "metrics.pickle"
        }

        # --- Visualisation ---
        if params.get("viz", False):
            save_figs(
                indiv_dic["Anon_Unique_Count"],
                indiv_dic["Original_Unique_Count"],
                indiv_dic["Comparison"],
                output_path + "/inference",
                output_path + "/individualisation"
            )

    return results_summary
