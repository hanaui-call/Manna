from django.http import JsonResponse
from django.shortcuts import render


def test(request):
    data = {
        'name': 'Luffy',
        'location': 'Korea',
        'is_active': True,
        'age': 38
    }
    return JsonResponse(data)


def index(request):
    data = {
        'name': 'Hello World'
    }
    return render(request, 'index.html', data)
