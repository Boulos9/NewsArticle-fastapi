"""PATH OPERATION For:
	- initialize the LSTM model
	- scraping the news article URL and extracting the data
	- classify if an article is Fake or Real news
	- add article with data above to database
"""

import pathlib
from ..database import get_db
from sqlalchemy.orm import Session
from .. import schemas, scraper, oauth2, ai_model, models
from fastapi import HTTPException, Depends, APIRouter, Body


router = APIRouter(
	prefix="/make-article",
	tags=["Scraper-Classification"],
	)


MAIN_PATH = pathlib.Path(__file__).resolve().parent.parent.parent # __file__ path of this file
EXPORTS_PATH = MAIN_PATH / "model_exports"
MODEL_H5_PATH = EXPORTS_PATH / "lstm_model.h5"
TOKENIZER_PATH = EXPORTS_PATH / "article_tokenizer.json"
DATA_PATH = EXPORTS_PATH / "metadata.json"

model = None


@router.on_event("startup")
def startup_event():
    global model
    model = ai_model.FAKE_NEWS_Model(MODEL_H5_PATH, TOKENIZER_PATH, DATA_PATH)


# return schema of the extracted data
@router.post("/metadata/", response_model=schemas.ParsedArticle)
def get_article_data(URL: schemas.ArticleCreate):
	"""
	Extract this data from the article in the URL:

	- **title**: the title of the article
	- **author**: the authors of the article
	- **subject**: the subject of the article
	- **content**: the content (text) of the article
	- *return* a pydantic model with the values above
	- @param URL: User input
	"""
	scrpr = scraper.Scraper(URL)
	return scrpr.parse_and_extract()


# return schema of the prediction result
@router.post("/pred/", response_model=schemas.PredictionRes)
def make_prediction(text: str = Body(...)):
	global model
	try:
		return model.get_prediction(text)
	except:
		raise Exception("couldn't make prediction")
	# if isinstance(text, str):
	# 	try:
	# 		return model.get_prediction(text)
	# 	except:
	# 		raise Exception("couldn't make prediction")
	# else:
	# 	raise TypeError("value should be of type string")


@router.post("/create/", response_model=schemas.ArticleOut)
def create_article(URL: schemas.ArticleCreate, db: Session = Depends(get_db), 
	current_user: int = Depends(oauth2.get_current_user)):
	"""
	Extract the article content and classify it Fake/Real:

	- **URL**: the URL of the article, required
	- *return* a pydantic model with the article data and the prediction result
	"""
	parsed_data = get_article_data(URL)
	result = make_prediction(parsed_data.content)
	article_data = {**parsed_data.dict(), **result.dict()}
	new_article = models.Article(owner_id=current_user.id, url=URL.url, **article_data)
	db.add(new_article)
	db.commit()
	db.refresh(new_article)
	return new_article