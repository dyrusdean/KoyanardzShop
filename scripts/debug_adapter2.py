from allauth.socialaccount.adapter import get_adapter
from django.test.client import RequestFactory
from allauth.socialaccount import providers

rf = RequestFactory()
req = rf.get('/')
adapter = get_adapter(req)
print('Adapter class:', adapter.__class__)
provider_cls = providers.registry.provider_map.get('google')
print('Provider class:', provider_cls)
provider_id = getattr(provider_cls, 'id', None)
print('Provider id:', provider_id)
try:
    app = adapter.get_app(req, provider_id)
    print('App id:', app.id, 'client_id', app.client_id)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Exception type:', type(e), e)
