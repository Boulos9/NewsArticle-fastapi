"""Scraper Pipeline"""

import re
import requests
from . import schemas
from requests_html import HTML
from dataclasses import dataclass
from fastapi import HTTPException


@dataclass
class Scraper():
	URL: schemas.ArticleCreate

	r_html = None
	patterns = [r".*(reuters\.com)", r".*(bbc\.com)"] # World/Business/Legal..
	html_id = {
				0:
				{
				#"title_selector": ".text__text__1FZLe.text__dark-grey__3Ml43.text__medium__1kbOh.text__heading_2__1K_hh.heading__base__2T28j.heading__heading_2__3Fcw5",
				#"author_selector": "div.article-body__element__2p5pI span[data-testid='Text'].text__dark-grey__3Ml43",
				"title_selector": "div.article-header-v2__heading__3KoAG h1[data-testid='Heading']",
				"author_selector": "a[href*='/authors']",
				"text_selector": "p[data-testid*='paragraph']",
				"subject_selector": "li a[data-testid='Button'] span[data-testid='Text']",
				#"subject_id": "li.tags__tag-item__iG2wd a[data-testid='TextButton'] span[data-testid='Text']",
				},
				1:
				{
				"title_selector": "article h1[id='main-heading']",
				"author_selector": "article p span strong",
				"text_selector": "article div[data-component='text-block']",
				"subject_selector": "article ul[role='list'] li a.ssrcss-156x968-StyledLink",
				},
			}
	web_id = None


	def __post_init__(self):
		self.web_id = self.web_server()
		self.r_html = self.url_to_html()


	def web_server(self):
		for i, pattern in enumerate(self.patterns):
			if re.match(pattern, self.URL.url) != None:
				return i
		raise HTTPException(status_code=422,
						detail="Unsupported website")


	def url_to_txt(self, url):
		r = requests.get(url)
		if r.status_code == 200:
			html_text = r.text
			return html_text
		raise HTTPException(status_code=r.status_code, 
							detail=f"something went wrong: {r.status_code}")

	
	def url_to_html(self):
		html_txt = self.url_to_txt(self.URL.url)
		return HTML(html=html_txt)


	def extract_title(self):
		title_selector = self.html_id[self.web_id]["title_selector"]
		r_table = self.r_html.find(title_selector)
		if len(r_table)==0:
			raise HTTPException(status_code=422,
								detail="title selector NOT found!") # "Unprocessable Entity"
		return r_table[0].text


	def extract_author(self):
		author_selector = self.html_id[self.web_id]["author_selector"]
		r_table = self.r_html.find(author_selector) # check if impty list return None
		if r_table == []:
			return None
		if len(r_table) > 1: # in reuters if more than one author they are seperated, we join them
			authors = "By " + r_table[0].text
			for i in range(1, len(r_table)):
				authors += " & " + r_table[i].text
			return authors
		return r_table[0].text


	def extract_text(self):
		text_selector = self.html_id[self.web_id]["text_selector"]
		r_table = self.r_html.find(text_selector)
		if len(r_table)==0:
			raise HTTPException(status_code=422,
								detail="text selector NOT found!")
		text = ""
		for i in range(len(r_table)):
			text += r_table[i].text + "\n"
		return text


	def extract_subject(self):
		subject_selector = self.html_id[self.web_id]["subject_selector"]
		r_table = self.r_html.find(subject_selector)
		if r_table == []:
			return None
		# for i in range(2):
		# 	print(f"sub_{i} list: ", r_table[i].text)
		# print(f"sub list: ", r_table)
		return r_table[0].text


	def parse_and_extract(self):

		title = self.extract_title()
		author = self.extract_author()
		content = self.extract_text()
		subject = self.extract_subject()

		return schemas.ParsedArticle(
								title=title,
								author=author,
								content=content,
								subject=subject
								)