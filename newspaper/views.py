# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .models import * 
from ninja import NinjaAPI
from ninja.pagination import paginate
import json
from ninja import Schema, ModelSchema
from typing import List, Dict
from django.db.models import Avg, Count

#from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from django.http import Http404
#from ninja_jwt.authentication import JWTAuth

#from ninja_jwt.routers.obtain import obtain_pair_router, sliding_router
#from ninja_jwt.routers.verify import verify_router


api = NinjaAPI(title="Newsroom Watch", version="1.0.0")
#api.register_controllers(NinjaJWTDefaultController)
#api.add_router('/auth/token', tags=['Auth'], router=obtain_pair_router)
#api.add_router('/auth/verify', tags=['Auth'], router=verify_router)


def get_inicators_for_items(articles):
    ixs = Indicator.objects.filter(datatype="float")
    aides = ArticleIndicator.objects.filter(article__in=articles)
    ret = {}
    for ix in ixs:
        ret[ix.name] = {
            "value": aides.filter(indicator=ix.name).aggregate(mean=Avg("value"))['mean'], 
            "count": aides.filter(indicator=ix.name).count(),
            "min": ix.min_value,
            "max": ix.max_value,
            "label": ix.name,
        }
    return ret


@api.get('/')
def get_index(request):
    return {
        "numbers":{
            "newspapers": Newspaper.objects.all().count(),
            "articles": Article.objects.all().count(),
            "analyses": ArticleAnalysis.objects.all().count(),
            "tools": ArticleAnalysisTool.objects.all().count(),
            "indicators": get_inicators_for_items(Article.objects.all())

        },
        "tags": [{"id": t.id, "cat": t.category, "name": t.name, "indicators": get_inicators_for_items(Article.objects.filter(newspaper__tags=t))} for t in Tag.objects.all()]
    }




class IndicatorSchema(ModelSchema):
    class Meta:
        model=ArticleIndicator
        fields = "__all__"

class BaseAnnotatedArticleSchema(ModelSchema):
    indicators: Dict
    class Meta:
        model=Article
        exclude=["content", "summary", "newspaper"]

    
    @staticmethod
    def resolve_indicators(obj):
        return get_inicators_for_items([obj])



class AnnotatedArticleSchema(BaseAnnotatedArticleSchema):
    indicators: Dict
    class Meta:
        model=Article
        exclude=["content", "summary", "newspaper"]

    
    @staticmethod
    def resolve_indicators(obj):
        return get_inicators_for_items([obj])

        

class ArticleAnalysisSchema(ModelSchema):
    class Meta:
        model=ArticleAnalysis
        exclude=['article']
        


class AnnotatedFullArticleSchema(BaseAnnotatedArticleSchema):
    analyses: List[ArticleAnalysisSchema]
    class Meta:
        model=Article
        exclude=["content", "newspaper"]
        
    @staticmethod
    def resolve_analyses(obj):
        return obj.analyses.all()

@api.get("/article", response=AnnotatedArticleSchema)
def add(request, url):
    try:
        a = Article.objects.get(url=url)
        return a
    except:
        raise Http404()

class TagSchema(ModelSchema):
    indicators: Dict
    class Meta:
        model=Tag
        fields="__all__"
    @staticmethod
    def resolve_indicators(obj):
        return get_inicators_for_items(Article.objects.filter(newspaper__tags=obj))


class NewspaperSchema(ModelSchema):
    indicators: Dict
    articles: int
    tags: List[TagSchema]
    class Meta:
        model=Newspaper
        fields="__all__"
        
    @staticmethod
    def resolve_indicators(obj):
        return get_inicators_for_items(obj.articles.all())
    @staticmethod
    def resolve_articles(obj):
        return obj.articles.count()

        
class NewspaperListSchema(ModelSchema):
    indicators: Dict
    articles: int
    class Meta:
        model=Newspaper
        fields="__all__"
        
    @staticmethod
    def resolve_indicators(obj):
        return get_inicators_for_items(obj.articles.all())
    @staticmethod
    def resolve_articles(obj):
        return obj.articles.count()

