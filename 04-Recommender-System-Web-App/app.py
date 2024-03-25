from flask import Flask, render_template, request, session, redirect, url_for

from neo4j import GraphDatabase
from graphdatascience import GraphDataScience

# my 
from neo4j_tools import get_credential
import recommender
import data_loader
import pre_training


# neo4j connections

# Get credentials to connect neo4j
HOST, DATABASE, PASSWORD = get_credential()

# create neo4j Python driver
driver = GraphDatabase.driver(HOST, auth=(DATABASE, PASSWORD))

# Connect using GDS library
gds = GraphDataScience(HOST,auth=(DATABASE, PASSWORD))

# create app
app = Flask(__name__)

# Secret key for session management
app.secret_key = 'secret'


# Index route
@app.route('/')
def index():

    # Check if the 'user_id' key exists in the session, get user id
    if 'user_id' in session:
        user_id = session['user_id']
        # get recommendations
        rec_pois = recommender.recommend(gds=gds, user_id=user_id)
    #print(rec_pois)
    else:
        rec_pois = []
    #print(f'rec_pois:{rec_pois}')

    # Get data from database
    with driver.session() as neo4j_session:

        # Retrieve all POI nodes from Neo4j
        poi_records = neo4j_session.run("MATCH (poi:Poi) RETURN poi")   #<class 'neo4j._sync.work.result.Result'>
        pois = [record['poi'] for record in poi_records]    #<class 'list'>
        #print(type(pois[0]))    #<class 'neo4j.graph.Node'>

        # Sort the pois list alphabetically by the name attribute
        pois_sorted = sorted(pois, key=lambda x: x['name'])
  
        # get 10 popular pois
        popular_pois_records = neo4j_session.run("MATCH (poi:Poi) RETURN poi ORDER BY poi.numReviews DESC LIMIT 10") 
        popular_pois = [record['poi'] for record in popular_pois_records]
        #print(f"pooular_pois: {popular_pois}")

    return render_template('index.html', pois=pois_sorted, rec_pois=rec_pois, popular_pois=popular_pois)


# Poi detail route
@app.route('/poi/<poi_id>')
def poi(poi_id):

    # Check if the 'user_id' key exists in the session, get user id
    if 'user_id' in session:
        user_id = session['user_id']
    else:
        user_id = 0
    #print(f'user_id:{user_id}')

    # convert str to int
    poi_id = int(poi_id)

    # get recommendations
    rec_pois = recommender.recommend(gds=gds, poi_id=poi_id, user_id=user_id)
    #print(rec_pois)

    # Get data from database
    with driver.session() as neo4j_session:

        # Retrieve target POI nodes from Neo4j
        pois = neo4j_session.run('''
                MATCH (poi:Poi{id: $target_poi}) 
                RETURN poi
                ''', target_poi=poi_id)
        poi = pois.single()['poi']   #<class 'neo4j.graph.Node'>

    return render_template('poi.html', poi=poi, rec_pois=rec_pois)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Assuming you have a user table in your database
        username = request.form['username']
        password = request.form['password']

        # Perform authentication
        # If authentication succeeds, set the user ID in the session
        if username == 'user1' and password == 'user1':
            session['user_id'] = 3098  # Review Count: 34
            return redirect(url_for('index'))
        elif username == 'user2' and password == 'user2':
            session['user_id'] = 433  # Review Count: 5
            return redirect(url_for('index'))
        elif username == 'user3' and password == 'user3':
            session['user_id'] = 10  # Review Count: 1
            return redirect(url_for('index'))
        else:
            # Authentication failed, render login page with an error message
            return render_template('login.html', error='Invalid username or password')

    # If request method is GET, render the login page
    return render_template('login.html')


# Log out route
# back to curent page, back to index if current page is user profile
@app.route('/logout', methods=['POST'])
def logout():
    # Get the referrer URL (the URL of the page that sent the request)
    referrer = request.referrer

    # Remove the 'user_id' key from the session
    session.pop('user_id', None)

    # Check if the referrer URL is the user_profile page
    if referrer and referrer.endswith('/user_profile'):
        return redirect(url_for('index'))  # If referrer is user_profile, redirect to index
    else:
        return redirect(referrer or url_for('index'))  # Redirect back to the referrer if available, otherwise to index


# User profile route
@app.route('/user_profile')
def user_profile():

    # Check if the 'user_id' key exists in the session
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Redirect to index if user is not logged in

    # Get user info
    with driver.session() as neo4j_session:
                
        user_id = session['user_id']
        #print(f'user_id:{user_id}')

        user_node = neo4j_session.run("MATCH (user:User{id: $target_user}) RETURN user", target_user=user_id)
        user = user_node.single()['user']   #<class 'neo4j.graph.Node'>

        origin_node = neo4j_session.run("MATCH (user:User{id: $target_user})-[:FROM]->(origin:Origin) RETURN origin", target_user=user_id)
        origin = origin_node.single()['origin']   #<class 'neo4j.graph.Node'>

        review_count = neo4j_session.run("MATCH (user:User{id: $target_user})-[:WROTE]->(review:Review) RETURN COUNT(review) AS review_count", target_user=user_id)
        review_count = review_count.single()['review_count']   #<class 'neo4j.graph.Node'>
        #print(review_count)

    return render_template('user_profile.html', user=user, origin=origin, review_count=review_count)


if __name__ == '__main__':

    # preparation
    # when empty database is first intialized, 12 minutes to load data and pre train.
    data_loader.data_loading(driver)
    pre_training.pre_training(gds)

    # run the app
    app.run(debug=True)

