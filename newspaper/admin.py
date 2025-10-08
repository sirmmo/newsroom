# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Newspaper)
admin.site.register(NewspaperSubpage)

class ArticleAdmin(admin.ModelAdmin):
    list_display=["newspaper", "scraped", "published", "title"]
    list_fliter=["newspaper"]

admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleAnalysis)

admin.site.register(ArticleAnalysisTool)