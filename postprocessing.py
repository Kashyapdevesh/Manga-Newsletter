import pandas as pd
import json

def get_image(url):
    file_name='image.jpg'
    r=requests.get(url,stream=True)
    if r.status_code==200:
        with open(file_name,'wb') as f:
            shutil.copyfileobj(r.raw,f)
        print("\nImage Downloaded from " +str(url)+"\n")
    else:
        print("\nImage can't be retrieved\n")

def get_final_df():
    with open('final_data.txt') as file:
        data=file.read()
        
    info=json.loads(data)

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

    df=df[df['Chapter_Count']>=10]

    df['Rating_Value']=df['Rating_Value'].astype(float)
    df['View_Count']=df['View_Count'].astype(int)
    df['Chapter_Count']=df['Chapter_Count'].astype(int)

    df=df.sort_values(by=['Chapter_Count','View_Count','Rating_Value'], ascending=[True, False,False],ignore_index=True).head(10)

    return df

def main():
    df=get_final_df()
    
