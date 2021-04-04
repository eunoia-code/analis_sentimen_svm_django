from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'rows': 'Hello',
    }
    return render(request, 'dashboard.html', context)
