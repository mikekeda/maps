from django.shortcuts import render


def homepage(request):
    """Homepage."""

    return render(request, 'example1.html')


def example(request, example_id):
    """Example map."""

    return render(request, 'example' + example_id + '.html')
