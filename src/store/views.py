
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.translation import activate

# Create your views here.
def Home(request):
    return render(request, 'landing-page.html')




def switch_language(request, lang_code):
    activate(lang_code)
    request.session['django_language'] = lang_code
    return redirect(request.META.get('HTTP_REFERER', '/'))
