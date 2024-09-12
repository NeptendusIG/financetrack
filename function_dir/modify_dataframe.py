# ----------------------------
#
#        <PROJET NOM>
# DATE:
# VERSION: 1.0
# ----------------------------
"""  -- Structures des fonctions disponibles --
Associer type et Simplifier certains champs (redondants)
 - separer_types_de_transactions(df_source)
Catégoriser selon le magasin
 - simplifier_df_paiements(df)
 - categoriser_les_paiements(df, categ_dict_path)
"""


# -- IMPORTS --
# Modules basiques
import os, sys, re
if __name__ == '__main__':
    # Ajouter accès aux modules du projet
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Modules renommés
import pandas as pd
import tkinter as tk
# Imports spécifiques
from typing import Any, Optional
# Imports locaux
from utility_dir.utility import File, Settings, GUI
from class_dir.gui_app import FindStoreApp, FindAccountApp


# Paramètres
logger = Settings.setup_logging("debugging")


# -- FONCTIONS DÉFINIES --
# 1 - Associer type et Simplifier certains champs (redondants)
def separer_types_de_transactions(df_source):
    """Associe les transations à un type parmis :
    (argent quitte le compte) PAIEMENT, ENVOI, RETRAIT, 
    (argent arrive sur compte) RECEPTION
    """
    df = df_source.copy()
    df["type"] = df["type"].replace({"Paiement par carte": "PAIEMENT"})
    mask_paiement = df["type"] == "PAIEMENT"
    mask_virement = df["type"].str.contains("Virement")
    mask_retrait = df["type"].str.contains("Retrait")
    mask_positif = df["amount"] > 0
    # logger.debug(f"mask for filtrer: \n{mask_paiement}\n{mask_virement}\n{mask_positif}")
    df.loc[mask_virement & mask_positif, "type"] = "RECEPTION"
    df.loc[mask_virement & ~mask_positif, "type"] = "ENVOI"
    df.loc[mask_retrait & ~mask_positif, "type"] = "RETRAIT"
    return df


# 2 - Catégoriser selon le magasin
def categoriser_transactions(df, dict_path, dict_name="categorisation_store"):
    """Simplifie et catégorise les transactions de type PAIEMENT
    @pre: df de transactions
    @post: df de transactions avec catégorie pour chaque paiement
    """
    logger.info("OP:Categorisation: START")
    df['store_name'] = ""
    df['store_bankref'] = ""
    df['owner_num'] = ""
    # Récupérer les transaction de PAIEMENT
    mask = df["type"] == "PAIEMENT"
    df_paiements = df[mask].copy()

    # Simplifier les transactions, séparer les champs
    df_paiements = simplifier_df_paiements(df_paiements)
    logger.info("Categorisation: details SIMPLIFIED")

    # Catégoriser les paiements par rapport au magasin 
    categ_dict = File.JsonFile.get_value_jsondict(dict_path, dict_name)
    logger.info("Categorisation: stores names LOADED")
    df_paiemt_categ = categoriser_les_paiements(df_paiements, categ_dict)
    logger.info("Categorisation: paiements CATEGORISED")

    # Mettre à jour la liste des données des magasins
    File.JsonFile.set_value_jsondict(dict_path, key=dict_name, value=categ_dict)
    logger.debug("Categorisation: stores names UPDATED")
    pprint_dict = "\n\t\t" + "\n\t\t".join([f'{key}: {val}' for key, val in categ_dict.items()])
    logger.debug(f"Categories: {pprint_dict}")

    # Mettre à jour le dataframe initial
    df[mask] = df_paiemt_categ
    return df


def simplifier_df_paiements(df_paiements):
    """Supprime les données redondantes
    la val "details" donnée ainsi:
    [PAIEMENT...7538] [Nom Magasin] [Localité] [Date] [Moyen (VISA DEBIT/BANCONTACT)] <frais d'échanges> [REFERENCE BANQUE ...]
    """
    CARD_PREFIX_PATTERN = r"PAIEMENT AVEC LA CARTE DE DEBIT NUMERO \d{4} \d{2}XX XXXX \d{4} "
    DATE_PATTERN = r'\d{2}/\d{2}/\d{4}'
    REF_BANK_PATTERN = r'REFERENCE BANQUE : (\d{16})'

    def simplifier(row):
        details = row["details"]
        # Suppression du préfixe de carte
        row["owner_num"] = details[39:58]
        details = re.sub(CARD_PREFIX_PATTERN, "", details)
        
        # Extraction du nom et de la localisation
        match = re.match(f'^(.*?)\s{DATE_PATTERN}\s(.*)$', details)
        if match:
            row["store_name"] = match.group(1)
            details = match.group(1) + " " + match.group(2)
       
        # Suppression de "DATE VALEUR" et de la date associée
        details = re.sub(r'DATE VALEUR : \d{2}/\d{2}/\d{4}', '', details)

        # Extraction de la référence bancaire
        ref_match = re.search(REF_BANK_PATTERN, details)
        if ref_match:
            row["store_bankref"] = ref_match.group(1)
            details = re.sub(REF_BANK_PATTERN, '', details)

        logger.debug(f"details={row['details']} \tnew={details.strip()} \t{row['store_name']} \t{row['store_bankref']} \t{row['owner_num']}")
        row["details"] = details.strip()
        return row
   
    df_paiements['store_name'] = "111"
    df_paiements['store_bankref'] = ""
    df_paiements['owner_num'] = ""
    
    return df_paiements.apply(simplifier, axis=1)


