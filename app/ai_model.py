"""fake news lstm model pipeline"""

import json
import numpy as np
from . import schemas
from pathlib import Path
from dataclasses import dataclass
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

@dataclass
class FAKE_NEWS_Model():
	model_h5_path: Path
	tokenizer_path: Path
	data_path: Path

	model = None
	tokenizer = None
	metadata = None
	labels_legend = None

	# load data when creating new model instance
	def __post_init__(self):
		self.model = self.get_model()
		self.tokenizer = self.get_tokenizer()
		self.metadata = self.get_metadata()
		self.labels_legend = self.metadata['labels_legend']


	def get_model(self):
		if self.model_h5_path.exists() and self.model_h5_path.name.endswith("h5"):
			return load_model(self.model_h5_path)
		raise Exception("Model Not Implemented!")


	def get_tokenizer(self):
		if self.tokenizer_path.exists() and self.tokenizer_path.name.endswith("json"):
			return tokenizer_from_json(self.tokenizer_path.read_text())
		raise Exception("Tokenizer Not Implemented!")


	def get_metadata(self):
		if self.data_path.exists() and self.data_path.name.endswith("json"):
			return json.loads(self.data_path.read_text())
		raise Exception("metadata not implemented!")


	def clean_text(self, text):
		stop_words = set(stopwords.words('english'))
		lemma = WordNetLemmatizer()
		pattern1 = r"^([a-zA-Z])[\/]{0,1}(.*[a-zA-Z])\s\((Reuters)\)\s"
		text = re.sub(pattern1," ",text)
		text = text.lower()
		text = re.sub("[^a-zA-Z]"," ",text) # delete every thing not in a-z or A-Z
		words = word_tokenize(text)
		words = [word for word in words if word not in stop_words]
		words = [lemma.lemmatize(word, pos='v') for word in words]
		words = [lemma.lemmatize(word, pos='a') for word in words]
		text = " ".join(words)
		return text


	def get_model_input(self,text):
		tokenized_seq = self.tokenizer.texts_to_sequences(text)
		return pad_sequences(tokenized_seq, maxlen=self.metadata["seq_len"],padding='post', truncating='post')


	def get_prediction(self,text):
		text = self.clean_text(text)
		text = np.asarray([text])
		# text = pd.Series(data=text)
		model_input = self.get_model_input(text)
		preds = self.model.predict(model_input)
		preds_indx = np.argmax(preds)
		pred_conf = preds[0][preds_indx]
		# res = {
		# 		"label": f"{self.labels_legend[str(preds_indx)]}", 
		# 		"confidence": round(float(pred_conf), 4)
		# 		}
		# return res
		return schemas.PredictionRes(
								label=f"{self.labels_legend[str(preds_indx)]}",
								confidence=round(float(pred_conf), 4)
								)