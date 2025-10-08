#BBC


from django.core.management.base import BaseCommand, CommandError
import requests
from newspaper.models import * 

import ollama

import json

class Command(BaseCommand):
    def handle(self, *args, **options):

        oc = ollama.Client(host="http://51.15.160.236:11434")

        for aat in ArticleAnalysisTool.objects.filter(active=True):

            for a in Article.objects.exclude(analyses__tool=aat.name):
                try:
                    if(a.content):
                        d = oc.generate(model=aat.internal_name, prompt=a.content)
                    elif a.summary:
                        d = oc.generate(model=aat.internal_name, prompt=a.content)


                    aa = ArticleAnalysis()
                    aa.article = a
                    aa.tool = aat.name
                    aa.model = aat.model
                    aa.analysis = aat.system_prompt
                    aa.result = json.loads(d.response.replace('```json','').replace('`', ''))
                    #aa.response_full = json.dumps(d)

                    aa.save()
                except Exception as ex:
                    print(ex)
                
