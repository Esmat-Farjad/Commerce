
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.translation import activate
from django.conf import settings

# Create your views here.
def Landing(request):
    return render(request, 'landing-page.html')

def Home(request):
    return render(request, 'home.html')

def switch_language(request, lang_code):
    if lang_code in dict(settings.LANGUAGES):  # ✅ Ensure the language is valid
        activate(lang_code)
        request.session['django_language'] = lang_code  # ✅ Store in session

        # ✅ Store the language in a cookie
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', lang_code, max_age=31536000)  # 1 year
        return response

    return redirect('/')
