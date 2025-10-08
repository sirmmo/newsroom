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




class Article(models.Model):
    id = models.CharField(max_length=200, default=nuuid, primary_key=True)
    newspaper = models.ForeignKey(Newspaper, on_delete=models.PROTECT)
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


class ArticleAnalysis(models.Model):
    article = models.ForeignKey(Article, on_delete=models.PROTECT, related_name="analyses")
    analyzed = models.DateTimeField(auto_now_add = True)
    tool = models.CharField(max_length=2000)
    model = models.CharField(max_length=2000)
    analysis = models.CharField(max_length=2000)
    result = models.JSONField(null=True, blank=True)
    response_full = models.JSONField(null=True, blank=True)
    result_short = models.CharField(max_length=2000, null=True, blank=True)

class ArticleAnalysisTool(models.Model):
    name = models.CharField(max_length=2000)
    system_prompt = models.TextField()
    model = models.CharField(max_length=2000)
    internal_name = models.CharField(max_length=2000, null=True, blank=True)

    active = models.BooleanField(default=True)

    generates_indicators = models.BooleanField(default=True)

    indicators = models.JSONField(null=True, blank=True)
    def __str__(self):
        return self.name


class ArticleIndicator(models.Model):
    article = models.ForeignKey(Article, related_name="indicators", on_delete=models.PROTECT)
    analysis = models.ForeignKey(ArticleAnalysis, on_delete=models.PROTECT)
    indicator = models.CharField(max_length=1000)
    value = models.FloatField()
    explanation = models.TextField()