from transformers import pipeline
import time

start_time=time.time()


sentiment=pipeline(task='sentiment-analysis')
results=sentiment('''10/10 interesting story, art and its so freaking funny 😂😂😂 Recommended.''')
print(results)

print(time.time() - start_time)
