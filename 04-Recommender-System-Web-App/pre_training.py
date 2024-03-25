# import packages

import math
import pandas as pd
import warnings
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score

from py2neo import Graph
#from neo4j import GraphDatabase
from graphdatascience import GraphDataScience

from neo4j_tools import run
from neo4j_tools import get_credential


# filter warnings
warnings.filterwarnings("ignore")
#warnings.filterwarnings("ignore", message="DataFrame is highly fragmented.", category=UserWarning)
#warnings.filterwarnings("ignore", message="One of the relationship types in your query is not available in the database*", category=RuntimeWarning)

# define functions

# ## 2) Content-based Filtering Recommendations - Node Similarity
# duration: 6m
def algo_2_preparation(gds, graph):

    # Extract raw data of node poi and its attributes from GDS
    result = gds.run_cypher("""
    MATCH (poi:Poi)
    OPTIONAL MATCH (poi)-[:BELONGS_TO]->(category:Category)
    OPTIONAL MATCH (poi)-[:LOCATED_AT]->(region:Region)
    RETURN poi.id AS poi_id, 
        poi.name AS name, 
                            
        poi.description AS description, 

        poi.openingHours AS opening_hours, 
        poi.duration AS duration, 
        category.name AS category, 
        region.name AS region,
                            
        poi.price AS price, 
        poi.avgRating AS avg_rating, 
        poi.numReviews AS num_reviews, 
        poi.numReviews_5 AS num_reviews_5, 
        poi.numReviews_4 AS num_reviews_4, 
        poi.numReviews_3 AS num_reviews_3, 
        poi.numReviews_2 AS num_reviews_2, 
        poi.numReviews_1 AS num_reviews_1
    """)

    # Convert result to DataFrame
    df_pois = pd.DataFrame(result)

    # Extracting distinct poi_id and poi_name
    df_distinct_pois = df_pois.copy()
    df_distinct_pois = df_distinct_pois[['poi_id', 'name']].drop_duplicates()

    # Numerical Features - Min-Max Normalization
    # Attributes: 'price', 'avg_rating', 'num_reviews', 'num_reviews_5', 'num_reviews_4', 'num_reviews_3', 'num_reviews_2', 'num_reviews_1'

    scaler = MinMaxScaler()
    numerical_cols = ['price', 'avg_rating', 'num_reviews', 'num_reviews_5', 'num_reviews_4', 'num_reviews_3', 'num_reviews_2', 'num_reviews_1']
    # Create a new DataFrame with scaled columns and poi_id
    df_numerical_cols = df_pois.copy()
    df_numerical_cols = df_numerical_cols[['poi_id'] + numerical_cols]
    # retaining only distinct entries
    df_numerical_cols = df_numerical_cols.drop_duplicates()
    # Fill missing values in numerical columns with 0
    df_numerical_cols.fillna(0, inplace=True)

    # scale properties
    df_numerical_cols[numerical_cols] = scaler.fit_transform(df_numerical_cols[numerical_cols])


    # Categorical Features - One-hot Encoding
    # Attributes: category, region, opening_Hours, duration

    categorical_cols = ['category', 'region', 'opening_hours', 'duration']

    # Copy df_pois with only the specified categorical columns
    df_categorical_cols = df_pois.copy()
    df_categorical_cols = df_categorical_cols[['poi_id'] + categorical_cols]

    # Do one-hot encoding for categorical columns
    df_categorical_cols = pd.get_dummies(df_categorical_cols, columns=categorical_cols)


    # Merge rows with the same poi_id while applying OR logical operation
    df_categorical_cols = df_categorical_cols.groupby('poi_id').max().reset_index()


    # Textual Features - Token count
    # Attributes: description

    textual_cols = ['description']

    # Copy df_pois with only the specified textual columns
    df_cols = df_pois.copy()
    df_cols = df_cols[['poi_id'] + textual_cols]

    # retaining only distinct entries
    df_cols = df_cols.drop_duplicates()

    # create a mask to check if description column contains empty strings
    empty_description = df_cols['description'] == ''
    # Fill empty strings with "NULL"
    df_cols.loc[empty_description, 'description'] = 'NULL'

    # initialize token counter, ignore stop words
    count_vectorizer = CountVectorizer(stop_words="english")

    # Create an empty DataFrame to store token counts
    df_textual_cols = pd.DataFrame()

    # Iterate over each POI and its description
    for index, row in df_cols.iterrows():

        # Tokenize the description
        description = [row['description']]
        # print(f'description: {description}')
        
        # Count token and store in sparse matrix, then convert to dense matrix
        sparse_matrix = count_vectorizer.fit_transform(description)
        doc_term_matrix = sparse_matrix.todense()
        
        # Create DataFrame from the dense matrix
        df_token_counts = pd.DataFrame(
            doc_term_matrix,
            columns=count_vectorizer.get_feature_names_out(),
            index=[row['poi_id']]
        )
        
        # Append the DataFrame to df_token_counts
        df_textual_cols = pd.concat([df_textual_cols, df_token_counts])

    # fill NaN values with 0
    df_textual_cols.fillna(0, inplace=True)

    # Reset index, rename to poi_id
    df_textual_cols.reset_index(inplace=True)
    df_textual_cols = df_textual_cols.rename(columns={'index': 'poi_id'})
    


    # Compute pair-wise similarity between pois

    # Initialize similarity matrix
    similarity_matrix = {}

    # Calculate similarity for each pair of distinct POIs
    for i in range(len(df_distinct_pois)):
        for j in range(i+1, len(df_distinct_pois)):

            # get poi id in pairs

            poi1_id, poi2_id = df_distinct_pois.iloc[i]['poi_id'], df_distinct_pois.iloc[j]['poi_id']

            # Calculate Jaccard similarity for categorical attributes

            poi1_categorical_row = df_categorical_cols[df_categorical_cols['poi_id'] == poi1_id].iloc[:, 1:].values.flatten()
            poi2_categorical_row = df_categorical_cols[df_categorical_cols['poi_id'] == poi2_id].iloc[:, 1:].values.flatten()
            cat_cols_similarity = jaccard_score(poi1_categorical_row, poi2_categorical_row)

            # Calculate euclidean distance similarity for numerical attributes

            poi1_numerical_row = df_numerical_cols[df_numerical_cols['poi_id'] == poi1_id].iloc[:, 1:].values.flatten()
            poi2_numerical_row = df_numerical_cols[df_numerical_cols['poi_id'] == poi2_id].iloc[:, 1:].values.flatten()
            euclidean_distance = math.dist(poi1_numerical_row, poi2_numerical_row)
            num_cols_similarity = 1 / ( 1 + euclidean_distance )

            # Calculate cosine similarity for textual attributes

            poi1_textual_row = df_textual_cols[df_textual_cols['poi_id'] == poi1_id].iloc[:, 1:].values.flatten()
            poi2_textual_row = df_textual_cols[df_textual_cols['poi_id'] == poi2_id].iloc[:, 1:].values.flatten()
            text_cols_similarity = cosine_similarity([poi1_textual_row, poi2_textual_row])[0][1]

            # Compute weighted overall similarity

            num_cat_cols = len(categorical_cols)
            num_num_cols = len(numerical_cols)
            num_text_cols = len(textual_cols)
            similarity = ( num_cat_cols * cat_cols_similarity + num_num_cols * num_cols_similarity + num_text_cols * text_cols_similarity ) / ( num_cat_cols + num_num_cols + num_text_cols )
            
            # Store similarity in the matrix
            similarity_matrix[(poi1_id, poi2_id)] = similarity

    # Convert similarity matrix to DataFrame
    df_similarity = pd.DataFrame(similarity_matrix.items(), columns=['POI Pair', 'Similarity'])
    # Drop rows where Similarity is less than 0.5
    df_similarity = df_similarity[df_similarity['Similarity'] >= 0.5]
    # Split the 'POI Pair' column into two separate columns
    df_similarity[['poi1_id', 'poi2_id']] = pd.DataFrame(df_similarity['POI Pair'].tolist(), index=df_similarity.index)
    # Drop the original 'POI Pair' column
    df_similarity.drop(columns=['POI Pair'], inplace=True)
    # Reorder the columns
    df_similarity = df_similarity[['poi1_id', 'poi2_id', 'Similarity']]
    # Reorder the DataFrame by the column "Similarity"
    df_similarity = df_similarity.sort_values(by='Similarity', ascending=False)
    # Reindex the DataFrame
    df_similarity = df_similarity.reset_index(drop=True)


    # write SIMILAR relationship between pois with property similarity
    # duration: 5m

    # Iterate over the DataFrame rows and write the relationships to Neo4j
    for index, row in df_similarity.iterrows():
        poi1_id = row['poi1_id']
        poi2_id = row['poi2_id']
        similarity = row['Similarity']
        
        # Write undirected relationship between poi1_id and poi2_id with similarity property
        query = f"""
        MATCH (poi1:Poi {{id: {poi1_id}}})
        MATCH (poi2:Poi {{id: {poi2_id}}})
        MERGE (poi1)-[s1:CBF_SIMILAR]->(poi2)
        ON CREATE SET s1.score = {similarity}
        MERGE (poi1)<-[s2:CBF_SIMILAR]-(poi2)
        ON CREATE SET s2.score = {similarity}
        """
        # using py2neo to write dataframe back to neo4j
        graph.run(query)

    return


