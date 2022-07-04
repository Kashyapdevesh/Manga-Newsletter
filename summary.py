from transformers import pipeline

def get_summary(desc_text):
	summarizer = pipeline("summarization", model="facebook/bart-large-cnn") #1.14GB
	ARTICLE =desc_text
	summarized_text=summarizer(ARTICLE, truncation=True, min_length=30, do_sample=False)
	return summarized_text

