# import packages

from neo4j import GraphDatabase
import textwrap

from neo4j_tools import run
from neo4j_tools import get_credential

# define constants

# import .csv files are hostsed on Github for easier access
url_node_category = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_category.csv'

url_node_origin = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_origin.csv'

url_node_poi = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_poi.csv'

url_node_region = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_region.csv'

url_node_review_1 = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_review_1.csv'

url_node_review_2 = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_review_2.csv'

url_node_user = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_node_user.csv'

url_poi_belongsto_category = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_poi_belongsto_category.csv'

url_poi_locatedat_region = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_poi_locatedat_region.csv'

url_user_from_origin = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_user_from_origin.csv'

url_user_reviewed_poi = 'https://raw.githubusercontent.com/xiong-ying/KG-Rec-Sys-Tourism-SG/main/02-Data-Preprocessing-EDA/neo4j_import/df_user_reviewed_poi.csv'


# define functions


# FUNCTION: set constraint for primary key in graph database
def set_constrain(driver):

    run(driver,'CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (user:User) REQUIRE user.id IS UNIQUE')
    run(driver,'CREATE CONSTRAINT origin_id_unique IF NOT EXISTS FOR (origin:Origin) REQUIRE origin.id IS UNIQUE')
    run(driver,'CREATE CONSTRAINT poi_id_unique IF NOT EXISTS FOR (poi:Poi) REQUIRE poi.id IS UNIQUE')
    run(driver,'CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (category:Category) REQUIRE category.id IS UNIQUE')
    run(driver,'CREATE CONSTRAINT region_id_unique IF NOT EXISTS FOR (region:Region) REQUIRE region.id IS UNIQUE')
    run(driver,'CREATE CONSTRAINT review_id_unique IF NOT EXISTS FOR (review:Review) REQUIRE review.id IS UNIQUE')
    return


