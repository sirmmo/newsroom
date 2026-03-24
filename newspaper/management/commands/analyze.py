from django.core.management.base import BaseCommand
from newspaper.models import *
from openai import OpenAI
import os
import datetime
import json

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


class Command(BaseCommand):
    def print(self, *args):
        print(" ".join([str(a) for a in args]))
        self.rd.run += " ".join([str(a) for a in args]) + "\n"
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

        client = OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
        )

        to_analyze = ArticleAnalysisTool.objects.filter(active=True)
        if options['id']:
            to_analyze = to_analyze.filter(name=options['id'])

        for aat in to_analyze:
            self.print(aat)

            for a in Article.objects.exclude(analyses__tool=aat.name, content__isnull=not aat.applies_to_content, summary__isnull=not aat.applies_to_summary):
                self.print(a)
                try:
                    prompt = None
                    if aat.applies_to_title:
                        prompt = a.title
                    if aat.applies_to_summary:
                        prompt = a.summary
                    if aat.applies_to_media:
                        prompt = a.media
                    if aat.applies_to_content:
                        prompt = a.content

                    if prompt is None:
                        continue

                    response = client.chat.completions.create(
                        model=aat.model,
                        messages=[
                            {"role": "system", "content": aat.system_prompt},
                            {"role": "user", "content": prompt},
                        ]
                    )

                    response_text = response.choices[0].message.content
                    self.print(response_text)
                    self.print('analyzed')

                    aa = ArticleAnalysis()
                    aa.article = a
                    aa.tool = aat.name
                    aa.model = aat.model
                    aa.analysis = aat.system_prompt
                    aa.result = json.loads(response_text.replace('```json', '').replace('`', ''))
                    aa.response_full = response.model_dump()
                    aa.save()

                    if aat.generates_indicators:
                        for k in aat.indicators.all():
                            try:
                                ai = ArticleIndicator()
                                ai.article = a
                                ai.analysis = aa
                                ai.indicator = k.name
                                ai.value = aa.result.get(k.name)
                                ai.explanation = aa.result.get(f'{k.name}_explain', aa.result.get(k.name))
                                ai.save()
                            except:
                                pass

                except Exception as ex:
                    self.print(ex)

        self.rd.end = datetime.datetime.now()
        self.rd.save()
