import pytest
from app import schemas


@pytest.mark.parametrize("url", 
                            [('https://medium.com/'),
                            ("https://cnn.com/")])
def test_unsupported_website(client, url):
    response = client.post("/make-article/metadata/", json={"url": url})
    assert response.status_code == 422
    assert response.json()['detail'] == "Unsupported website"
    # print(response.__dict__)


@pytest.mark.parametrize("url,title,author,subject", 
                    [
                        (
                        "https://www.reuters.com/business/healthcare-pharmaceuticals/pfizer-start-us-trial-gene-therapy-fda-lifts-hold-2022-04-28/",
                        "Pfizer to start U.S. trial of gene therapy as FDA lifts hold",
                        "Reuters",
                        "Future of Health"
                        ),
                        (
                        "https://www.reuters.com/world/asia-pacific/nkorea-says-it-detected-outbreak-stealth-omicron-virus-state-media-2022-05-12/",
                        "N.Korea reports first COVID outbreak, orders lockdown in \"gravest emergency\"",
                        "By Joori Roh & Soo-Hyang Choi",
                        "Asia Pacific"
                        ),
                        (
                        "https://www.bbc.com/news/world-asia-61416760",
                        "North Korea: 'First' Covid cases prompt strict national lockdown",
                        "By Frances Mao",
                        "Coronavirus pandemic"
                        ),
                        (
                        "https://www.bbc.com/news/world-asia-61417972",
                        "Sri Lanka crisis: Gotabaya Rajapaksa appoints veteran politician as PM",
                        "By Ayeshea Perera & Simon Fraser",
                        "Asia"
                        ),
                        (
                        "https://www.bbc.com/news/world-middle-east-61403320",
                        "Al Jazeera reporter killed during Israeli raid in West Bank",
                        None,
                        "Press freedom"
                        )
                    ])
def test_get_article_data(client, url, title, author, subject):
    response = client.post("/make-article/metadata/", json={"url": url})
    assert response.status_code == 200
    article = schemas.ParsedArticle(**response.json())
    assert article.title == title
    assert article.author == author
    assert article.subject == subject


@pytest.mark.parametrize("url", 
                            [('https://www.reuters.com/investigates/special-report/usa-renewables-electric-grid/')])
def test_selector_not_found(client, url):
    response = client.post("/make-article/metadata/", json={"url": url})
    assert response.status_code == 422
    assert response.json()['detail'] == "title selector NOT found!"


# def test_get_article_data2(client, parsed_articles):
#     for i in range(len(parsed_articles)):
#         response = client.post("/make-article/metadata/", json={"url": parsed_articles[i]["url"]})
#         article = schemas.ParsedArticle(**response.json())
#         assert response.status_code == 200
#         assert article.title == parsed_articles[i]["title"]
#         assert article.author == parsed_articles[i]["author"]
#         assert article.subject == parsed_articles[i]["subject"]


@pytest.mark.parametrize("text, label", 
                            [("this is a fake news article","Fake"),
                            ("this is my second fake news article","Fake"),
                            ("April 28 (Reuters) - Pfizer Inc (PFE.N) said on Thursday it would open the first U.S. trial sites for its experimental gene therapy for a muscle-wasting disorder, after the Food and Drug Administration lifted its hold on a late-stage study.","Real")
                            ])
def test_make_prediction(client, text, label):
    response = client.post("/make-article/pred/", data={"text": text})
    result = schemas.PredictionRes(**response.json())
    assert response.status_code == 200
    assert result.label == label

#@pytest.mark.skip(reason="function not implemented yet")
def test_make_prediction_invalid_text(client):
    # with pytest.raises(ValueError): # test will fail if value error is not raised
    #     client.post("/make-article/pred/", data={"text": None})
    response = client.post("/make-article/pred/", data={"text": None})
    assert response.status_code == 422