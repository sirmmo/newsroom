# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid

def nuuid():
    return str(uuid.uuid4())

# Create your models here.

class Tag(models.Model):
    category = models.CharField(max_length=2000)
    name = models.CharField(max_length=2000)

    def __str__(self):
        return self.category + ":" + self.name

class Newspaper(models.Model):
    id = models.CharField(max_length=200, default=nuuid, primary_key=True)
    name = models.CharField(max_length=2000)
    base_url = models.CharField(max_length=2000)
    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def __str__(self):
        return self.name

class NewspaperSubpage(models.Model):
    newspaper = models.ForeignKey(Newspaper, on_delete=models.PROTECT, related_name = "pages")
    url = models.URLField()


    def __str__(self):
        return self.url

class NewspaperScraper(models.Model):
    newspaper = models.ForeignKey(Newspaper, on_delete=models.PROTECT, related_name = "scrapers")
    urls = models.ManyToManyField(NewspaperSubpage, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    scraper = models.TextField()

    def __str__(self):
        return f"{self.newspaper}: {urls.all().count()}"

from simple_history import register
register(NewspaperScraper)


class NewspaperFeed(models.Model):
    newspaper = models.ForeignKey(Newspaper, on_delete=models.PROTECT, related_name="feeds")
    url = models.URLField()
    fmt = models.CharField(max_length=200)


class Article(models.Model):
    id = models.CharField(max_length=200, default=nuuid, primary_key=True)
    newspaper = models.ForeignKey(Newspaper, on_delete=models.PROTECT, related_name="articles")
    in_paper_id = models.CharField(max_length=2000)
    url = models.CharField(max_length=2000)
    scraped = models.DateTimeField(auto_now_add = True)
    published = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=2000)
    media = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=2000, null=True, blank=True)

    archve_org=models.CharField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.newspaper.name + " - " + self.title
    class Meta:
        ordering=["-scraped"]


class ArticleAnalysis(models.Model):
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name="analyses")
    analyzed = models.DateTimeField(auto_now_add = True)
    tool = models.CharField(max_length=2000)
    model = models.CharField(max_length=2000)
    analysis = models.CharField(max_length=2000)
    result = models.JSONField(null=True, blank=True)
    response_full = models.JSONField(null=True, blank=True)
    result_short = models.TextField(null=True, blank=True)

    class Meta:
        ordering=["-analyzed"]

    


class Indicator(models.Model):
    name = models.CharField(max_length=2000)
    description = models.TextField()
    datatype = models.CharField(max_length=2000)

    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

    min_value_label = models.CharField(max_length=2000)
    max_value_label = models.CharField(max_length=2000)


class ArticleAnalysisTool(models.Model):
    name = models.CharField(max_length=2000)
    system_prompt = models.TextField()
    model = models.CharField(max_length=2000)
    internal_name = models.CharField(max_length=2000, null=True, blank=True)

    applies_to_title = models.BooleanField(default=False)
    applies_to_content = models.BooleanField(default=True)
    applies_to_media = models.BooleanField(default=False)
    applies_to_summary = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    generates_indicators = models.BooleanField(default=True)

    indicators = models.ManyToManyField(Indicator)
    def __str__(self):
        return self.name




class ArticleIndicator(models.Model):
    article = models.ForeignKey(Article, related_name="indicators", on_delete=models.PROTECT)
    analysis = models.ForeignKey(ArticleAnalysis, on_delete=models.PROTECT)
    indicator = models.CharField(max_length=1000)
    value = models.FloatField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)

class RunDump(models.Model):
    action = models.CharField(max_length=2000, null=True, blank=True)
    run = models.TextField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.action}@{self.start}"