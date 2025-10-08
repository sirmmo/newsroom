# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid

def nuuid():
    return str(uuid.uuid4())

# Create your models here.

class Event(models.Model):
    id = models.CharField(max_length=200, default=nuuid, primary_key=True)
    name = models.CharField(max_length=2000)
    date = models.CharField(max_length=20, null=True, blank=True)
    time = models.CharField(max_length=20, null=True, blank=True)

    description = models.TextField()

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class EventGroup(models.Model):
    id = models.CharField(max_length=200, default=nuuid, primary_key=True)
    name = models.CharField(max_length=2000)

    events = models.ManyToManyField(Event)

    
    def __str__(self):
        return self.name