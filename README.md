![](https://i.pinimg.com/564x/2b/ae/61/2bae615a911d23480f38c430b5d287fd.jpg)

# Kashya's Newsletter

The aim of this project is to create a fully automated personalized manga/manhwa 
newsletter integrated with WhatsApp and emailing services.




## Milestones



STAGE | STATUS 
--- | --- 
Single page manganelo scraper | &check;
Pipeline automated scraper with single page scraper | &check;
Multithreaded queue for storing queries | &cross;
Sentiment analysis of text in comments | &check;
Sentiment analysis of memes in comments | &cross;
Text summarization model | &check;
Connection with MySQL DB | &check;
Single page newsletter image generation(url sample)| &check;
WhatsApp cloup API'S webhook  |&cross;
Fully concurrent final WA client  | &cross;
Flask API between client and DB | &cross;
Emailing services |&cross;
Improve Logging |&cross;







## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`DB_TYPE` 

`DB_USER`

`DB_PASS`

`DB_HOST`

`DB_NAME`

### NOTE:
 You don't need the environment variables for simple testing as mentioned below.


## Run Locally

Clone the project

```bash
  git clone git@github.com:Kashyapdevesh/Manga-Newsletter.git
```

Go to the project directory

```bash
  cd  Manga-Newsletter
```

Prepare and activate virtual environment 

```bash
  virtualenv venv

  source venv/bin/activate
```

Install dependencies

```bash
  pip install -r  requirements.txt 

```

### NOTE:
Currently the project is under developement and the instructions will
be simulatneously updated.

At present state we can check the functioning of modules listed in milestones.

You can generate single page newsletter sample for the manga of your choice 
by following the instructions below:

* Select the manga of your choice from https://m.manganelo.com/www 

* Replace variable *url* with chosen url in line no. 240 in [page_scraper.py](../main/page_scraper.py)

* Run the script

```bash
  python3 page_scraper.py
```

You can view some pre-prepared samples at [link](https://github.com/Kashyapdevesh/Manga-Newsletter/tree/main/test_samples)


## Authors

- [@Kashyapdevesh](https://github.com/Kashyapdevesh)

Contributions are always welcome!


## Feedback

If you have any feedback, please reach out to us at devesh.btech.cs19@iiitranchi.ac.in


