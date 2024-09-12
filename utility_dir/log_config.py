import os.path
from logging import Filter

log_dir = "FinancesTracker/data/logs/errors.log"
config_dct = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
        },
        'short': {
            'format': '%(levelname)s - %(message)s',
        },
        'message': {
            'format': '%(message)s',
        },
        'debbuging': {
            'format': '%(module)-14s - %(levelname)-7s - %(funcName)-20s - Line%(lineno)4d - %(message)s',
        }
    },

    'filters': {
        'util_filter': {
            '()': 'utility_dir.log_config.UtilFilter',
        },
        'operation_info_filter': {
            '()': 'utility_dir.log_config.OperationFilter',
        },
    },

    'handlers': {
        'console_debug': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'debbuging',
        },
        'console_op': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'message',
            'filters': ['operation_info_filter']
        },
        'file_error': {
            'class': 'logging.FileHandler',
            'filename': f'{log_dir}',
            'level': 'ERROR',
            'formatter': 'standard',
        },
        'file_util': {
            'class': 'logging.FileHandler',
            'filename': f'{log_dir}',
            'level': 'INFO',
            'formatter': 'standard',
            'filters': ['util_filter'],
        },
        'file_op': {
            'class': 'logging.FileHandler',
            'filename': f'{log_dir}',
            'level': 'INFO',
            'formatter': 'short',
            'filters': ['operation_info_filter'],
        }
    },

    'loggers': {
        'main': {
            'handlers': ['file_error', 'file_util', 'console_op'],
            'level': 'INFO',
        },
        'debugging': {
            'handlers': ['console_debug'],
            'level': 'DEBUG',
        }
    },
}


# Précautions d'importation
self_path_from_main = "utility_dir/log_config"
directory_for_logs_files = log_dir
assert os.path.exists(log_dir), f"Le dossier {log_dir} n'existe pas ou n'est pas accessible."


# Filtres
class UtilFilter(Filter):
    def filter(self, record):
        return "UTIL" in record.getMessage()


class OperationFilter(Filter):
    def filter(self, record):
        if "OP" in record.getMessage():
            record.msg = record.msg.replace("OP-", "OP -> ", 1)
            return True
        return False
