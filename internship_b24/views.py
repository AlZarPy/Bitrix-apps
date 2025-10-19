from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def index(request):
    return render(request, "internship_b24/index.html")

def module1(request): return HttpResponse("Модуль 1: заглушка")
def module2(request): return HttpResponse("Модуль 2: заглушка")
def module3(request): return HttpResponse("Модуль 3: заглушка")
def module4(request): return HttpResponse("Модуль 4: заглушка")
def module5(request): return HttpResponse("Модуль 5: заглушка")

def oauth_bitrix(request):
    return HttpResponse("OAuth handler OK", status=200)
