import pytest
from app import schemas


def test_get_articles(authorized_client, test_user1, test_posts):
	response = authorized_client.get("/articles/")
	assert response.status_code == 200
	articles = list(map(lambda article: schemas.ArticleOut(**article), response.json()))
	for article in articles:
		assert article.owner_id == test_user1['id']


def test_unauthenticated_get_articles(client, test_user1, test_posts):
	response = client.get("/articles/")
	#print(response.json())
	assert response.status_code == 401
	assert response.json()["detail"] == "Not authenticated"


def test_get_all_articles(client, test_posts):
	"""
	print(test_posts[0].__dict__) ->
		{'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x0000022BB85EB070>,
		 'id': 1, 
		 'publisher': None, 
		 'label': 'Fake', 
		 'owner_id': 1, 
		 'title': None, 
		 'content': 'this is my first news article', 
		 'created_at': datetime.datetime(2022, 4, 27, 15, 26, 53, 601649, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800))), 
		 'confidence': 0.9999}
	"""
	response = client.get("/admin/all/articles")
	assert len(response.json()) == len(test_posts)
	assert response.status_code == 200


#test_get_one_article
def test_get_article(authorized_client, test_posts):
	response = authorized_client.get(f"/articles/{test_posts[0].id}")
	article = schemas.ArticleOut(**response.json())
	assert article.owner_id == test_posts[0].owner_id
	assert article.id == test_posts[0].id
	assert response.status_code == 200
	assert test_posts[0].owner_id > 0


def test_get_unauthorized_item(authorized_client, test_posts, test_user2):
	response = authorized_client.get(f"/articles/{test_posts[3].id}")
	assert test_posts[3].owner_id == test_user2['id']
	assert response.status_code == 401
	assert response.json()["detail"] == "UNAUTHORIZED ACTION"


def test_get_non_existing_item(authorized_client, test_posts):
	response = authorized_client.get("/articles/212")
	assert response.status_code == 404
	assert response.json()['detail'] == "article with id: 212 was NOT FOUND"


@pytest.mark.parametrize("id, status_code",[
                            (0,422),
                            ("abc",422)])
def test_get_invalid_article_id(authorized_client,id,status_code):
	response = authorized_client.get(f"/articles/{id}")
	assert response.status_code == status_code


def test_delete_item(authorized_client, test_posts):
	id = test_posts[0].id
	response = authorized_client.delete(f"/articles/delete/{id}")
	assert response.status_code == 204 # no content
	response = authorized_client.get(f"/articles/{id}")
	assert response.status_code == 404
	assert id > 0


def test_delete_non_existing_item(authorized_client, test_posts):
	response = authorized_client.delete("/articles/delete/212")
	assert response.status_code == 404
	assert response.json()['detail'] == "article with id: 212 was NOT FOUND"


def test_delete_unauthorized_item(authorized_client, test_posts):
	response = authorized_client.delete(f"/articles/delete/{test_posts[3].id}")
	assert response.status_code == 401
	assert response.json()['detail'] == "UNAUTHORIZED ACTION"


@pytest.mark.parametrize("id, status_code",[
                            (0,422),
                            ("abc",422)])
def test_delete_invalid_article_id(authorized_client,id,status_code):
	response = authorized_client.delete(f"/articles/delete/{id}")
	assert response.status_code == status_code