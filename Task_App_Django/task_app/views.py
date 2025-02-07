from django.shortcuts import render, HttpResponse

def home(request):
    # return render('home.html', request)
    return HttpResponse("This works!")
