import textwrap
import pandas as pd

from neo4j import GraphDatabase
from graphdatascience import GraphDataScience

from neo4j_tools import run
from neo4j_tools import get_credential

# Algo 1 Content Based Filtering Recommendations - Heuristic Method

# FUNCTION: make recommendation based on Content Based Filtering Recommendations - Heuristic Method
# INPUT: poi_id
# OUTPUT: dataframe[poi_id, rec_poi_id]

def heuristic_recommendation(gds, poi_id):
    # get pois in the same region as reviewed_poi by the user
    df_records_region = gds.run_cypher("""
        MATCH (poi:Poi {id: $poi_id})-[:LOCATED_AT]->(region:Region)<-[:LOCATED_AT]-(other_poi:Poi)
        WHERE poi <> other_poi
        WITH poi, other_poi, region
        RETURN poi.id AS poi_id, other_poi.id AS rec_poi_id, region.name AS region, other_poi.numReviews AS occurrences
        """, params = {'poi_id': poi_id})

    # get pois in the same category as reviewed_poi by the user 
    df_records_category = gds.run_cypher("""
        MATCH (poi:Poi {id: $poi_id})-[:BELONGS_TO]->(category:Category)<-[:BELONGS_TO]-(other_poi:Poi)
        WHERE poi <> other_poi
        WITH poi, other_poi, category
        RETURN poi.id AS poi_id, other_poi.id AS rec_poi_id, category.name AS category_name, other_poi.numReviews AS occurrences
        """, params = {'poi_id': poi_id})
    
    # Convert the result to a DataFrame
    if not df_records_region.empty:
        # Group by 'poi_id', 'poi_name', and 'occurrences', then aggregate the count of occurrences
        df_records_region_agg = df_records_region.groupby(['poi_id', 'rec_poi_id', 'occurrences']).size().reset_index(name='weight')
    else:
        df_records_region_agg = pd.DataFrame(columns=['poi_id', 'rec_poi_id', 'occurrences', 'weight'])

    if not df_records_category.empty:
        # Group by 'poi_id', 'poi_name', and 'occurrences', then aggregate the count of occurrences
        df_records_category_agg = df_records_category.groupby(['poi_id', 'rec_poi_id', 'occurrences']).size().reset_index(name='weight')
    else:
       df_records_category_agg = pd.DataFrame(columns=['poi_id', 'rec_poi_id', 'occurrences', 'weight'])


    # compute appearance fequency of pois in both lists

    # Merge the two DataFrames on 'rec_poi_id'
    recommended_interactions = pd.merge(df_records_region_agg, df_records_category_agg, on='rec_poi_id', suffixes=('_region', '_category'), how='outer')

    # Fill NaN values in '_region' columns with values from '_category' columns
    recommended_interactions['poi_id_region'].fillna(recommended_interactions['poi_id_category'], inplace=True)
    recommended_interactions['occurrences_region'].fillna(recommended_interactions['occurrences_category'], inplace=True)

    # Rename the columns '_region'
    recommended_interactions.rename(columns={'poi_id_region': 'poi_id'}, inplace=True)
    recommended_interactions.rename(columns={'occurrences_region': 'occurrences'}, inplace=True)

    # Fill NaN values with 0 for the 'weight' columns
    recommended_interactions['weight_region'].fillna(0, inplace=True)
    recommended_interactions['weight_category'].fillna(0, inplace=True)
    # Sum the 'weight' columns to get the total weight
    recommended_interactions['total_weight'] = recommended_interactions['weight_region'] + recommended_interactions['weight_category']

    # Drop the individual 'weight' columns if needed
    recommended_interactions.drop(['poi_id_category', 'occurrences_category', 'weight_region', 'weight_category'], axis=1, inplace=True)
    # Order the DataFrame by 'total_weight' in descending order, then by 'occurrences'
    recommended_interactions = recommended_interactions.sort_values(by=['total_weight', 'occurrences'], ascending=[False, False])
    # Reindex the DataFrame
    recommended_interactions.reset_index(drop=True, inplace=True)
    # Rearrange the columns
    recommended_interactions = recommended_interactions[['poi_id', 'rec_poi_id']]
    # drop duplicate
    recommended_interactions = recommended_interactions.drop_duplicates()

    # Display the merged DataFrame
    return recommended_interactions



