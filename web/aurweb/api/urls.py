#!/usr/bin/env python3
from django.urls import path
from .views import RPCView

urlpatterns = [
    path('rpc/', RPCView.as_view(), name='rpc'),
]


