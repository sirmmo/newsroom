# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Tag)
admin.site.register(Newspaper)
admin.site.register(NewspaperSubpage)

class ArticleAdmin(admin.ModelAdmin):
    list_display=["newspaper", "enabled"]
    list_fliter=["newspaper"]

admin.site.register(NewspaperScraper)


class ArticleAnalysisInline(admin.TabularInline):
    model = ArticleAnalysis
    
class ArticleIndicatorInline(admin.TabularInline):
    model = ArticleIndicator

class ArticleAdmin(admin.ModelAdmin):
    list_display=["newspaper", "scraped", "published", "title"]
    list_fliter=["newspaper"]
    inlines= [
        ArticleAnalysisInline,
        ArticleIndicatorInline
    ]
    search_fields=['newspaper', 'title']
admin.site.register(Article, ArticleAdmin)

class ArticleAnalysisAdmin(admin.ModelAdmin):
    list_display = ["article", "analyzed", "tool", "model"]
    autocomplete_fields = ["article"]

admin.site.register(ArticleAnalysis, ArticleAnalysisAdmin)


admin.site.register(ArticleAnalysisTool)
admin.site.register(ArticleIndicator)
admin.site.register(Indicator)
admin.site.register(RunDump)