# Algo 2 Content Based Filtering Recommendations - Node Similarity

# FUNCTION: make recommendation based on Content Based Filtering Recommendations - Node Similarity
# INPUT: poi_id
# OUTPUT: dataframe[poi_id, rec_poi_id]

def similar_poi_recommendation(gds, poi_id):
    result = gds.run_cypher(
        """
            MATCH (p1:Poi {id: $target_poi})-[s:CBF_SIMILAR]->(p2:Poi)
            RETURN p1.id as poi_id, p2.id as rec_poi_id
            ORDER BY s.score DESC
        """, params = {'target_poi': poi_id}
    )
    result = result.drop_duplicates()
    return result


# Algo 3 Collaborative Filtering Recommendations - User-Based

# FUNCTION: make recommendation based on Collaborative Filtering Recommendations - User-Based kNN based on FastRP embeddings
# INPUT: user_id
# OUTPUT: dataframe[user_id, rec_poi_id]

def userKNN_recommendation(gds, user_id):

    result = gds.run_cypher(
        """
            MATCH (u1:User {id: $target_user})-[s:CF_SIMILAR_USER]->(u2:User)-[:REVIEWED]->(p:Poi)
            WITH u1, p, s.score AS user_similarity
            RETURN u1.id as user_id, p.id as rec_poi_id
            ORDER BY user_similarity DESC, p.avgRating DESC
        """, params = {'target_user': user_id}
    )
    result = result.drop_duplicates()
    return result


# Algo 4 Collaborative Filtering Recommendations - Item-Based kNN

# FUNCTION: make recommendation based on Collaborative Filtering Recommendations - Item-Based kNN based on FastRP embeddings
# INPUT: poi_id
# OUTPUT: dataframe[poi_id, rec_poi_id]

def itemKNN_recommendation(gds, poi_id):
    result = gds.run_cypher(
        """
            MATCH (p1:Poi {id: $target_poi})-[s:CF_SIMILAR_POI]->(p2:Poi)
            RETURN p1.id as poi_id, p2.id as rec_poi_id
            ORDER BY s.score DESC, p2.avgRating DESC
        """, params = {'target_poi': poi_id}
    )
    result = result.drop_duplicates()
    return result



# Helper function for ensemble learning
# FUNCTION: helper to cleaning up each df after calling recommendation algorithm, prepare them for ensemble learning
def df_cleaning (df):
    if not df.empty:    # Reset index, get rank, and re-arrange columns
        df.reset_index(drop=True, inplace=True)          
        df = df.reset_index().rename(columns={'index': 'rank'})
        df['rank'] += 1
        df = df.reindex(columns=['user_id', 'poi_id', 'rec_poi_id', 'rank', 'df_name'])

    return df


# FUNCTION: make recommendation based on Ensemble Learning - Majority Voting
# INPUT: poi_id, user_id, algo_combination
# OUTPUT: dataframe[poi_id, user_id, rec_poi_id]

