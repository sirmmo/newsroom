#BBC


from django.core.management.base import BaseCommand, CommandError
import requests
from newspaper.models import * 

import ollama

from openai import OpenAI

OPENROUTER_API_KEY="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"

import datetime

import json

class Command(BaseCommand):
    def print(self, *args):
        print(" ".join([str(a) for a in args]))
        self.rd.run += " ".join([str(a) for a in args])+"\n"
        self.rd.save()

    def add_arguments(self, parser):
        parser.add_argument("--id", nargs="?", type=str)
        parser.add_argument("--rd", nargs="?", type=str)
    def handle(self, *args, **options):

        if options['rd']:
            self.rd = RunDump.objects.get(id=options['rd'])
        else:
            self.rd = RunDump()
        self.rd.action = "analyze"
        self.rd.start = datetime.datetime.now()
        self.rd.run = ""
        self.rd.save()

        oc = ollama.Client(host="http://51.15.160.236:11434")

        
        oaiclient = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        models = oc.list()
        avail_models = []
        for m in models.models:
            avail_models.append(m.model)

        req_models = []
        gen_models = []
        for aat in ArticleAnalysisTool.objects.all():
            if aat.model not in avail_models:
                oc.pull(aat.model)
            if aat.internal_name not in avail_models:
                oc.create(model=aat.internal_name, from_=aat.model, system=aat.system_prompt)

        to_analyze =  ArticleAnalysisTool.objects.filter(active=True)
        if options['id']:
            to_analyze = to_analyze.filter(name=options['id'])

        for aat in to_analyze:
            self.print(aat)

            for a in Article.objects.exclude(analyses__tool=aat.name, content__isnull=not aat.applies_to_content, summary__isnull=not aat.applies_to_summary):
                self.print(a)
                d = None
                try:
                    if aat.applies_to_title:
                        d = oc.generate(model=aat.internal_name, prompt=a.title)
                    if aat.applies_to_summary:
                        d = oc.generate(model=aat.internal_name, prompt=a.summary)
                    if aat.applies_to_media:
                        d = oc.generate(model=aat.internal_name, prompt=a.media)
                    if aat.applies_to_content:
                        d = oc.generate(model=aat.internal_name, prompt=a.content)

                    self.print(d)

                    self.print('analyzed')

                    aa = ArticleAnalysis()
                    aa.article = a
                    aa.tool = aat.name
                    aa.model = aat.model
                    aa.analysis = aat.system_prompt
                    aa.result = json.loads(d.response.replace('```json','').replace('`', ''))
                    aa.response_full = d.response

                    aa.save()

                    if aat.generates_indicators:
                        for k in aat.indicators.all():
                            try:
                                ai = ArticleIndicator()
                                ai.article = a
                                ai.nalysis = aa
                                ai.indicator = k.name
                                ai.value = aa.result.get(k)
                                ai.explanation=aa.result.get(f'{k}_explain', result.get(k))
                                ai.save()
                            except:
                                pass 
                

                except Exception as ex:
                    self.print(ex)
        
        
        self.rd.end = datetime.datetime.now()
        self.rd.save()
