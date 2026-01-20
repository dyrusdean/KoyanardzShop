from allauth.socialaccount.adapter import get_adapter
from django.test.client import RequestFactory
from allauth.socialaccount.providers import registry

rf = RequestFactory()
req = rf.get('/')
adapter = get_adapter(req)
print('Adapter class:', adapter.__class__)
provider = registry.by_id('google', None)
print('Provider:', provider)
try:
    app = adapter.get_app(req, provider.id)
    print('App id:', app.id, 'client_id', app.client_id)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Exception type:', type(e), e)
