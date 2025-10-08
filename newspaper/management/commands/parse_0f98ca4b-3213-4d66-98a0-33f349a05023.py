#BBC


from django.core.management.base import BaseCommand, CommandError
import requests
from bs4 import BeautifulSoup as bs
from newspaper.models import * 

NEWSPAPER = "0f98ca4b-3213-4d66-98a0-33f349a05023"

class Command(BaseCommand):
    def handle(self, *args, **options):
        Article.objects.filter(newspaper_id=NEWSPAPER).delete()
        page = requests.get('https://www.bbc.com/news').content
        ppage = bs(page).find_all(attrs={"data-testid":"anchor-inner-wrapper"})
        for p in ppage:
            if "svg" in str(p):
                continue
            print(p)
            tatt = p.find('a').attrs['href']
            ident = tatt.split('/')[-1]
            title = p.find(attrs={"data-testid":"card-headline"}).text
            summary = p.find(attrs={"data-testid":"card-description"}).text
            ctt, media, author = self.get_article(tatt)

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

        try:
            text_blocks = pdata.find_all(attrs={"data-component":"text-block"})
            text_blocks = [t.text for t in textblock]
            ctt = "\n".join(text_blocks)
        except: 
            ctt = ""
        try:
            media = pdata.find(attrs={"data-component":"image-block"}).find('img').attrs['src']
        except: 
            media = ""
        try:
            author = pdata.find(attrs={"data-testid":"byline-new-contributors"}).text
        except: 
            author = ""

        return ctt, media, author