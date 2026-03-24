#BBC


from django.core.management.base import BaseCommand, CommandError
import requests
from newspaper.models import * 

import ollama

import json

class Command(BaseCommand):
    def handle(self, *args, **options):

        oc = ollama.Client(host="http://51.15.160.236:11434")

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
            
