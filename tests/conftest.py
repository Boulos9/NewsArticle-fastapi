from fastapi.testclient import TestClient
import pytest
from app.main import app

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.database import get_db, Base

from app.oauth2 import create_access_token
from app import models


settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.dict()["database_test_credentials"]

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""
fixture: each test function can call this fixture session as an argument,
and the fixture will yield back the db value as the argument value of the test function

scope: the session is closed after each test even if there were an exception (finally block)
"""
@pytest.fixture(scope="function") # we want each test function independent from the other
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    """
    or
    with TestingSessionLocal() as db:
        yield db

    will be closed after all tests finish
    """


# test environment
@pytest.fixture(scope="function")
def client(session): # session is a fixture
    def override_get_db(): # the overide depend
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    #yield TestClient(app)
    # to test startup_event
    with TestClient(app) as cl:
        yield cl


@pytest.fixture
def test_user1(client):
    user_data = {"email": "hello@gmail.com", "password": "pass123"}
    response = client.post("/users/", json=user_data) # create test user
    assert response.status_code == 201

    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email": "hello2@gmail.com", "password": "pass123"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user



@pytest.fixture
def token(test_user1):
    return create_access_token(data = {"user_id": test_user1["id"]})


"""
the token is built for test_user1
so the authorized_client is test_user1
"""
@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, 
                        "Authorization": f"Bearer {token}"}
    return client


# we need a user to make a post so we need test_user
# we need to work with the database to make a post so we need session
@pytest.fixture
def test_posts(test_user1, session, test_user2):
    articles_data = [{
                    "title": "test title",
                    "author": "test publisher",
                    "subject": "test sub",
                    "content": "this is my first news article",
                    "owner_id": test_user1['id'],
                    "label": "Fake",
                    "confidence": 0.9999,
                    "url": "https://www.reuters.com/"
                    },
                    {
                    "title": "test title",
                    "author": "test publisher",
                    "subject": "test sub",
                    "content": "this is my second news article",
                    "owner_id": test_user1['id'],
                    "label": "Fake",
                    "confidence": 0.9999,
                    "url": "https://www.reuters.com/"
                    },
                    {
                    "title": "test title",
                    "author": "test publisher",
                    "subject": "test sub",
                    "content": "this is my third news article",
                    "owner_id": test_user1['id'],
                    "label": "Fake",
                    "confidence": 1.0,
                    "url": "https://www.reuters.com/"
                    },
                    {
                    "title": "test title",
                    "author": "test publisher",
                    "subject": "test sub",
                    "content": "reuters this is my fourth news article",
                    "owner_id": test_user2['id'],
                    "label": "Real",
                    "confidence": 0.9545,
                    "url": "https://www.reuters.com/"
                    }]
    # now we need to take each article from articles_data and add it to our test article table
    # we do that by passing that article to our Article model.
    # lambda function takes an article (dict) and convert it to an article object,
    # map takes an article from articles_data and feed it to lambda function
    # to sum it up, we will take a list of dict and convert it into a list of article models
    articles = list(map(lambda article: models.Article(**article), articles_data))
    # print("\nposts ", articles)
    session.add_all(articles)
    session.commit()
    return session.query(models.Article).all()


# @pytest.fixture
# def parsed_articles():
#     test_articles = [
#                         {
#                         "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/pfizer-start-us-trial-gene-therapy-fda-lifts-hold-2022-04-28/",
#                         "title": "Pfizer to start U.S. trial of gene therapy as FDA lifts hold",
#                         "author": "Reuters",
#                         "subject": "Future of Health"
#                         },
#                         {
#                         "url": "https://www.reuters.com/world/asia-pacific/nkorea-says-it-detected-outbreak-stealth-omicron-virus-state-media-2022-05-12/",
#                         "title": "N.Korea reports first COVID outbreak, orders lockdown in \"gravest emergency\"",
#                         "author": "By Joori Roh & Soo-Hyang Choi",
#                         "subject": "Asia Pacific"
#                         },
#                         {
#                         "url": "https://www.bbc.com/news/world-asia-61416760",
#                         "title": "North Korea: 'First' Covid cases prompt strict national lockdown",
#                         "author": "By Frances Mao",
#                         "subject": "Coronavirus pandemic"
#                         },
#                         {
#                         "url": "https://www.bbc.com/news/world-asia-61417972",
#                         "title": "Sri Lanka crisis: Gotabaya Rajapaksa speech fails to reassure as crisis grows",
#                         "author": "By Ayeshea Perera",
#                         "subject": "Asia"
#                         },
#                         {
#                         "url": "https://www.bbc.com/news/world-middle-east-61403320",
#                         "title": "Al Jazeera reporter killed during Israeli raid in West Bank",
#                         "author": None,
#                         "subject": "Press freedom"
#                         }]
#     return test_articles