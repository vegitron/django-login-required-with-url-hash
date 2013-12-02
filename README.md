django-login-required-with-url-hash
===================================

Allows you to require authentication on Django pages that use URL hashes for state.

To install:

    pip install -e git://github.com/vegitron/django-login-required-with-url-hash#egg=LoginRequired-HashURL
  
To use in your views:

    from login_url_hash.decorators import hash_aware_login_required 
  
    @hash_aware_login_required
    def view_name(request)....
