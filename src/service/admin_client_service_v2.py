import hashlib
import json
import random
import sys
import time

from ..core.facade import f_t_cache, f_gct
from ..utils.tools import create_http_session, generate_guid, is_json, get_device_uuid
from ...config.config import APP_VERSION, NETWORK_DRIVE_HOST, NETWORK_DRIVE_SECRET_KEY, IS_DEBUG
from .encrypt import Encrypt
from ..exceptions.AdminClientService415 import AdminClientService415
from ..exceptions.hoo_execption import HooException


class AdminClientServiceV2:
    def __init__(self, **kwargs):
        self.session = create_http_session(verify=False)

    def res_out(self, res):
        if res.status_code != 200:
            raise Exception('无法连接到服务器！请稍后再试')
        if not is_json(res.text):
            return res.text
        res_json = res.json()
        if res_json['code'] == 200:
            return res_json['data']
        elif res_json['code'] == 415:
            raise AdminClientService415(res_json['message'])
        else:
            raise HooException(res_json['message'], res_json['code'])

    def make_cache_key(self, api, data):
        raw = f"{api}:{json.dumps(data, sort_keys=True)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def http_post(self, api, json=None, timeout=10, ttl=None):
        if json is None:
            json = {}

        def get(api, json=None, timeout=None):
            res = self.session.post(
                url=f'{NETWORK_DRIVE_HOST}{api}',
                json=json,
                timeout=timeout
            )
            return self.res_out(res)
        if ttl:
            key = self.make_cache_key(api, json)
            return f_t_cache().remember(key, ttl, lambda: get(api, json, timeout))
        else:
            return get(api, json, timeout)

    def http_get(self, api, json=None, timeout=10, ttl=None):
        if json is None:
            json = {}

        def get(api, json=None, timeout=None):
            res = self.session.get(
                url=f'{NETWORK_DRIVE_HOST}{api}',
                json=json,
                timeout=timeout
            )
            return self.res_out(res)

        if ttl:
            key = self.make_cache_key(api, json)
            return f_t_cache().remember(key, ttl, lambda: get(api, json, timeout))
        else:
            return get(api, json, timeout)