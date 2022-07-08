import base64
import hashlib
import hmac
import os
import sys
import time
import requests
import logging

from django.views import View
import json
from django.http import JsonResponse,HttpResponse

log = logging.getLogger('mydjango')

class RecordView(View):
    def post(self, request):

        access_key = ""
        access_secret = ""
        requrl = "http://identify-cn-north-1.acrcloud.cn/v1/identify"

        http_method = "POST"
        http_uri = "/v1/identify"

        data_type = "audio"
        signature_version = "1"
        timestamp = time.time()

        string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(timestamp)

        sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'), digestmod = hashlib.sha1).digest()).decode('ascii')

        File = request.FILES.get('music', None)

        if File is None:
            return JsonResponse({ "success": False }, safe = False)
        else:
            with open("/tmp/music/%s" %File.name, 'wb+') as f:
                for chunk in File.chunks():
                    f.write(chunk)

                filename = "/tmp/music/%s" %File.name
                theFile = open(filename, "rb")
                log.info(theFile)
                sample_bytes = os.path.getsize(filename)

                files = [
                  ('sample', (File.name, open(filename, 'rb'), 'audio/mpeg'))
                ]
                data = {
                    'access_key': access_key,
                    'sample_bytes': sample_bytes,
                    'timestamp': str(timestamp),
                    'signature': sign,
                    'data_type': data_type,
                    "signature_version": signature_version
                }

                r = requests.post(requrl, files = files, data = data)
                r.encoding = "utf-8"
                log.info(r.text)
                resObj = eval(r.text)
            return JsonResponse(resObj, safe = False)
