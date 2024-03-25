# import packages

import pandas as pd
import os
import configparser


# FUNCTION: get neo4j connection credential from config file or default value
def get_credential():
    # Using an ini file for credentials, otherwise providing defaults
    HOST = 'neo4j://localhost'
    DATABASE = 'neo4j'
    PASSWORD = 'password'

    NEO4J_CONF_FILE = 'neo4j.ini'

    if NEO4J_CONF_FILE is not None and os.path.exists(NEO4J_CONF_FILE):
        config = configparser.RawConfigParser()
        config.read(NEO4J_CONF_FILE)
        HOST = config['NEO4J']['HOST']
        DATABASE = config['NEO4J']['DATABASE']
        PASSWORD = config['NEO4J']['PASSWORD']
        print('Using custom database properties')
    else:
        print('Could not find database properties file, using defaults')
    
    # Set the display format for float values, to avoid using scientific notation for big number
    pd.options.display.float_format = '{:.0f}'.format

    return HOST, DATABASE, PASSWORD


# FUNCTION: helper function run query using python driver with or without params
def run(driver, query, params=None):
    with driver.session() as session:
        if params is not None:
            return [r for r in session.run(query, params)]
        else:
            return [r for r in session.run(query)]