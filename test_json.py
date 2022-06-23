import json
  
# Opening JSON file
f = open('sample.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
print(data)
  
# Closing file
f.close()
