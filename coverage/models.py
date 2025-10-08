# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from events.models import * 
from newspaper.models import * 

# Create your models here.

class EventCoverage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    article = models.ForeignKey(Article, on_delete=models.PROTECT)