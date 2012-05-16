# Create your views here.
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello world!!! NOTES ALL UP IN HERE")