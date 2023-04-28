import pandas as pd
import dateparser
import json
import re
import warnings
warnings.filterwarnings("ignore")


def extract_chapter(text):
    # define regular expression pattern to match chapter number
    pattern = r'(?:Vol\.|Volume )?(\d+)[^\d]*(\d+)?|Chapter (\d+)'
   
    # match pattern in the given text
    match = re.search(pattern, text)
    if match:
        # extract matched groups and return chapter number as string
        vol_num, ch_num, ch_num_only = match.groups()
        if ch_num:
            return f'Chapter {ch_num}'
        elif vol_num:
            return f'Chapter {vol_num}'
        elif ch_num_only:
            return f'Chapter {ch_num_only}'
    # if no match found, return None
    return None

def single_manga_df(idx):

    # Extract manga info
    info = info_dict[list(info_dict.keys())[idx]]
    manga_name = info['Name']
    cover_image_url = info['Cover Image']
    manga_author=info['Author']
    manga_current_status=info['Current Status']
    manga_total_views=info['Manga Total Views']
    manga_rating=info['Rating']
    manga_desc=info['Description']
    
    # Extract chapter info using list comprehension
    chapters = [(chapter, info['chapters_info'][chapter]['chapter_views'], dateparser.parse(info['chapters_info'][chapter]['chapter_upload_date'])) for chapter in info['chapters_info']]
    
    # Create a pandas DataFrame from the chapter info
    df_chapters = pd.DataFrame(chapters, columns=['Chapter', 'Views', 'Upload Date'])
    df_chapters['Chapter'] = df_chapters['Chapter'].apply(extract_chapter)

    # Add the manga name and cover image URL to each row
    df_chapters['Manga Name'] = manga_name
    df_chapters['Cover Image URL'] = cover_image_url
    df_chapters['Author']=manga_author
    df_chapters['Current Status']=manga_current_status
    df_chapters['Manga Total Views']=manga_total_views
    df_chapters['Rating']=manga_rating
    df_chapters['Description']=manga_desc

    # define the manga genres
    genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Fantasy', 'Harem', 'Horror', 'Mystery', 'Romance', 'School life', 'Sci-fi', 'Shounen', 'Slice of life', 'Supernatural', 'Tragedy']

    # add boolean columns for each genre
    df_chapters['Manga Genre'] = info['Manga Genre']
    for genre in genres:
        df_chapters[genre] = df_chapters['Manga Genre'].str.contains(genre)

    # Reorder the columns
    df_chapters = df_chapters[['Manga Name', 'Cover Image URL', 'Author', 'Current Status', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Fantasy', 'Harem', 'Horror', 'Mystery', 'Romance', 'School life', 'Sci-fi', 'Shounen', 'Slice of life', 'Supernatural', 'Tragedy', 'Manga Total Views', 'Rating', 'Description', 'Chapter', 'Views', 'Upload Date']]


    # Convert the 'Upload Date' column to datetime and extract date only
    df_chapters['Upload Date'] = pd.to_datetime(df_chapters['Upload Date']).dt.date


    # Sort the rows by chapter number
    df_chapters.sort_values('Chapter', inplace=True)

    # Reset the index
    df_chapters.reset_index(drop=True)
    
    return df_chapters



with open('final_data.txt') as data_file:
    raw_data=data_file.read()

info_dict=json.loads(raw_data)

final_df = pd.DataFrame(columns = ['Manga Name', 'Cover Image URL', 'Author', 'Current Status', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Fantasy', 'Harem', 'Horror', 'Mystery', 'Romance', 'School life', 'Sci-fi', 'Shounen', 'Slice of life', 'Supernatural', 'Tragedy', 'Manga Total Views', 'Rating', 'Description', 'Chapter', 'Views', 'Upload Date'])

for idx in range(len(info_dict)):
    print(f"PROCESSING MANGA {idx+1}/{len(info_dict)}")
    manga_df=single_manga_df(idx)   
    final_df = final_df.append(manga_df,ignore_index = True)
    print("MANGA_DF APPENDED\n")
    
final_df.to_csv("FULL_DB.csv")