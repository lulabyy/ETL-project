import logging
import os

def setupLogger(name="etl_logger", log_dir="log", log_filename="etl.log"):
    """
    Initialise le logger et écrit les logs dans le dossier spécifié (par défaut 'log').

    Parameters:
    ----------
    :param name: logger name
    :param log_dir: dir name
    :return: the logger
    """
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))

    full_log_dir = os.path.join(project_root, log_dir)
    os.makedirs(full_log_dir, exist_ok=True)

    log_file = os.path.join(full_log_dir, log_filename)

    # Création du logger si il existe pas déjà
    logger = logging.getLogger(name)
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
