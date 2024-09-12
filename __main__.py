#####################################
#  Finance Visualisateur - 9/7/24   #
#####################################
# NOTES :
"""
"""
# -- IMPORTS --
# Modules
import sys
import pandas as pd
import matplotlib.pyplot as plt
from utility import GUI, Settings, File
from financetrack.function_dir.csv_managing import import_new_transactions_dt, update_csvfile_with_dataframe
from financetrack.function_dir.modify_dataframe import separer_types_de_transactions, categoriser_transactions, ajouter_nom_proprietaire
from financetrack.function_dir.interfaces import get_interval_dates, date_filter, hist_paired_and_stacked, evolution_balance
from datetime import datetime

# Settings
logger = Settings.setup_logging("debugging")
logger.info("Logging configuration: COMPLETE")

# -- OPÉRATIONS DÉFINIES --




# -- VARIABLES INITIALES --
INPUT_PATH = "data/input/CSV_2024-07-09-11.28.csv"
ARCHIVES_PATH = "data/output/finance_archives.csv"
NAMES_PATH = "data/input/finance_names.json"
PRODUCED_PATH = "data/output/finance_completed.csv"
renaming_tab = {"Nº de séquence": "num",
        "Date d'exécution": "date_exe",
        "Date valeur": "date_val",
        "Montant": "amount",
        "Devise du compte": "currency",
        "Numéro de compte": "owner",
        "Type de transaction": "type",
        "Contrepartie": "sender_account",
        "Nom de la contrepartie": "sender_name",
        "Communication": "communication",
        "Détails": "details",
        "Statut": "status",
        "Motif du refus": "refusal_reason"
     }
used_headers = ["num", "date_exe", "amount", "type", "sender_account", "sender_name", "details"]


# -- FONCTIONS MAÎTRES --
def mise_a_jour_depuis_dossier():
    """Traitement du nouveau rapport financier."""
    logger.info("OP: UpdatingArchives: START")
    new = INPUT_PATH
    update_df = import_new_transactions_dt(new, ARCHIVES_PATH, )
    update_df = update_df.rename(columns=renaming_tab)
    update_df.set_index('num')
    logger.info(f"UpdatingArchives: new transactions LOADED \n\t({update_df.columns})")
    update_csvfile_with_dataframe(ARCHIVES_PATH, update_df, used_headers)


def categorisation_des_transactions():
    """Selon type (Paiement/Virement), selon le destinataire (magasin) ou de l'expéditeure"""
    logger.info("OP: CategorisingTransactions: START")
    df: pd.DataFrame = pd.read_csv(ARCHIVES_PATH, delimiter=';', index_col="num")
    logger.info(f"CategorisingTransactions: LOADED \n\t({df.columns})")
    typing_df = separer_types_de_transactions(df.copy())
    categ_df = categoriser_transactions(typing_df, dict_path=NAMES_PATH)
    owner_df = ajouter_nom_proprietaire(categ_df,  dict_path=NAMES_PATH)
    logger.info(f"CategorisingTransactions: DONE \n\t({owner_df.columns})")
    owner_df.to_csv(PRODUCED_PATH, sep=';')
    # HEADERS : num;date_exe;amount;type;sender_account;sender_name;details;store_name;store_bankref;category;sender_name
    logger.info(f"CategorisingTransactions: SAVED\t->\tOP:END")


def montrer_graph_resultats():
    """Affichage des résultats"""
    logger.info("OP: ShowingGraph: START")
    # Données
    df = pd.read_csv(PRODUCED_PATH, delimiter=';')
    # df = pd.read_csv("FinancesTracker/data/archives/by_types.csv", delimiter=';')
    # Filtre
    from_date, to_date = get_interval_dates()
    start_ddt = datetime.strptime(from_date, '%d/%m/%Y')
    end_ddt = datetime.strptime(to_date, '%d/%m/%Y')
    logger.info(f"ShowingGraph: date RECEIVED ({start_ddt} - {end_ddt})")
    df_interv = date_filter(df.copy(), "date_exe", start_ddt, end_ddt)
    logger.info(f"ShowingGraph: FILTERED (len={len(df_interv['amount'])}) \n\t({df_interv.columns})")
    # Graphiques
    hist_paired_and_stacked(df_interv.iloc[::-1], start_ddt, end_ddt)
    evolution_balance(df_interv.iloc[::-1])
    logger.info(f"OP:ShowingGraph: graph CREATED \n\t({df.columns})")
    plt.show()


# -- PROGRAMME --
if __name__ == '__main__':
    # - Variables -
    # - Environment -
    File.create_file(ARCHIVES_PATH, can_make_dirs=False, default_content=";".join(used_headers))
    # - Programme -
    mise_a_jour_depuis_dossier()
    categorisation_des_transactions()
    montrer_graph_resultats()

    sys.exit(0)
    df = pd.DataFrame({'num': [1, 2, 3], 'type': ['Paiement par carte', 'Virement en euros', 'Paiement par carte'], 'B': [4, 5, 6]})
    objet = None
    # Programme test
    p, v = separer_paiements_virements(df)
    print(p)
    print(v)
