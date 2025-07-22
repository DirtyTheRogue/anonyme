import time
from functools import wraps
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import pickle
import warnings
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, mean_squared_error
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)


def save_artefacts(output_path, first_name_dict, name_dict, NIR_dict, date_dict, cache, json_files_dict, time_df):
    if cache:
        output_pickle_path = os.path.join(output_path, "anonymization_artefacts.pkl")
        artefacts = {
            "first_name_dict": first_name_dict,
            "name_dict": name_dict,
            "NIR_dict": NIR_dict,
            "date_dict": date_dict
        }
        with open(output_pickle_path, "wb") as f:
            pickle.dump(artefacts, f)

        if time_df is not None:
            time_df.to_csv(f"{output_path}/execution_time.csv")
        print(f"All artefacts have been saved in a single pickle file at {output_pickle_path}")
    else:
        for table_name, json_list in json_files_dict.items():
            first_name_dict, name_dict, NIR_dict, date_dict = json_list
            output_pickle_path = os.path.join(output_path, f"{table_name}_artefacts.pkl")
            artefacts = {
                "first_name_dict": first_name_dict,
                "name_dict": name_dict,
                "NIR_dict": NIR_dict,
                "date_dict": date_dict
            }
            with open(output_pickle_path, "wb") as f:
                pickle.dump(artefacts, f)
            print(f"Artefacts for table {table_name} have been saved in a pickle file")


def make_unique_dir(path):
    original_path = path
    counter = 1

    while os.path.exists(path):
        path = f"{original_path}_{counter}"
        counter += 1

    os.makedirs(path, exist_ok=True)
    return path


def timing_decorator(func_timings):
    """
    Un décorateur pour mesurer le temps d'exécution des méthodes
    et enregistrer les résultats dans une liste avec des informations supplémentaires.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            table_name = kwargs.get("table_name", "Unknown")
            start_time = time.time()
            result = func(self, *args, **kwargs)
            elapsed_time = time.time() - start_time

            func_timings.append({
                "Table": table_name,
                "Method": func.__name__,
                "Execution_Time_Seconds": elapsed_time
            })

            return result
        return wrapper
    return decorator


def save_figs(anon_indiv, ori_indiv, comparison_indiv, inf_path, indiv_path):
    # Unique Count Viz
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axes = plt.subplots(2, 2, figsize=(25, 20))
    fig.suptitle('Individualisation Test', fontsize=28)

    variables = ['unique_count', 'unique_percentage', 'small_groups_count', 'small_groups_percentage']
    titles = ['Unique Count', 'Unique Percentage', 'Small Groups Count', 'Small Groups Percentage']

    for i, ax in enumerate(axes.flatten()):
        var = variables[i]
        x = np.arange(len(anon_indiv['columns']))
        width = 0.35

        bars1 = ax.bar(x - width/2, anon_indiv[var], width, label='Anonymized Data', color="#00CEE2", alpha=0.8)
        bars2 = ax.bar(x + width/2, ori_indiv[var], width, label='Original Data', color="#0083EF", alpha=0.8)

        for bar in bars1:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=8)
        for bar in bars2:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=8)

        ax.set_title(titles[i], fontsize=18)
        ax.set_xticks(x)
        ax.set_xticklabels(anon_indiv['columns'], rotation=45, ha='right')

    ax.set_ylabel('Valeurs')
    ax.legend()
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f"{indiv_path}/individualisation_plot.png")

    # Exact Match Comparison Viz
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axes = plt.subplots(1, 2, figsize=(15, 10))
    fig.suptitle('Exact Match Comparison', fontsize=28)

    variables = ['Match_Count', 'Percentage']
    titles = ['Match Count', 'Percentage']

    for i, ax in enumerate(axes.flatten()):
        var = variables[i]
        x = np.arange(len(comparison_indiv['Combo']))
        width = 0.35

        bars = ax.bar(x - width/2, comparison_indiv[var], width, color="#0083EF", alpha=0.8)

        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=8)

        ax.set_title(titles[i], fontsize=18)
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_indiv['Combo'], rotation=45, ha='right')
        ax.set_ylabel('Valeurs')

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f"{indiv_path}/comparison_plot.png")


def encode_target(target, table):
    """
    Encode the target variable from the provided table based on its unique values and data type.
    """
    y = table[target].fillna(table[target].mode()[0])

    if y.nunique() == 2:
        y_encoded = (y == y.unique()[0]).astype(int)
    elif y.nunique() < 12:
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
    else:
        if y.dtype == "object":
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
        else:
            y_encoded = y
    return y_encoded


def encode_features(exp_features, table):
    """
    Encodes the explanatory features from the provided table based on its unique values and data type.
    """
    encoded_x = table[exp_features].copy()
    for col in exp_features:
        if encoded_x[col].dtype == "object":
            le = LabelEncoder()
            encoded_x[col] = le.fit_transform(encoded_x[col].astype(str))
    return encoded_x


def plot_performance(X_test, y_test, y_pred, model, output_path, table_type):
    """
    Fonction pour afficher les visualisations des performances du modèle de classification ou de régression.
    """
    if isinstance(model, RandomForestClassifier):
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=np.unique(y_test), yticklabels=np.unique(y_test))
        plt.title("Matrice de Confusion")
        plt.xlabel("Prediction")
        plt.ylabel("Vrai label")
        plt.savefig(f"{output_path}/confusion_matrix_{table_type}.png")

        if len(np.unique(y_test)) == 2:
            fpr, tpr, thresholds = roc_curve(y_test, model.predict_proba(X_test)[:, 1])
            roc_auc = auc(fpr, tpr)
            plt.figure(figsize=(6, 5))
            plt.plot(fpr, tpr, color='blue', lw=2, label=f'Courbe ROC (AUC = {roc_auc:.2f})')
            plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
            plt.title("Courbe ROC")
            plt.xlabel("Taux de faux positifs")
            plt.ylabel("Taux de vrais positifs")
            plt.legend(loc='lower right')
            plt.savefig(f"{output_path}/roc_curve_{table_type}.png")

        else:
            plt.figure(figsize=(6, 5))
            plt.scatter(y_test, y_pred, color='blue', alpha=0.6)
            plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', lw=2)
            plt.title("Régression - Erreurs des prédictions")
            plt.xlabel("Valeurs réelles")
            plt.ylabel("Valeurs prédites")
            plt.savefig(f"{output_path}/predictions_error_{table_type}.png")

            feature_importances = model.feature_importances_
            sorted_idx = np.argsort(feature_importances)[::-1]
            plt.figure(figsize=(8, 6))
            plt.bar(range(len(sorted_idx)), feature_importances[sorted_idx], align='center')
            plt.xticks(range(len(sorted_idx)), np.array(X_test.columns)[sorted_idx])
            plt.title("Importance des caractéristiques")
            plt.xlabel("Importance")
            plt.savefig(f"{output_path}/features_importance_{table_type}.png")

