#####################################
#   Module Utilitaire - 2024    #
#####################################
""" 
** ORGANISATION **
- Settings : paramètres de configuration
- File : gestion des fichiers
- GUI : interface graphique
"""

# -- IMPORTS --
import os.path, subprocess, logging.config
import tkinter as tk
# import ttkbootstrap as ttk

logger = logging.getLogger("debugging")


# -- FONCTIONS --
class Settings:
    @classmethod
    def setup_logging(cls, name):
        try:
            import utility_dir.log_config as log
            logging.config.dictConfig(log.config)
            return logging.getLogger(name)
        except ImportError:
            print("Module log_config not found")
        except FileNotFoundError:
            print("log files unreachable")


class File:
    @classmethod
    def open_file(cls, file_path):
        """Show/open a file (any type)
        pre:  - file_path
              - import subprocess, platform
        """
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['start', '""', file_path], shell=True)
            elif system == 'Darwin':
                subprocess.run(['open', file_path])
            elif system == 'Linux':
                subprocess.run(['xdg-open', file_path])
            else:
                print("Unsupported operating system")
        except Exception as e:
            print(f"An error occurred: {e}")

    class JsonFile:  # On peut hiérarchiser les classes
        pass
    

class GUI:
    @classmethod
    def set_basic_window(cls, title="Tableau des commandes", level="auto", themename="journal", size="",
                        ):
        """Create a window in proper level"""

        def master_window_is_open() -> bool:
            if tk._default_root is None:
                return False  # Aucune fenêtre principale n'est ouverte
            elif tk._default_root.winfo_exists():
                return True  # Une fenêtre principale est déjà ouverte
            return False

        if level == "master" or (level == "auto" and not master_window_is_open()):
            window = ttk.Window(themename=themename)
        elif level == "toplevel" or (level == "auto" and master_window_is_open()):
            window = ttk.Toplevel()

            def close():
                window.quit()
                window.withdraw()

            window.protocol("WM_DELETE_WINDOW", close)
        else:
            logger.error(f"Window creation error: WRONG state ({level=}, {master_window_is_open()})")
            return
        logger.info(f"Window created: {level=} master state before: {master_window_is_open()}")

        window.title(title)
        window.geometry(size)
        return window