## 3) Collaborative Filtering Recommendations - User-Based kNN based on FastRP embeddings

def algo_3_4_preparation(gds):

    # Projection Graph
    # duration: 20s

    # define how to project database into GDS
    node_projection = ["User", "Poi"]
    relationship_projection = {"REVIEWED": {"orientation": "UNDIRECTED", "properties": "rating"}}

    # proceed with projection
    G, result = gds.graph.project("myGraph", node_projection, relationship_projection)


    # Create Fast RP embeddings

    # run FastRP and mutate our projected graph with the results
    result = gds.fastRP.mutate(
        G,
        randomSeed=42,
        embeddingDimension=256,
        relationshipWeightProperty="rating",
        iterationWeights=[0, 1, 1, 1],
        mutateProperty="embedding"
    )

    #print(f"Number of embedding vectors produced: {result['nodePropertiesWritten']}")

    # Similarity with User-based KNN

    # Run the kNN with optimal topK hyperparameter and write back to db
    # duration: 3m

    topK_best = 12

    result = gds.knn.write(
        G,
        topK=topK_best,
        nodeLabels=['User'],
        nodeProperties=["embedding"],
        randomSeed=42,
        concurrency=1,
        sampleRate=1.0,
        deltaThreshold=0.0,
        writeRelationshipType="CF_SIMILAR_USER",
        writeProperty="score",

    )

    #print(f"Relationships produced: {result['relationshipsWritten']}")
    #print(f"Nodes compared: {result['nodesCompared']}")
    #print(f"Mean similarity: {result['similarityDistribution']['mean']}")


    # Similarity with Item-based KNN

    # Run the kNN with optimal topK hyperparameter and write back to db

    topK_best = 2

    result = gds.knn.write(
        G,
        topK=topK_best,
        nodeLabels = ['Poi'],
        nodeProperties=["embedding"],
        randomSeed=42,
        concurrency=1,
        sampleRate=1.0,
        deltaThreshold=0.0,
        similarityCutoff = 0.5,
        writeRelationshipType="CF_SIMILAR_POI",
        writeProperty="score"
    )

    #print(f"Relationships produced: {result['relationshipsWritten']}")
    #print(f"Nodes compared: {result['nodesCompared']}")
    #print(f"Mean similarity: {result['similarityDistribution']['mean']}")

    # Remove our projection from the GDS graph catalog
    G.drop()

    

    return



