from fastapi import FastAPI
from .routers import user, auth, news, extract, admin_dev

description = """
# News Article API.

this API is for learning purposes only.

Here you will be able to create your own user and save your favourite news article from supported websites,
and check if it's fake or real news.


## Articles

* **extract article info from supported websites such as:**
    * title
    * authors
    * subject
    * content (text)
* **classify articles Fake/Real**
* **read articles from db**
* **save articles to db**
* **delete articles from db**

## Users

* **Create users**
* **Read users**
* **Authenticate users\\login**
"""

app = FastAPI(description=description)

app.include_router(news.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(extract.router)
app.include_router(admin_dev.router)


@app.get("/")
def root():
    return {"Disclaimer": "this API is for learning purposes only."}