# FUNCTION: load nodes
def nodes_loader(driver):

    # df_node_category
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE(category:Category {id: toInteger(row.id), name: row.name})
        RETURN count(category)
        """),
        params = {'file': url_node_category}
    )

    # df_node_origin
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE(origin:Origin {id: toInteger(row.id), name: row.name})
        RETURN count(origin)
        """),
        params = {'file': url_node_origin}
    )

    #df_node_poi
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE (poi:Poi {id: toInteger(row.id)})
        ON CREATE SET
            poi.name = coalesce(row.name, ''),
            poi.description = coalesce(row.description, ''),
            poi.url = coalesce(row.url, ''),
            poi.openingHours = coalesce(row.openingHours, ''),
            poi.duration = coalesce(row.duration, ''),
            poi.price = toFloat(coalesce(row.price, '0.0')),
            poi.address = coalesce(row.address, ''),
            poi.avgRating = toFloat(coalesce(row.avgRating, '0.0')),
            poi.numReviews = toInteger(coalesce(row.numReviews, '0')),
            poi.numReviews_5 = toInteger(coalesce(row.numReviews_5, '0')),
            poi.numReviews_4 = toInteger(coalesce(row.numReviews_4, '0')),
            poi.numReviews_3 = toInteger(coalesce(row.numReviews_3, '0')),
            poi.numReviews_2 = toInteger(coalesce(row.numReviews_2, '0')),
            poi.numReviews_1 = toInteger(coalesce(row.numReviews_1, '0'))
        RETURN count(poi)
        """),
        params = {'file': url_node_poi}
    )

    # df_node_region
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE(region:Region {id: toInteger(row.id), name: row.name})
        RETURN count(region)
        """),
        params = {'file': url_node_region}
    )

    #df_node_review_1
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE (review:Review {id: toInteger(row.id)})
        ON CREATE SET
            review.title = coalesce(row.title, ''),
            review.date = date(coalesce(row.date, '')),
                    review.rating = toFloat(coalesce(row.rating, '0.0')),
                    review.content = coalesce(row.content, '')
        RETURN count(review)
        """),
        params = {'file': url_node_review_1}
    )

    #df_node_review_2
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE (review:Review {id: toInteger(row.id)})
        ON CREATE SET
            review.title = coalesce(row.title, ''),
            review.date = date(coalesce(row.date, '')),
                    review.rating = toFloat(coalesce(row.rating, '0.0')),
                    review.content = coalesce(row.content, '')
        RETURN count(review)
        """),
        params = {'file': url_node_review_2}
    )

    # df_node_user
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MERGE(user:User {id: toInteger(row.id), name: row.name})
        RETURN count(user)
        """),
        params = {'file': url_node_user}
    )

    return


# FUNCTION: load relationships
def relationships_loader(driver):
    # df_poi_belongsto_category
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MATCH (poi:Poi {id: toInteger(row.poi_id)})
        MATCH (category:Category {id: toInteger(row.category_id)})
        MERGE (poi)-[r:BELONGS_TO]->(category)
        RETURN count(r) AS BELONGS_TO_count
        """),
        params = {'file': url_poi_belongsto_category}
    )

    # df_poi_locatedat_region
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MATCH (poi:Poi {id: toInteger(row.poi_id)})
        MATCH (region:Region {id: toInteger(row.region_id)})
        MERGE (poi)-[r:LOCATED_AT]->(region)
        RETURN count(r) AS LOCATED_AT_count
        """),
        params = {'file': url_poi_locatedat_region}
    )

    # df_user_from_origin
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        MATCH (user:User {id: toInteger(row.user_id)})
        MATCH (origin:Origin {id: toInteger(row.origin_id)})
        MERGE (user)-[r:FROM]->(origin)
        RETURN count(r) AS FROM_count
        """),
        params = {'file': url_user_from_origin}
    )

    # df_user_reviewed_poi
    run(driver, textwrap.dedent("""\
        LOAD CSV WITH HEADERS FROM $file AS row
        CALL{
            WITH row
            MATCH (user:User {id: toInteger(row.user_id)})
            MATCH (review:Review {id: toInteger(row.review_id)})
            MATCH (poi:Poi {id: toInteger(row.poi_id)})
            MERGE (user)-[w:WROTE]->(review)
            MERGE (review)-[rated:RATED]->(poi)
            MERGE (user)-[reviewed:REVIEWED ]->(poi)
            ON CREATE SET reviewed.rating = review.rating
            RETURN count(w) AS WROTE_count, count(rated) AS RATED_count, count(reviewed) AS REVIEWED_count
        } IN TRANSACTIONS
        RETURN SUM(WROTE_count) AS total_WROTE_count, SUM(RATED_count) AS total_RATED_count, SUM(REVIEWED_count) AS total_REVIEWED_count
        """),
        params = {'file': url_user_reviewed_poi}
    )

    return


# FUNCTION: load data into neo4j
def data_loading(driver):

    # get the count of nodes in database
    node_count = run(driver, "MATCH (n) RETURN count(n) AS count")[0][0]  #[<Record count=0>]
    #<class 'list'>, <class 'neo4j._data.Record'>, <class 'int'>

    # check if the database is empty first
    if  node_count == 0:

        # create constraint for primary key
        print("Setting constrains...")
        set_constrain(driver)
        print("Set Constrains done.")

        # load nodes into neo4j database
        print("Loading nodes...")
        nodes_loader(driver)
        print("Nodes loading done.")

        # load relationships into neo4j database
        print("Loading relationships...")
        relationships_loader(driver)
        print("Relationships loading done.")
    
    else:
        print("Database is already loaded with data.")

    return
    
# entry point
if __name__ == '__main__':

    # neo4j connections

    # Get credentials to connect neo4j
    HOST, DATABASE, PASSWORD = get_credential()

    # create neo4j Python driver
    driver = GraphDatabase.driver(HOST, auth=(DATABASE, PASSWORD))

    data_loading(driver)

    # close the driver
    driver.close()