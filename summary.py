from transformers import pipeline

def get_summary(desc_text):
	summarizer = pipeline("summarization", model="facebook/bart-large-cnn") #1.14GB
	ARTICLE =desc_text
	print(summarizer(ARTICLE, truncation=True))

