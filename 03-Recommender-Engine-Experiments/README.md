
# 03 Recommender Engine - Algorithm Experiments and Evaluation
This directory contains Jupyter notebooks for developing and evaluating recommendation algorithms tasks related to the project.

## Introduction

It consists of several Jupyter Notebooks:

### 01 cc-heuristic.ipynb

This notebook explores the Content-Based Filtering (CC) heuristic approach for recommendation systems. It delves into the fundamental concepts and implementation details of the heuristic-based recommendation approach.

### 02 cc-node similarity.ipynb

This notebook investigates the utilization of node similarity metrics in Content-Based Filtering (CC) recommendation. It explores various node similarity measures and their impact on the effectiveness of the recommendation algorithm.

### 03 cf-userKnn fastRP.ipynb

In this notebook, the Collaborative Filtering (CF) approach with User-Based K-Nearest Neighbors (KNN) and Fast Random Projection (FastRP) techniques is explored. It examines the combination of user-based similarity and dimensionality reduction methods for enhancing recommendation performance.

### 04 cf-itemKnn fastRP.ipynb

Similar to the previous notebook, this one focuses on the Collaborative Filtering (CF) method but employs Item-Based K-Nearest Neighbors (KNN) and Fast Random Projection (FastRP) techniques. It analyzes how item-based similarity and dimensionality reduction can improve the accuracy and efficiency of recommendation systems.

### 05 ensemble - max voting.ipynb

This notebook explores ensemble techniques, specifically the Majority Voting method, for combining the predictions of multiple recommendation models. It investigates how ensemble learning can enhance recommendation performance by aggregating the outputs of individual models.

## Usage

Follow these steps:

1. Ensure that Python and the required dependencies are installed.
2. Save the credentials required to connect to the Neo4j database in a file named neo4j.ini and place in the root directory of this module. 
Sample neo4j.ini File:
`[NEO4J]
HOST = bolt://[IP]:[PORT]
DATABASE = neo4j
PASSWORD = [PASSWORD]`
2. Run the desired notebook.

## Dependencies

- Python 3.x
- neo4j
- pandas
- scikit-learn
- matplotlib
- py2neo
- graphdatascience

## Contributors

Xiong Ying

## License

This project is licensed under the [MIT License](LICENSE).