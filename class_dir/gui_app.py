#############################
#     Project name      #
#      Class name       #
#        Date//         #
#############################
# NOTES :
"""

"""
# IMPORTS
import sys, os
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utility_dir.utility import GUI, File, Settings
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from datetime import datetime, date

# SETTINGS
logger = Settings.setup_logging("debugging")



class DateRangeApp:
    def __init__(self, master, start_entry_var, end_entry_var):
        self.master = master
        master.title("Sélection de plage de dates")

        # Date de début (premier jour du mois courant)
        self.start_label = ttk.Label(master, text="Date de début:")
        self.start_label.grid(row=0, column=0, padx=5, pady=5)
        self.start_entry = ttk.Entry(master, textvariable=start_entry_var)
        self.start_entry.grid(row=0, column=1, padx=5, pady=5)

        # Date de fin (date du jour)
        self.end_label = ttk.Label(master, text="Date de fin:")
        self.end_label.grid(row=1, column=0, padx=5, pady=5)
        self.end_entry = ttk.Entry(master, textvariable=end_entry_var)
        self.end_entry.grid(row=1, column=1, padx=5, pady=5)

        # Bouton Valider
        self.validate_button = ttk.Button(master, text="Valider", command=self.validate_dates)
        self.validate_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Initialiser les dates
        self.set_initial_dates()

    def set_initial_dates(self):
        today = date.today()
        first_day = date(today.year, 1, 1)

        self.start_entry.insert(0, first_day.strftime("%d/%m/%Y"))
        self.end_entry.insert(0, today.strftime("%d/%m/%Y"))

    def validate_dates(self):
        start_date = self.start_entry.get()
        end_date = self.end_entry.get()
        self.quit()
    
    def quit(self):
        self.master.quit()
        self.master.withdraw()


class FindStoreApp:

    def __init__(self, master, informations_dict, transaction_details):
        self.master = master
        master.title("Recherche de magasin")
        self.store_var = informations_dict["store_name"]
        self.store_key_var = informations_dict["store_key"]
        self.initial_hint = transaction_details.split(" ")[0]
        self.validation = informations_dict["is_validated"]
        self.continue_asking = informations_dict["is_continue"]

        # Information brut 
        self.info_label = ttk.Label(master, text=transaction_details, font=("Arial", 14, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Champ de recherche
        self.store_label = ttk.Label(master, text="Magasin correspondant:")
        self.store_label.grid(row=1, column=0, padx=5, pady=5)
        self.store_entry = ttk.Entry(master, textvariable=self.store_var)
        self.store_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.key_label = ttk.Label(master, text="Code d'indentification:")
        self.key_label.grid(row=2, column=0, padx=5, pady=5)
        self.key_entry = ttk.Entry(master, textvariable=self.store_key_var)
        self.key_entry.grid(row=2, column=1, padx=5, pady=5)

        # Boutons (Valider & Annuler & Fermer)
        self.search_button = ttk.Button(master, text="Valider", command=self.valid_store)
        self.search_button.grid(row=3, column=0, columnspan=1, pady=10, sticky="e")
        self.cancel_button = ttk.Button(master, text="Annuler", command=self.cancel)
        self.cancel_button.grid(row=3, column=1, columnspan=1, pady=10, padx=5, sticky="w")
        self.close_button = ttk.Button(master, text="Fermer", command=self.stop)
        self.close_button.grid(row=4, column=1, pady=10, sticky="e")

        # Initialiser le champ
        self.store_entry.insert(0, self.initial_hint)
        self.key_entry.insert(0, self.initial_hint)

    def quit(self):
        logger.debug(f"QuitApp: Verification: {self.validation.get()=} et {self.store_entry.get()=}")
        if not self.validation.get() or self.store_entry.get():
            self.master.quit()
            self.master.withdraw()
        else:
            self.store_entry.insert(0, "VALEUR NON VIDE")

    def valid_store(self):
        self.validation.set(True)
        self.quit()
    
    def cancel(self):
        self.validation.set(False)
        self.quit()
    
    def stop(self):
        self.validation.set(False)
        self.continue_asking.set(False)
        self.quit()


class FindAccountApp:
    def __init__(self, master, informations_dict, transaction_details):
        self.master = master
        master.title("Déterminer le compte correspondant")
        self.num = informations_dict["account_num"]
        self.name = informations_dict["account_name"]
        self.validation = informations_dict["is_validated"]
        self.continue_asking = informations_dict["is_continue"]

        # Information brut 
        self.info_label = ttk.Label(master, text=transaction_details, font=("Arial", 14, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Champ de recherche
        self.store_label = ttk.Label(master, text="Numéro du compte:")
        self.store_label.grid(row=1, column=0, padx=5, pady=5)
        self.store_entry = ttk.Label(master, text=self.num)
        self.store_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.key_label = ttk.Label(master, text="Nom du compte:")
        self.key_label.grid(row=2, column=0, padx=5, pady=5)
        self.key_entry = ttk.Entry(master, textvariable=self.store_key_var)
        self.key_entry.grid(row=2, column=1, padx=5, pady=5)

        # Boutons (Valider & Annuler & Fermer)
        self.search_button = ttk.Button(master, text="Valider", command=self.valid_store)
        self.search_button.grid(row=3, column=0, columnspan=1, pady=10, sticky="e")
        self.cancel_button = ttk.Button(master, text="Annuler", command=self.cancel)
        self.cancel_button.grid(row=3, column=1, columnspan=1, pady=10, padx=5, sticky="w")
        self.close_button = ttk.Button(master, text="Fermer", command=self.stop)
        self.close_button.grid(row=4, column=1, pady=10, sticky="e")

        # Initialiser le champ
        self.store_entry.insert(0, self.initial_hint)
        self.key_entry.insert(0, self.initial_hint)

    def quit(self):
        logger.debug(f"QuitApp: Verification: {self.validation.get()=} et {self.store_entry.get()=}")
        if not self.validation.get() or self.store_entry.get():
            self.master.quit()
            self.master.withdraw()
        else:
            self.store_entry.insert(0, "VALEUR NON VIDE")

    def valid_store(self):
        self.validation.set(True)
        self.quit()
    
    def cancel(self):
        self.validation.set(False)
        self.quit()
    
    def stop(self):
        self.validation.set(False)
        self.continue_asking.set(False)
        self.quit()



if __name__ == '__main__':
    # tests
    def test_daterangeapp():
        root = tk.Tk()
        start_date = tk.StringVar()
        end_date = tk.StringVar()
        app = DateRangeApp(root, start_date, end_date)
        root.mainloop()
        print(f"Dates sélectionnées : {start_date.get()} - {end_date.get()}")

    def test_findstoreapp():
        root = tk.Tk()
        store_name = tk.StringVar()
        store_key_code = tk.StringVar()
        app = FindStoreApp(root, store_name, store_key_code, "brut_store_name")
        root.mainloop()
        print(f"Magasin recherché : {store_name.get()}")
    
    test_findstoreapp()