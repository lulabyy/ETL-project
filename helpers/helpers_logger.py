import logging

def setupLogger():
    # The log allows tracking the execution of the code
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(name)s | %(levelname)s | %(module)s | %(filename)s | %(funcName)s | %(lineno)d | %(message)s",
        handlers=[
            logging.StreamHandler(),  # Display the log in the console
            logging.FileHandler("etl.log"),  # Write the log in a file
        ],
    )

    # Création du logger
    logger = logging.getLogger("etl_logger")
    logging.getLogger("sqlalchemy.engine.Engine").disabled = True


