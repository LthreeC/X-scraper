# X (twitter) scraper

## intro

*This project is based on https://github.com/Mostafa-Ehab/Twitter-Scrapper*

The project is a selenium based X (twitter) scraper

...

## install & env

```bash
git clone git@github.com:LthreeC/X-scrapper.git
cd X-scrapper
pip install -r requirements.txt
```

ensure PYTHONPATH is set to the root of the project

```bash
export PYTHONPATH=<your project root>:$PYTHONPATH
```

## run

> input/conf.json: configuration file, make sure access token is set

[how to get access token](https://github.com/Mostafa-Ehab/Twitter-Scrapper)

**scrap_tweets: input a list of id, get tweets**
```bash
python script/scrap_tweets.py --threads 1 --users -1 --tweet_num 100 --time_range 240 --homepage_list home
```

**output format:**
```json
{
  "<token>": {
    "<url>": {
      "url": "<url>",
      "ID": "",
      "Nickname": "",
      "Date": "",
      "isReposted": ,
      "isMedia": ,
      "Language": "",
      "Replies": ,
      "Reposts": ,
      "Likes": ,
      "Bookmarks": ,
      "Views": ,
      "Text": ""
    }
  }
}
```

<br>

**scrap_interactions: input a list of id, get interactions**
```bash
python script/scrap_interactions.py --threads 1 --users 1 --url_list "https://x.com/MathVerseNFT/status/1899369827866685661" "https://x.com/MathVerseNFT/status/1874155560058196310"
```

**output format:**
```json
{
  "<token>": {
    "<url>": {
      "quotes": [],
      "retweets": [
        {
          "ID": "",
          "Nickname": ""
        },
        {
          "ID": "",
          "Nickname": ""
        }
      ]
    }
  }
}
```

<br>

**scrap_homepage: input a list of id, get homepage info**
```bash
python script/scrap_homepage.py --threads 1 --users 1 --url_list "elonmusk" "NASA" "realDonaldTrump" "realDonaldTrump"
```

**output format:**
```json
{
    "<token>": {
        "<id>": {
            "ID": "",
            "Nickname": "",
            "Description": "",
            "dateCreated": "",
            "homeLocation": "",
            "followers": ,
            "following": ,
            "posts": 
        },
    }
}
```

## webui

```bash
python webui.py
```

or

```bash
gradio webui.py
```
