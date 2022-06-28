from transformers import pipeline
import time

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def analyze_comments(comments): #814 MB
	start_time=time.time()
	sentiment=pipeline("sentiment-analysis",model="nlptown/bert-base-multilingual-uncased-sentiment")
	total_stars=0
	for comment in comments:
		result=sentiment(comment)
		#print(comment)
		#print(result)
		stars=int(result[0]['label'][:1])
		#print(stars)
		total_stars+=stars
		#print("\n\n\n")
	#print(total_stars/len(comments))
	print("Time taken for setiment analysis: ")
	print(time.time() - start_time)
	print("\n\n")
	return total_stars/len(comments)
	
	