def ensemble_recommendation(gds, poi_id, user_id, algo_combination):

    # Based on the chosen algorithm combination, decide whether to call each recommendation function
    if 1 in algo_combination:  
        rec_CBF_heuristic = heuristic_recommendation(gds, poi_id)            # OUTPUT: dataframe[poi_id, rec_poi_id]
        rec_CBF_heuristic['df_name'] = 'rec_CBF_heuristic'              # Add DataFrame name as a column
        rec_CBF_heuristic['user_id'] = user_id                          # Add missing column
        rec_CBF_heuristic = df_cleaning (rec_CBF_heuristic)             # Clean up df for ensemble
    else:
        rec_CBF_heuristic = pd.DataFrame()

    if 2 in algo_combination:
        rec_CBF_similarity = similar_poi_recommendation(gds, poi_id)         # OUTPUT: dataframe[poi_id, rec_poi_id]
        rec_CBF_similarity['df_name'] = 'rec_CBF_similarity'            # Add DataFrame name as a column
        rec_CBF_similarity['user_id'] = user_id                         # Add missing columns
        rec_CBF_similarity = df_cleaning (rec_CBF_similarity)           # Clean up df for ensemble
    else:
        rec_CBF_similarity = pd.DataFrame()

    if 3 in algo_combination:
        rec_CF_userKnn =  userKNN_recommendation(gds, user_id)               # OUTPUT: dataframe[user_id, rec_poi_id]
        rec_CF_userKnn['df_name'] = 'rec_CF_userKnn'                    # Add DataFrame name as a column
        rec_CF_userKnn['poi_id'] = poi_id                               # Add missing columns
        rec_CF_userKnn = df_cleaning (rec_CF_userKnn)                   # Clean up df for ensemble
    else:
        rec_CF_userKnn = pd.DataFrame()

    if 4 in algo_combination:
        rec_CF_itemKnn = itemKNN_recommendation(gds, poi_id)                 # OUTPUT: dataframe[poi_id, rec_poi_id]
        rec_CF_itemKnn['df_name'] = 'rec_CF_itemKnn'                    # Add DataFrame name as a column
        rec_CF_itemKnn['user_id'] = user_id                             # Add missing columns
        rec_CF_itemKnn = df_cleaning (rec_CF_itemKnn)                   # Clean up df for ensemble
    else:
        rec_CF_itemKnn = pd.DataFrame()
    
    # Concatenate the DataFrames along the rows
    merged_df = pd.concat([rec_CF_itemKnn, rec_CF_userKnn, rec_CBF_similarity, rec_CBF_heuristic])
    #print(f'merged_df: \n{merged_df}')

    # check if merged df is not empty
    if not merged_df.empty:
        # Group by user_id, poi_id, rec_poi_id and compute average rank and count
        grouped_df = merged_df.groupby(['user_id', 'poi_id', 'rec_poi_id']).agg({'rank': 'mean', 'df_name': 'count'}).reset_index()

        # Rename the count column to count
        grouped_df.rename(columns={'df_name': 'count'}, inplace=True)

        # drop any item with count = 1
        grouped_df = grouped_df[grouped_df['count'] > 1]

        # Sort by count in descending order and average rank in ascending order
        sorted_df = grouped_df.sort_values(by=['count', 'rank'], ascending=[False, True])
        #print(f'sorted_df: \n{sorted_df}')

        # Drop the 'count' and 'rank' columns
        result = sorted_df.drop(columns=['count', 'rank'])
        #result = sorted_df.copy()
        result.reset_index(drop=True, inplace=True)
    else:
        result = merged_df.drop(columns=['df_name'])

    return result


# FUNCTION: find the poi that the user has reviewed 
def reviewed_poi(gds, user_id):
    df_reviewed_poi = gds.run_cypher("""
        MATCH (user:User {id: $user_id})-[:REVIEWED]->(poi:Poi)
        RETURN poi.id AS reviewed_poi_id
        """, params = {'user_id': user_id})
    # Extract reviewed POI IDs from the DataFrame
    reviewed_poi_ids = df_reviewed_poi['reviewed_poi_id'].tolist()
    return reviewed_poi_ids

