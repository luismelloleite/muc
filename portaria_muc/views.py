from django.shortcuts import render

def generic_error_view(request, exception=None, status_code=None):
    if hasattr(exception, 'status_code'):
        status_code = exception.status_code

    if status_code is None:
        status_code = 500

    context = {'status_code': status_code}
    return render(request, 'errors/generic_error.html', context, status=status_code)