class TagSchema(ModelSchema):
    indicators: Dict
    class Meta:
        model=Tag
        fields="__all__"
        
    @staticmethod
    def resolve_indicators(obj):
        return get_inicators_for_items(Article.objects.filter(newspaper__tags=obj))


@api.get("/newspapers", response=List[NewspaperListSchema])
@paginate
def get_newspapers(request, mode="parsed"):
    if mode == "parsed":
        return Newspaper.objects.annotate(c=Count('articles')).filter(c__gt=0)
    elif mode == "all": 
        return Newspaper.objects.all()


@api.get("/newspapers/{nid}", response=NewspaperSchema)
def get_newspaper(request, nid):
    return Newspaper.objects.get(id=nid)


@api.get("/newspapers/{nid}/articles", response=List[AnnotatedArticleSchema])
@paginate
def get_newspaper_articles(request, nid):
    return Article.objects.filter(newspaper_id=nid)

    
@api.get("/newspapers/{nid}/articles/{aid}", response=AnnotatedFullArticleSchema)
def get_newspaper_article(request, nid, aid):
    return Article.objects.get(id=aid)


@api.get("/newspapers/{nid}/scrapers")
def get_newspaper_scrapers(request, nid):
    ret = []
    for s in NewspaperScraper.objects.filter(newspaper_id=nid):
        ret.append({
            "code": s.scraper,
            "urls": [{"id": su.id, "url":su.url} for su in s.urls.all()],
            "id": s.id,
            "history": [{"id": h.history_id, "date":h.history_date} for h in s.history.all()]
        })

    return ret

@api.post('/newspapers/{nid}/scrapers')
def create_scraper(request, nid):
    ns = NewspaperScraper()
    ns.newspaper_id = nid
    ns.enabled  = False
    ns.scraper = "code here..."
    ns.save()

    return {"response": "ok", "id": ns.id}

@api.post("/newspapers/{nid}/scrapers/{sid}/code")
def update_code(request, nid, sid):
    code = json.loads(request.body)
    code = code.get('code')

    s = NewspaperScraper.objects.get(newspaper_id=nid, id=sid)
    s.scraper = code
    s.save()

    return {"response":"ok"}

@api.post("/newspapers/{nid}/scrapers/{sid}/urls")
def add_url_to_scraper(request, nid, sid, url):
    ns = NewspaperSubpage()
    ns.newspaper_id = nid
    ns.url = url 
    ns.save()
    nsc = NewspaperScraper.objects.get(newspaper_id=nid, id=sid)
    nsc.urls.add(ns)
    nsc.save()

    return {"response":"ok"}

@api.delete("/newspapers/{nid}/scrapers/{sid}/urls/{uid}")
def del_url_from_scraper(request, nid,sid,uid):
    NewspaperSubpage.objects.flter(newspaper_id=nid, id=uid).delete()
    return {"response":"ok"}




from threading import Thread

def do_call_command(action, parameters):
    from django.core.management import call_command
    call_command(action, *parameters)


@api.post('/run/{action}')
def run_action(request, action):
    if action in ['analyze', 'parse', 'prepare']:

        rd = RunDump()
        rd.save()
        try:
            params = json.loads(request.body)
        except:
            params = {}

        params["--rd"] = rd.id
        linear_params = []
        for k,v in params.items():
            linear_params += [str(k),str(v)]
        t = Thread(target=do_call_command, args=(action, params))
        t.start()
        return {"response": "ok", "action": action, "status": "running", "log": rd.id}
    else:
        return {"response": "nok", "action": action, "status": "not available"}

    

class ToolSchema(ModelSchema):
    class Meta:
        model = ArticleAnalysisTool
        fields = "__all__"

@api.get('/tools', response=List[ToolSchema])
@paginate
def get_tools(request):
    return ArticleAnalysisTool.objects.all()



@api.get('/log/{lid}')

def get_log(request, lid):
    return {"log": RunDump.objects.get(id=lid).run}