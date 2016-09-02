from django.shortcuts import render


def index(request):
    """
    Main page of the site. List of all locations.
    """
    return render(request, 'boiska/index.html')
