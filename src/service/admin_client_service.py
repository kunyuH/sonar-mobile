import hashlib
import json
import random
import sys
import time

import requests

from ..core.facade import f_t_cache, f_gct
from ..utils.tools import generate_guid, is_json, get_device_uuid
from ...config.config import APP_VERSION, NETWORK_DRIVE_HOST, NETWORK_DRIVE_SECRET_KEY, IS_DEBUG
from .encrypt import Encrypt
from ..exceptions.AdminClientService415 import AdminClientService415
from ..exceptions.hoo_execption import HooException


class AdminClientService:
    def __init__(self, **kwargs):
        pass

    def rep(self, data=None):
        if data is None:
            data = {}
        if not data.get('key'):
            from .auth_service import Auth
            data['key'] = Auth().get_super_key()
        if not data.get('info'):
            if sys.platform == "android" or sys.platform == "linux":
                from ascript.android.system import Device
                data['info'] = json.dumps({
                    'platform': 'android',
                    'version': Device.version(),
                    'brand': Device.brand(),
                    'model': Device.model(),
                    'name': Device.name(),
                    'device_name': f_gct().get('device_name', ''),
                })
            elif sys.platform == "ios":
                data['info'] = json.dumps({
                    'name': "iOS",
                    'device_name': f_gct().get('device_name', ''),
                })


        data['uuid'] = get_device_uuid()
        data['version'] = APP_VERSION
        data['key_type'] = 'mobile-script'

        data_json = json.dumps({
            'data': data,
            'timestamp': int(time.time() * 1000),
            'randomStr': generate_guid(),
            'random': random.randint(100000, 999999)
        })
        return Encrypt(NETWORK_DRIVE_SECRET_KEY).sm4_encrypt(data_json)

    def res_out(self, res):
        if res.status_code != 200:
            raise Exception('无法连接到服务器！请稍后再试')
        if not is_json(res.text):
            return res.text
        res_json = res.json()
        if res_json['code'] == 200:
            data_json = Encrypt(NETWORK_DRIVE_SECRET_KEY).sm4_decrypt(res_json['data'])
            if not data_json:
                raise Exception('异常数据！')
            data = json.loads(data_json)
            if int(time.time() * 1000) - int(data['timestamp']) > (3600 * 24 * 1000):
                raise Exception('数据已失效！')

            if IS_DEBUG:
                print("#################### AdminClientService 日志 ####################")
                print(data['data'])
            return data['data']
        elif res_json['code'] == 415:
            raise AdminClientService415(res_json['message'])
        else:
            raise HooException(res_json['message'], res_json['code'])

    def make_cache_key(self, api, data):
        raw = f"{api}:{json.dumps(data, sort_keys=True)}"
        return hashlib.md5(raw.encode()).hexdigest()

    def http_post(self, api, data=None, timeout=10, ttl=None):
        if data is None:
            data = {}

        ciphertext = self.rep(data)
        def get(api, ciphertext=None, timeout=None):
            res = requests.post(
                url=f'{NETWORK_DRIVE_HOST}{api}',
                data={
                    'ciphertext': ciphertext,
                },
                timeout=timeout
            )
            return self.res_out(res)
        if ttl:
            key = self.make_cache_key(api, data)
            return f_t_cache().remember(key, ttl, lambda: get(api, ciphertext, timeout))
        else:
            return get(api, ciphertext, timeout)

    def http_get(self, api, json=None, timeout=10, ttl=None):
        if json is None:
            json = {}

        ciphertext = self.rep(json)
        def get(api, ciphertext=None, timeout=None):
            res = requests.get(
                url=f'{NETWORK_DRIVE_HOST}{api}',
                json={
                    'ciphertext': ciphertext,
                },
                timeout=timeout
            )
            return self.res_out(res)

        if ttl:
            key = self.make_cache_key(api, json)
            return f_t_cache().remember(key, ttl, lambda: get(api, ciphertext, timeout))
        else:
            return get(api, ciphertext, timeout)