from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def courses(request):
    return render(request, 'courses.html')

def materials(request):
    return render(request, 'materials.html')

def tests(request):
    return render(request, 'tests.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')