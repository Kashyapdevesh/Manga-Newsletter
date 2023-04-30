import pandas as pd
import json
import time
import sys
import shutil
import os
# import subprocess
import tempfile


final_info_file=os.environ['FINAL_INFO_FILE'] 
# final_info_file = sys.argv[1]
temp_file_path = os.path.join(final_info_file, 'final_data_file.json')

print("\nSTARTED PREPARING DF")
start=time.time()

with open(temp_file_path, 'r') as temp_file:
    info = json.load(temp_file)

df = pd.DataFrame(columns=['Name','Cover Image','Author','Current Status','Manga Genre', 'Manga Total Views','Rating','Description','Chapter_Count'])

for url,val in info.items():
    df.loc[len(df.index)] = [info[url]['Name'], info[url]['Cover Image'], info[url]['Author'],
                             info[url]['Current Status'],info[url]['Manga Genre'],info[url]['Manga Total Views'],
                             info[url]['Rating'],info[url]['Description'],len(list(info[url]['chapters_info'].keys()))]

df['Rating_Value'] = df['Rating'].apply(lambda x: x.split("/")[0])
df['View_Count']=df['Rating'].apply(lambda x: x[x.find("-")+1:x.find("v")].replace(" ","").replace(",",""))

df['Rating_Value']=df['Rating_Value'].replace('',0)
df['View_Count']=df['View_Count'].replace('',0)
df['Chapter_Count']=df['Chapter_Count'].replace('',0)

df=df[df['Chapter_Count']>=30]

df['Rating_Value']=df['Rating_Value'].astype(float)
df['View_Count']=df['View_Count'].astype(int)
df['Chapter_Count']=df['Chapter_Count'].astype(int)

df=df.sort_values(by=['Chapter_Count','View_Count','Rating_Value'], ascending=[True, False,False],ignore_index=True).head(10)

# Create a temporary directory with a unique name
csv_dir = tempfile.mkdtemp(prefix='csv_storage')

# Create a temporary file inside the directory
csv_file_path = os.path.join(csv_dir, 'full_test.csv')

df.to_csv(csv_file_path,index=False)

print((time.time()-start)/60)

shutil.rmtree(final_info_file)

print("DF PREPARTION OVER\n")

# subprocess.call(['python', 'final_post.py', csv_dir])
os.environ['CSV_DIR'] = csv_dir

