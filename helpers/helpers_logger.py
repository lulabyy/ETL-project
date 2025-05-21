import logging
import os

def initLogger(log_name: str, log_dir_path: str, log_filename: str):
    """
    Initialise le logger et écrit les logs dans le dossier spécifié (par défaut 'log').

    Parameters:
    ----------
    :param name: logger name
    :param log_dir_path: dir path
    :param log_filename: filename path
    :return: the logger
    """
    os.makedirs(log_dir_path, exist_ok=True)

    log_file = os.path.join(log_dir_path, log_filename)

    # Création du logger si il existe pas déjà
    logger = logging.getLogger(log_name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(module)s | %(funcName)s | %(lineno)d | %(message)s"
        )

        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