'''
# FUNCTION: get recommendations
def recommend(gds, poi_id=0, user_id=0):

    # if user id is available, find pois that the user has reviewed, exclude these from result
    reviewed = reviewed_poi(gds, user_id) if user_id else []

    # when both user_id and poi_id, use ensemble1234
    if poi_id and user_id:

        # combination of algorithm for ensemble learning
        algo_combination = [1,2,3,4]

        #(1) Content Based Filtering - Heuristic            #heuristic_recommendation(poi_id)
        #(2) Content Based Filtering - Node Similarity      #similar_poi_recommendation(poi_id)
        #(3) Collaborative Filtering - UserKnn with FastRP  #userKNN_recommendation(user_id)
        #(4) Collaborative Filtering - ItemKnn with FastRP  #itemKNN_recommendation(poi_id)

        result = ensemble_recommendation(gds, poi_id, user_id, algo_combination)['rec_poi_id'].tolist()  # ensemble
        #result = ensemble_recommendation(gds, poi_id, user_id, algo_combination)  # ensemble
        # exclude reviewed poi by user
        #result = result[~result['rec_poi_id'].isin(reviewed)]
        result = list(filter(lambda x: x not in reviewed, result))

        # BACKUP PLAN
        # if result is emtpy, use algo3, algo2, algo4, algo1 by sequence
        if len(result)==0:
            result = userKNN_recommendation(gds, user_id)['rec_poi_id'].tolist()                 # algo 3
            # exclude reviewed poi by user
            result = list(filter(lambda x: x not in reviewed, result))

            if len(result)==0:
                result = similar_poi_recommendation(gds, poi_id)['rec_poi_id'].tolist()          # algo 2

                if len(result)==0:
                    result = itemKNN_recommendation(gds, poi_id)['rec_poi_id'].tolist()          # algo 4

                    if len(result)==0:
                        result = heuristic_recommendation(gds, poi_id)['rec_poi_id'].tolist()    # algo 1

        
    # when only user_id, use algo3, which is the only available algo in this case
    elif user_id and (poi_id == 0):
        
        result = userKNN_recommendation(gds, user_id)['rec_poi_id'].tolist()     # algo 3
        # exclude reviewed poi by user
        result = list(filter(lambda x: x not in reviewed, result))
    
    # when only poi_id, use algo2
    elif poi_id and (user_id == 0):

        result = similar_poi_recommendation(gds, poi_id)['rec_poi_id'].tolist()  # algo 2

        # if algo2 result is emtpy, use algo 4, algo 1
        if len(result)==0:
            result = itemKNN_recommendation(gds, poi_id)['rec_poi_id'].tolist()  # algo 4

            if len(result)==0:
                result = heuristic_recommendation(gds, poi_id)['rec_poi_id'].tolist()    # algo 1
    
    # else just return empty
    else:
        result = []
        print("No recommendation.")

    # get poi name and id
    df_result = gds.run_cypher(
    """
    MATCH (p:Poi)
    WHERE p.id IN $poi_ids
    RETURN p.id AS id, p.name AS name
    """,
    params={'poi_ids': result})
    list_result = df_result.to_dict(orient='records')

    # return a list of recommended poi IDs
    return list_result
'''


# FUNCTION: from a list of poi ids, get poi name, save poi {id,name} in a list
def get_poi_name(gds, poi_ids):
    # get poi name and id
    df_result = gds.run_cypher(
    """
    MATCH (p:Poi)
    WHERE p.id IN $poi_ids
    RETURN p.id AS id, p.name AS name
    """,
    params={'poi_ids': poi_ids})
    result_list = df_result.to_dict(orient='records')
    print(f"Recommendations: {result_list}")

    return result_list


