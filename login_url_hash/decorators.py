import urllib
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.template import Context, Template

HASH_KEY_NAME = '__hash__'

def hash_aware_login_required(view_function, *wrapper_args, **wrapper_kwargs):
    login_required_decorator = login_required(view_function, *wrapper_args, **wrapper_kwargs)

    def wrapper(request, *args, **kwargs):

        params = []
        param_dict = {}
        for param in request.GET:
            if param != HASH_KEY_NAME:
                param_dict[param] = request.GET.getlist(param)
                for value in request.GET.getlist(param):
                   params.append({'k': param, 'v': value })

        # When starting auth, this key means we're ready to go to login
        # When done with auth, we need to take the hash out of the params,
        # and then redirect to the page w/ the hash
        if HASH_KEY_NAME in request.GET:
            if request.user.is_authenticated():
                new_query_string = urllib.urlencode(param_dict, doseq=True)
                url_hash = request.GET[HASH_KEY_NAME]

                url = None
                if new_query_string:
                    url = request.path+"?"+new_query_string+url_hash
                else:
                    url = request.path+url_hash

                return HttpResponseRedirect(url)
            else:
                return login_required_decorator(request, *args, **kwargs)

        if request.user.is_authenticated():
            return view_function(request, *args, **kwargs)

        template = Template(_get_template_content())
        context = Content({
            'hash_input_name': HASH_KEY_NAME,
            'params': params
        })

        return HttpResponse(template.render(context))

    return wrapper


# Doing this so the application doesn't need to be added to the installed
# applications list.
def _get_template_content():
    return """
<html>
    <head></head>
    <body>
        <form method="GET" id="hash_submit">
            <input type="hidden" name="{{ hash_input_name }}" value="">
            {% for param in params %}
            <input type="hidden" name="{{ param.k }}" value="{{ param.v }}"/>
            {% endfor %}
            <div style="position: absolute; left: -100; top: -100;">
                <input type="submit">
            </div>
            <noscript>
            <input type="submit" value="Click here to continue"/>
            </noscript>
        </form>

        <script>
            document.getElementById("hash_submit").action = document.location.href;
            document.getElementsByName("{{ hash_input_name }}")[0].value = document.location.hash;
            document.getElementById("hash_submit").submit();
        </script>
    </body>
</html>
"""

