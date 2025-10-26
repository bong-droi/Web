from django.shortcuts import render
from django.http import HttpResponse

#request: yeu cau cuar nguoi dung
#response: tra ve cho nguoi dung

# Create your views here.
def index(request):
    return HttpResponse("Hello day laf app1 nhe!")