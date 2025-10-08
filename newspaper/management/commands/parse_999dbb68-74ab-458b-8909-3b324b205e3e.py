# LA STAMPA
from django.core.management.base import BaseCommand, CommandError
import requests
from bs4 import BeautifulSoup as bs
from newspaper.models import * 

NEWSPAPER = "999dbb68-74ab-458b-8909-3b324b205e3e"

class Command(BaseCommand):
    def handle(self, *args, **options):
        Article.objects.filter(newspaper_id=NEWSPAPER).delete()
        page = requests.get('https://www.repubblica.it').content
        ppage = bs(page).find_all(class_="block__item")
        for p in ppage:
            #print(p)
            title = p.find(class_="entry__title")
            tatt = title.find('a').attrs['href']
            ident = tatt.split('/')[-2].split('-')[-1]
            ftitle = title.text.strip().replace(u'\u201c', '"').replace(u'\u201d', '"').replace(u'\xe0',"").replace(u'\xf9',"u'")
            ctt, summary, media = self.get_article(tatt)

            a, c = Article.objects.get_or_create(newspaper_id=NEWSPAPER, in_paper_id=ident)
            a.url = tatt
            a.title = ftitle
            a.content = ctt
            a.summary = summary
            a.media = media
            a.save()
            
            
    def get_article(self, url):
        pdata = requests.get(url).content
        pdata = bs(pdata)

        ctt = ""
        try:
            summary = pdata.find(class_="story__summary").text
        except: 
            summary = ""
        try:
            media = pdata.find(class_="story__media").find('img').attrs['src']
        except: 
            media = ""
        try:
            date = pdata.find(class_="story__date").text
        except: 
            date = ""

        return ctt, summary, media