import asyncio
import telegram

import sys
import os
import shutil

import datetime

directory_path = sys.argv[1]

file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

api_token=os.environ["API_TOKEN"]
api_chat_id=os.environ["CHAT_ID"]


async def main():
    bot = telegram.Bot(token=api_token)

    chat_id = api_chat_id

    message = f"""
    ----------------------------------------
      KASHYA'S MANGA NEWSLETTER - {datetime.date.today()}
    ----------------------------------------

    Hey fellow otakus!

    It's time for another edition of Kashya's Manga Newsletter! 

    Here are some of the titles that caught our eye.


    ----------------------------------------
                """

    list_of_image_paths = [f for f in file_paths if f.endswith('.png')]

    await bot.send_message(chat_id=chat_id, text=message)

    for image_path in list_of_image_paths:
        with open(image_path, 'rb') as f:
            for i in range(5): # Retry up to 5 times
                try:
                    await bot.send_photo(chat_id=chat_id, photo=f)
                    break # Break out of the retry loop if the message is sent successfully
                except telegram.error.TimedOut:
                    print("Timed out. Retrying...")
                    await asyncio.sleep(5) # Wait for 5 seconds before retrying

if __name__ == '__main__':
    print("\nTRANSMITTING TO TELEGRAM")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    print("\nTRANSMISSION ENDED")

    shutil.rmtree(directory_path)


