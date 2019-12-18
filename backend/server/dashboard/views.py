from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import Http404

from .models import Current_status



def home(request):
    current_status = Current_status.objects.all()

    return render(request, 'index.html', {'current_status': current_status})