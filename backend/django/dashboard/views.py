from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import Http404

from .models import Data



def home(request):

    data = Data.objects.all()

    return render(request, 'index.html', {'data': data})