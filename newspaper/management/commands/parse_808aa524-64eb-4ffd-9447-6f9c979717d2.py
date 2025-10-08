from django.core.management.base import BaseCommand, CommandError
import requests
from bs4 import BeautifulSoup as bs
from newspaper.models import * 

import datetime

NEWSPAPER = "808aa524-64eb-4ffd-9447-6f9c979717d2"

class Command(BaseCommand):
    def handle(self, *args, **options):
        Article.objects.filter(newspaper_id=NEWSPAPER).delete()
        for pages in [
            "https://www.ilpost.it",
            "https://www.ilpost.it/italia/",
            "https://www.ilpost.it/mondo/",
            "https://www.ilpost.it/politica/",
            "https://www.ilpost.it/tecnologia/",
            "https://www.ilpost.it/internet/",
            "https://www.ilpost.it/scienza/",
            "https://www.ilpost.it/cultura/",
            "https://www.ilpost.it/economia/",
            "https://www.ilpost.it/sport/",
            "https://www.ilpost.it/moda/",
            "https://www.ilpost.it/libri/",
            "https://www.ilpost.it/consumismi/",
            "https://www.ilpost.it/storie-idee/",
            "https://www.ilpost.it/ok-boomer/"
        ]:
            page = requests.get(pages).content
            ppage = bs(page).find(class_='container').find_all("article")
            for p in ppage:
                if "podcast" in " ".join(p.attrs['class']):
                    tatt = p.find_parent().attrs['href']
                    ftitle = p.text.strip()
                else: 
                    tatt = p.find('a').attrs['href']
                    ident = tatt.split('/')[-2]
                    ftitle = p.text.strip()
                    
                print(ftitle)
                ctt, sry, media, date = self.get_article(tatt)

                a, c = Article.objects.get_or_create(newspaper_id=NEWSPAPER, in_paper_id=ident)
                a.url = tatt
                a.title = ftitle
                a.content = ctt
                a.summary = sry
                a.media = media
                a.published = date
                a.save()

            
    def get_article(self, url):
        pdata = requests.get(url).content
        pdata = bs(pdata)

        try:
            ctt = pdata.find(class_="contenuto").text
        except: 
            ctt = ""
        try:
            summary = pdata.find('h2').text
        except: 
            summary = ""
        try:
            media = pdata.find('img').attrs['src']
        except: 
            media = ""
        try:
            date = pdata.find(class_="story__date").text
        except: 
            date = datetime.datetime.now()

        return ctt, summary, media, date