# FUNCTION: preparation for making recommendation
def pre_training(gds):

    # algorithm 2 preparation
    if gds.run_cypher("""MATCH ()-[r:CBF_SIMILAR]->() RETURN r LIMIT 10""").empty:

        print("algo_2_preparation starts...")

        # neo4j connections

        # Get credentials to connect neo4j
        HOST, DATABASE, PASSWORD = get_credential()

        # Connect using py2neo
        graph = Graph(HOST, auth=(DATABASE, PASSWORD))

        algo_2_preparation(gds, graph)

        print("algo_2_preparation done.")

    else:
        print("Algo 2 was already prepared.")

    # algorithm 3 4 preparation
    if gds.run_cypher("""MATCH ()-[r:CF_SIMILAR_POI]->() RETURN r LIMIT 10""").empty:

        print("algo_3_4_preparation starts...")

        algo_3_4_preparation(gds)

        print("algo_3_4_preparation done.")

    else:
        print("Algo 3 & 4 was already prepared.")

    return

    

# entry point
if __name__ == '__main__':

    # Get credentials to connect neo4j
    HOST, DATABASE, PASSWORD = get_credential()
    
    # Connect using GDS library
    gds = GraphDataScience(HOST,auth=(DATABASE, PASSWORD))

    pre_training()

        # Close the connection created using GDS library
    gds.close()