def categoriser_les_paiements(df, categ_dict):
    """Ajoute le champ catégorie, correspondant au magasin.
    @post: df de paiements uniquement (déjà simplifié)
    @return: df de paiements avec catégorie pour chaque
     - type - entrée modifiée
    """
    def find_category(details, categ_dict_stores=categ_dict):
        for key, value in categ_dict_stores.items():
            if key in details:
                logger.debug(f"StoreFound: {key} -> {value}")
                return value
        else:
            logger.debug("StoreNotFound")
            return ask_new_store_registration(details, categ_dict_stores)


    logger.info("StoreCategorisation: START")
    df["category"] = None
    for index, row in df.iterrows():
        result = find_category(row['details'], categ_dict_stores=categ_dict)
        if isinstance(result, bool) and result == True:
            continue  # row['details'] = None
        if isinstance(result, bool) and result == False:
            logger.info(f"StoreCategorisation: Stop Asking to User ({index=})")
            break  # row['details'] = None
        row['details'] = result
    logger.info("StoreCategorisation: DONE")
    return df


def ask_new_store_registration(extrait: str, categ_dict: dict):
    """Demande pour l'identification d'un magasin
    Si trouvé -> Ajouter à la liste
    Sinon return None et ajouter la transaction à liste spéciale ?
    """
    logger.info("AskingUser: for new store registration")
    # Fenetre de dialogue
    window = GUI.set_basic_window(title="Magasin inconnu")
    infos = {"store_name": tk.StringVar(window), 
                 "store_key": tk.StringVar(window),
                 "is_validated": tk.BooleanVar(window),
                 "is_continue": tk.BooleanVar(window, value=True)}
    FindStoreApp(window, infos, extrait)
    window.mainloop()
    # Gestion de la réponse (valide/passer/passer & arrêter)
    logger.debug(f"AskingUser: RESULT: {infos['store_key'].get()} -> {infos['store_name'].get()} (valid={infos['is_validated'].get()} continue={infos['is_continue'].get()})")
    if infos["is_validated"].get() == True:
        categ_dict[infos["store_key"].get()] = infos["store_name"].get()
        # logger.debug("StoreCategorisation: NewRegistration: {informations['store_key']} -> {informations['store_name']}")
        return infos["store_name"].get()
    # logger.debug(f"StoreCategorisation: NewRegistration: NotValidated ({infos['is_continue']})") 
    return infos["is_continue"].get()  # Réponse non validée 
    

# TODO: 
# 3 - Ajouter nom du compte
def ajouter_nom_proprietaire(df, dict_path, dict_key="accounts"):
    """Ajoute le nom du propriétaire du compte"""
    df["sender_name"] = None
    return df
    accounts_dict = File.JsonFile.get_value_jsondict(dict_path, dict_key)
    for index, row in df.iterrows():
        numero = row["owner_num"]
        if not numero:
            continue
        if numero in accounts_dict:
            row["sender_name"] = accounts_dict[numero]
        else:
            logger.debug(f"OwnerNotFound: {numero}")
            print("\nOwner not found for account number: ", numero)
            input()
            name = input("Please enter the name of the account: ").strip()
            if name:
                row["sender_name"] = name
                accounts_dict[numero] = name
    File.JsonFile.set_value_jsondict(dict_path, key=dict_key, value=accounts_dict)
    return df



# -- TESTS ET EXEMPLES --
if __name__ == '__main__':
    # Variables
    df = pd.DataFrame({'num': [1, 2, 3], 'type': ['Paiement par carte', 'Virement en euros', 'Virement par carte'], 
                        'amount': [40, 50, -60],
                       'details': [
                           "PAIEMENT AVEC LA CARTE DE DEBIT NUMERO 4871 04XX XXXX 7538 SUMUP *CERCLE INDUSTR LOUVAIN LA NE 18/04/2024 VISA DEBIT - SANS CONTACT REFERENCE BANQUE : 2404191406272737 DATE VALEUR : 18/04/2024", 
                           "", 
                           "PAIEMENT AVEC LA CARTE DE DEBIT NUMERO 4871 04XX XXXX 7538 ZEB GEMBLOUX GEMBLOUX 30/01/2024 BANCONTACT REFERENCE BANQUE : 2401301402173506 DATE VALEUR : 30/01/2024"
                        ]
                    })
    objet = None
    # Programme test
    paiements, r, e = separer_paiements_receptions_envois(df)
    print(paiements)
    print(r)
    print(e)
    paiements = simplifier_df_paiements(paiements)
    print(paiements)
    print(v)