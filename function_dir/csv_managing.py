# ----------------------------
#   Module local de fonctions
#        <PROJET NOM>
# DATE: 
# VERSION: 1.0
# ----------------------------
"""  -- Structures des fonctions disponibles --
Classement 1
 - function_name(arg1)
Classement 2
- f2(arg1)
"""


# -- IMPORTS --
# Modules basiques
import sys, os, csv
if __name__ == '__main__':
    # Ajouter accès aux modules du projet
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Modules renommés
import numpy as np
import pandas as pd
# Imports spécifiques
from typing import Any, Optional
# Imports locaux
from utility import File, Settings, GUI


# Paramètres
logger = Settings.setup_logging("debugging")
FULLLIST_PATH = "data/output/finance_full_list.csv"

# -- FONCTIONS DÉFINIES --
# 1 - Récupération des données CSV
def import_csv_list(path):
    """"""
    with open(path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        transactions = []
        for row in reader:
            num = row[0]
            date = row[1]
            amount = row[3]
            assert row[4] == "EUR"
            assert row[5] == "BE89001884679785"
            trans_type = row[6]
            expediteur_number_name = (row[7], row[8])
            communication = row[9]
            details = row[10]
            assert row[11] == "Accepté" and row[12] == ""
            transactions.append({
                "num": num,
                "date": date,
                "amount": amount,
                "type": trans_type,
                "expediteur": expediteur_number_name,
                "communication": communication,
                "details": details,
                "status": "Accepté"
            })

def import_csv_pandas(path, columns=None):
    logger.info(f"CSV Import: to Pandas ({path})")
    df = pd.read_csv(path, delimiter=';')
    return df

            

# 2 - Mise à jour des données
def import_new_transactions_dt(new_csv, last_csv):
    logger.info(f"ManageNewImport: START ({new_csv})")
    raw_dt = import_csv_pandas(new_csv)
    last_dt = import_csv_pandas(last_csv)
    return filter_new_transactions(raw_dt, last_dt)

def filter_new_transactions(raw_dt: pd.DataFrame, last_dt: pd.DataFrame):
    """Retire toutes les transactions de raw_dt présentent dans last_dt"""
    if last_dt.empty:
        return raw_dt
    df = raw_dt.loc[:last_dt.index[0],:].iloc[:-1,:]
    return df


def update_csvfile_with_dataframe(csv_path, df, headers):
    """Les row du DataFrame df sont toutes à ajoutée au CSV. Le première rangée doit arriver en première ligne du CSV"""
    # 1 - ecq les colones correspondent
    # 2 - Lire le contenu actuel du fichier CSV
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        existing_headers = next(reader)  # Récupérer les en-têtes
        existing_data = list(reader)  # Lire le reste des données
    # 3 - Convertir le DataFrame en liste de listes
    assert headers == existing_headers
    selected_data = df.loc[:, headers]
    new_data = selected_data.values.tolist()
    # 4 - Écrire les nouvelles données dans le fichier CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(headers)
        writer.writerows(new_data)
        writer.writerows(existing_data)

def remake_csvfile_with_dataframe(csv_path, df):
    """Les row du DataFrame df sont toutes à ajoutée au CSV. Le première rangée doit arriver en première ligne du CSV"""
    # 1 - ecq les colones correspondent
    # 2 - Lire le contenu actuel du fichier CSV
    old_df = import_csv_pandas(FULLLIST_PATH)
    logger.info(f"UpdateCSVArchive: old LOADED (headers: {old_df.add_prefix()} size: {len(old_df)})")
    # 3 - Convertir le DataFrame en liste de listes
    new_data = df.values.tolist()
    # 4 - Écrire les nouvelles données dans le fichier CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(headers)
        writer.writerows(new_data)
        writer.writerows(existing_data)


# -- TESTS ET EXEMPLES --
if __name__ == '__main__':
    # Variables
    new = "FinancesTracker/data/input/CSV_2024-07-09-09.34.csv"
    last = "FinancesTracker/data/input/CSV_2024-07-09-11.28.csv"
    # Programme test
    print(import_new_transactions_dt(new, last))
