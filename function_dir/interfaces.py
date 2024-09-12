# ----------------------------
#   Module local de fonctions
#        <PROJET NOM>
# DATE: 
# VERSION: 1.0
# ----------------------------
"""  -- Structures des fonctions disponibles --
Choix de paramètres
 - get_interval_dates()
Modifier les données bruts pour graphique
 - date_filter(df, columns_texted, val_min, val_max)
Réalisation des graphiques
 - hist_paired_and_stacked(df, date_start, date_end)
 - evolution_balance(df)
"""


# -- IMPORTS --
# Modules basiques
import os, logging, sys
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Modules renommés
import tkinter as tk
import ttkbootstrap as ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
# Imports spécifiques
from datetime import date
from datetime import datetime
# Imports locaux
from utility_dir.utility import File, Settings, GUI
from class_dir.gui_app import DateRangeApp


# Paramètres
logger = Settings.setup_logging("debugging")


# -- FONCTIONS DÉFINIES --
# 1 - Choix du mode de sélection
def get_interval_dates():
    """    """
    # Widget
    window = GUI.set_basic_window(title="Choix de la période", size="400x200")
    from_date = tk.StringVar(window)
    to_date = tk.StringVar(window)
    # Boite de dialogue
    DateRangeApp(window, from_date, to_date)
    window.mainloop()
    # Résultat
    logger.info(f"Dates choisies : {from_date.get()} - {to_date.get()}")
    return from_date.get(), to_date.get()


# 2 - Application de la sélection
def date_filter(df, column, start_ddt, end_ddt):
    """Filtre les données d'un DataFrame selon une période donnée.
    df : pd.DataFrame (dont une colone "date" contenant des dates au format "dd/mm/yyyy")
    column : str ("date_exe")
    start_date, end_date : datatime
    """
    # Convertir la colonne de dates en objets datetime
    df[column] = pd.to_datetime(df[column], format='%d/%m/%Y')
    
    # Appliquer le filtre
    return df.loc[(df[column] >= start_ddt) & (df[column] <= end_ddt), :]



# 3 - Réalisation des graphiques
def basic_axis_design(axis: plt.Axes, title: str, legend_title: str) -> None:
    """titres et légende, cacher le cadre, couleur de fond, grille horizontale"""
    axis.set_title(title, fontsize=16, fontweight='bold', pad=20)
    axis.set_xlabel('Dates', fontsize=12, fontweight='bold')
    axis.set_ylabel('Montant', fontsize=12, fontweight='bold')
    axis.legend(title=legend_title, title_fontsize='12', fontsize='10', loc='upper left', bbox_to_anchor=(1, 1))
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.set_facecolor('#f0f0f0')
    axis.grid(True, axis='y', linestyle='--', alpha=0.7)


def figure_decoration(fig):
    """Couleur + copyright + Source"""
    fig.patch.set_facecolor('#f0f0f0')
    fig.text(0.95, 0.05, '© MonApp 2023', fontsize=8, color='gray', 
        ha='right', va='bottom', alpha=0.7)  # Copyright
    fig.text(0.98, 0.02, 'Source: Données bancaires FORTIS', ha='right', va='bottom', fontsize=8, fontstyle='italic')  # Sources


def ticks_labels(axes):
    """Uniquement Lundi, en 04 Jan, à 45degres, symbole €"""
    axes.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY)) 
    axes.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    axes.tick_params(axis='x', rotation=45, labelsize=10)
    axes.xaxis.set_minor_locator(mdates.DayLocator())
    axes.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{x:,.0f}€'))


def hist_paired_and_stacked(df: pd.DataFrame, date_start, date_end):
    """Fais l'histogram des transactions.
    - Une colone pour Types dépenses (PAIEMENT, ENVOI, RETRAIT) 
    - Une colone pour Types revenus (VERSEMENTS, )
    
    Format du graph :
    fond gris, dates (jour-mois) des lundis comme abcisses, symbole € aux ordonée 
    """
        # Données
    def make_dataframe_for_histogram(df, date_start, date_end):
        """Complèter les jours, regrouper par type et jour."""
        df['amount'] = df['amount'].abs()
        grouped_data = df.groupby(['date_exe', 'type'])['amount'].sum().unstack(fill_value=0)
        date_fullrange = pd.date_range(start=date_start, end=date_end, freq='D')
        grouped_data = grouped_data.reindex(date_fullrange, fill_value=0)
        return grouped_data
    grouped_by_typeday = make_dataframe_for_histogram(df.copy(), date_start, date_end)

        # Graphique
    fig, ax = plt.subplots(figsize=(15, 8))
    # paramètres
    x = mdates.date2num(grouped_by_typeday.index)
    bar_width = 0.5
    # plotting
    paiements = ax.bar(x - bar_width/2, grouped_by_typeday['PAIEMENT'], color='#FF6B6B', width=bar_width, label='PAIEMENT', alpha=0.7)
    envois = ax.bar(x - bar_width/2, grouped_by_typeday.get('ENVOI', 0), bottom=np.array(grouped_by_typeday['PAIEMENT']) , color='#5337DE', width=bar_width, label='ENVOI', alpha=0.7)
    if 'RETRAIT' in df['type'].unique():
        retraits = ax.bar(x - bar_width, grouped_by_typeday['RETRAIT'], bottom=np.array(grouped_by_typeday['PAIEMENT']) + np.array(grouped_by_typeday['ENVOI']) , color='#98969e', width=bar_width, label='RETRAIT', alpha=0.7)
    receptions = ax.bar(x + bar_width/2, grouped_by_typeday.get('ENVOI', 0), color='#4ECDC4', width=bar_width, label='RECEPTION', alpha=0.7)
    # design
    basic_axis_design(ax, 'Transactions entrantes et sortantes de chaque jour', 'Types de transactions')  # graph design
    ticks_labels(ax)  # axes design
    figure_decoration(fig)  # figure decoration

    plt.tight_layout()
    return


def evolution_balance(df: pd.DataFrame, initial_balance=0):
    """Fais l'évolution du solde du compte.
    """
    # Données
    assert df['date_exe'].is_monotonic_increasing, "Les dates ne sont pas ordonnées."
    df['balance'] = initial_balance + df['amount'].cumsum()
    
        # Graphique
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.plot(df['date_exe'], df['balance'], label='Solde', color='#e07a0d', linewidth=2)
    basic_axis_design(ax, "Évolution du solde du compte", "Tracés")  # graph design
    ax.axhline(y=0, c='black', ls='-', lw=1, alpha=0.7)
    figure_decoration(fig)  # figure decoration
    ticks_labels(ax)  # axes design

    plt.tight_layout() 
    return

# -- TESTS ET EXEMPLES --
if __name__ == '__main__':
    # Variables
    variable = None
    objet = None
    # Programme test
