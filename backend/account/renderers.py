import json
from rest_framework import renderers

class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = {}

        if 'ErrorDetail' in str(data):
            response = {'error': data}
        else:
            response = data

        return super().render(response, accepted_media_type, renderer_context)