# FUNCTION: get recommendations
def get_rec_poi_id(gds, poi_id=0, user_id=0, n=10):

    # if user id is available, find pois that the user has reviewed, exclude these from result
    reviewed = reviewed_poi(gds, user_id) if user_id else []
    print(f'reviewed: {reviewed}')

    # initialize a result list
    result = []

    # only when both poi_id and user_id exist, get recommendation from ensemble with algo 1234
    if poi_id and user_id:

        try:
            algo_combination = [1,2,3,4]
            #(1) Content Based Filtering - Heuristic            #heuristic_recommendation(poi_id)
            #(2) Content Based Filtering - Node Similarity      #similar_poi_recommendation(poi_id)
            #(3) Collaborative Filtering - UserKnn with FastRP  #userKNN_recommendation(user_id)
            #(4) Collaborative Filtering - ItemKnn with FastRP  #itemKNN_recommendation(poi_id)

            result_ensemble = ensemble_recommendation(gds, poi_id, user_id, algo_combination)['rec_poi_id'].tolist()  # ensemble

            # Remove items that also appear in the reviewed list
            result_ensemble = list(filter(lambda x: x not in reviewed, result_ensemble))

            # Append to result, check item uniqueness
            for item in result_ensemble:
                if item not in result:
                    result.append(item)
            
            print(f'result from ensemble1234: {result_ensemble}')
        except: # When either parameter not available
            #result_ensemble = []  # Set result to an empty list
            print(f'Ensemble learning is not applicable.')

        # if already have more than n result, return the first n, to skip the computing for other algo
        if len(result) >= n:
            return result[:n]   

    # only when user_id exist, get recommendation from algo 3
    if user_id:

        try:
            result_algo3 = userKNN_recommendation(gds, user_id)['rec_poi_id'].tolist()

            # Remove items that also appear in the reviewed list
            result_algo3 = list(filter(lambda x: x not in reviewed, result_algo3))

            # Append to result, check item uniqueness
            for item in result_algo3:
                if item not in result:
                    result.append(item)

            print(f'result from algo3: {result_algo3}')
        except:
            #result_algo3 = []
            print(f'Algorithm 3 is not applicable.')

        
        # check if can return
        if len(result) >= n:
            return result[:n]

    # only when poi_id exist, get recommendation from algo 2
    if poi_id:

        try:
            result_algo2 = similar_poi_recommendation(gds, poi_id)['rec_poi_id'].tolist()

            # Remove items that also appear in the reviewed list
            result_algo2 = list(filter(lambda x: x not in reviewed, result_algo2))

            # Append to result, check item uniqueness
            for item in result_algo2:
                if item not in result:
                    result.append(item)
                
            print(f'result from algo2: {result_algo2}')
        except:
            #result_algo2 = []
            print(f'Algorithm 2 is not applicable.')

        # check if can return
        if len(result) >= n:
            return result[:n]

    # only when poi_id exist, get recommendation from algo 4
    if poi_id:

        try:
            result_algo4 = itemKNN_recommendation(gds, poi_id)['rec_poi_id'].tolist()

            # Remove items that also appear in the reviewed list
            result_algo4 = list(filter(lambda x: x not in reviewed, result_algo4))

            # Append to result, check item uniqueness
            for item in result_algo4:
                if item not in result:
                    result.append(item)
            
            print(f'result from algo4: {result_algo4}')
        except:
            # result_algo4 = []
            print(f'Algorithm 4 is not applicable.')
    
        # check if can return
        if len(result) >= n:
            return result[:n]
        
    # only when poi_id exist, get recommendation from algo 1
    if poi_id:

        try:
            result_algo1 = heuristic_recommendation(gds, poi_id)['rec_poi_id'].tolist()

            # Remove items that also appear in the reviewed list
            result_algo1 = list(filter(lambda x: x not in reviewed, result_algo1))

            # Append to result, check item uniqueness
            for item in result_algo1:
                if item not in result:
                    result.append(item)
            
            print(f'result from algo1: {result_algo1}')
        except:
            #result_algo1 = []
            print(f'Algorithm 1 is not applicable.')

    # return the first n
    return result[:n]
    

# FUNCTION: get recommendations
def recommend(gds, poi_id=0, user_id=0):

    # get a list of recommended poi ids, with at most n instances
    rec_poi_ids = get_rec_poi_id(gds, poi_id, user_id, n=10)

    # get poi id and name in list
    poi_id_name = get_poi_name(gds, rec_poi_ids)

    # return a list of recommended poi ID and name
    return poi_id_name


# entry point
if __name__ == '__main__':

    # neo4j connection

    # Get credentials to connect neo4j
    HOST, DATABASE, PASSWORD = get_credential()

    # create neo4j Python driver
    driver = GraphDatabase.driver(HOST, auth=(DATABASE, PASSWORD))

    # Connect using GDS library
    gds = GraphDataScience(HOST,auth=(DATABASE, PASSWORD))

    # testing

    # target user's id
    user_id = 3098 # reviewed: 34 pois, UserKNN recommendation: [1888873, 317421, 317473, 678639, 2138910]
    user_id = 433  # reviewed: 5 pois [1888873, 1888876, 4400781, 310900, 2149128], UserKNN recommendation: [8016698, 317415]
    user_id = 6 # reviewed: 1 poi, UserKNN recommendation: []
    #user_id = 0 # simulate when user_id not available

    # target poi's id
    poi_id = 2149128
    # poi_id = 0 # simulate when poi_id not available

    # Make recommendations
    print(recommend(gds, poi_id=poi_id, user_id=user_id))