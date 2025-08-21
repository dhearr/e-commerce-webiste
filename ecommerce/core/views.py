from django.shortcuts import render

# Create your views here.
def index(request):
  context = {
    "head_title": "Sellara | E-Commerce Website"
  }
  return render(request, 'core/index.html', context)