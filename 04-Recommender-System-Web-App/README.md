
# 04 Recommender System Web Application

This module encompasses the code for a web application designed to showcase the integration of a knowledge graph-based recommender engine with a user-friendly web interface.

## Introduction

It consists of several Python scripts:

### app.py
This script serves as the core of the web application. It utilizes Flask for web development and integrates with Neo4j for database operations. 

### data_loader.py

This script facilitates the loading of data into the Neo4j database. It defines constants for CSV file URLs, and provides functions for setting constraints, loading nodes, loading relationships, and performing data loading into the Neo4j database.

### pre_training.py
This script encompasses the preparation steps for recommendation algorithms, focusing on content-based filtering and collaborative filtering. It starts by data manipulation, machine learning, and Neo4j interactions. 

### recommender.py
This script defines several recommendation algorithms implemented using Neo4j and the Graph Data Science library. The script includes a testing section where you can specify a user ID and/or a POI ID to receive recommendations.

### neo4j_tools.py
This script contains functions to handle Neo4j database connections and queries,providing a convenient way to manage Neo4j connection credentials and execute queries using Python.

## Usage

To set up the web application locally, follow these steps:

1. Ensure that Python and the required dependencies are installed.
2. Save the credentials required to connect to the Neo4j database in a file named neo4j.ini and place in the root directory of this module. 
Sample neo4j.ini File:
`[NEO4J]
HOST = bolt://[IP]:[PORT]
DATABASE = neo4j
PASSWORD = [PASSWORD]`
3. Run the `app.py`
4. Upon initializing the web application and verifying that the Neo4j database is empty, it may require approximately 5 to 10 minutes to load the data into the Neo4j database before launching the web application.

## Dependencies

- Python 3.x
- Flask
- neo4j
- graphdatascience
- pandas
- scikit-learn
- py2neo

## Contributors

Xiong Ying

## License

This project is licensed under the [MIT License](LICENSE).