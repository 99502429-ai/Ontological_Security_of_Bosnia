import pandas as pd
import numpy as np
import requests
import json
import re
from bs4 import BeautifulSoup
from newsplease import NewsPlease
from easynmt import EasyNMT
from torch import cuda
import nltk

# Languages: bs-BA, hr-HR, sr-SP-Cyrl, en-US

def getPresidencyPages(language: str) -> list:
  index = 1
  pres_site = 'https://www.predsjednistvobih.ba/gov/Archive.aspx?langTag=' + language + '&template_id=156&pageIndex='
  speech_ids = []

  while True:
    page = pres_site + str(index)

    r = requests.get(page)
    soup = BeautifulSoup(r.text, "html.parser")
    tags = soup.find_all('a', href=re.compile(r'/gov/\?id=\d+'))
    for tag in tags:
      id = re.search(r'\d{5,}', str(tag))
      if id: # Check if id is not None
        speech_ids.append(id.group())
      else:
        break   
    index += 1
  return speech_ids

def getSpeechs(speech_ids: list, language: str):
  titles = []
  speech_urls = []
  publish_date = []
  content = []
  for id in speech_ids:
    speech_url = 'https://www.predsjednistvobih.ba/gov/default.aspx?id=' + id + '&langTag=' + language
    speech = NewsPlease.from_url(speech_url)
    titles.append(speech.title)
    speech_urls.append(speech_url)
    publish_date.append(speech.date_publish)
    content.append(speech.maintext)
  return pd.DataFrame({
      'id': speech_ids,
      'title': titles,
      'speech_url': speech_urls,
      'publish_date': publish_date,
      'content': content
  })

def singleCrawl(language: str, fileName):
  speech_ids = getPresidencyPages(language=language)
  print("Speech Ids:" + len(speech_ids))
  df = getSpeechs(speech_ids, language)
  df.to_csv(fileName, encoding="utf-8")
  print("Done")
