import feedparser
import json
from datetime import datetime, date
import logging
import os
from flask import current_app
import sys

# adding Folder_2 to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from config import Config
from app.models import RSSArticle, RSSCategory

#Open the dictionary containing all rss sources to check
SOURCE_FILENAME = os.path.join(os.path.dirname(__file__), 'rss_sources.json')

try:
    f = open(SOURCE_FILENAME, 'r')
    rss_sources = json.load(f)
except:
    rss_sources = []

total_new = []
total_old = []
newfound_entries = 0

#Compare current entries with previous entries in temp file
for source in rss_sources:
    TEMP_FILENAME = os.path.join(os.path.dirname(__file__), 'temp', 'temp_' + source["name"] + '.json')
    try:
        f = open(TEMP_FILENAME, 'r')
        OLD_TEMP_FILE = json.load(f)
        total_old.extend(OLD_TEMP_FILE)
    except:
        OLD_TEMP_FILE = []
    NewsFeed = feedparser.parse(source["feed"])
    NEW_TEMP_FILE = NewsFeed.entries
    for new_entry in NEW_TEMP_FILE:
        duplicate = False
        for old_entry in OLD_TEMP_FILE:
            total_old.append(old_entry)
            if new_entry["id"] == old_entry["id"]:
                duplicate = True
                break
        if duplicate is False:
            total_new.append(new_entry)
            newfound_entries += 1


    with open(TEMP_FILENAME, 'w') as data_file:
        json.dump(NEW_TEMP_FILE, data_file, indent=3)

#Create year/month directories if they don't exist already
date = str(date.today()).split("-")
if os.path.exists(os.path.join(os.path.dirname(__file__), 'data', date[0])):
    pass
else:
    os.mkdir(os.path.join(os.path.dirname(__file__), 'data', date[0]))
if os.path.exists(os.path.join(os.path.dirname(__file__), 'data', date[0], date[1])):
    pass
else:
    os.mkdir(os.path.join(os.path.dirname(__file__), 'data', date[0], date[1]))

#Load the existing data of the day and save everything
try:
    f = open(os.path.join(os.path.dirname(__file__), 'data', date[0], date[1], f'{("-").join(date)}.json'), 'r')
    data = json.load(f)
except:
    data = []
data.extend(total_new)
with open(os.path.join(os.path.dirname(__file__), 'data', date[0], date[1], f'{("-").join(date)}.json'), 'w') as data_file:
    json.dump(data, data_file, indent=3)

#Log the newfound entries
logging.basicConfig(level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), 'py_log.log'),filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
logging.info(f'We have found {newfound_entries} new RSS entries.')


#add to database
app = create_app(config_class=Config)
total_upload = 0
with app.app_context():
    nogolist = []
    query = RSSArticle.query
    for x in query:
        nogolist.append(x.link)
    for entry in total_new:
        if entry["link"] not in nogolist:
            image_link = ""
            timestamp = datetime.strptime(entry["published"], '%a, %d %b %Y %H:%M:%S %z')
            for link in entry["links"]:
                if link["type"] == "image/jpeg":
                    image_link = link["href"]
            u = RSSArticle(title=entry["title"], link=entry["link"], image=image_link, publish_timestamp=timestamp, summary=entry["summary"])
            db.session.add(u)
            nogolist.append((entry["link"]))
            total_upload += 1
            print(entry["link"])
        else:
            continue
    db.session.commit()

    for entry in total_new:
        article = RSSArticle.query.filter_by(link=entry["link"]).first()
        category = RSSCategory.query.filter_by(link=entry["title_detail"]["base"]).first()
        article.categories.append(category)
        current = current_app.elasticsearch.get(index='article', id=str(article.id))
        try:
            current_app.elasticsearch.update(index='article', id=str(article.id), doc={'category': f'{current["_source"]["category"]} | {category.title}'})
        except KeyError:
            current_app.elasticsearch.update(index='article', id=str(article.id), doc={'category': f'{category.title}'})

    db.session.commit()
#Log upload of newfound entries
logging.basicConfig(level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), 'py_log.log'),filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
logging.info(f'We have uploaded {total_upload} new entries to the database.')