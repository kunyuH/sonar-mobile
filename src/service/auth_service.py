from datetime import datetime
from .admin_client_service import AdminClientService
from ..core.facade import f_gct


class Auth:
    def get_super_key(self):
        return f_gct().get('super_key')

    def set_super_key(self, super_key):
        f_gct().set('super_key', super_key)

    def get_key_info(self, ttl=60 * 60 * 0.5):
        super_key = self.get_super_key()
        if not super_key:
            raise Exception('请先设置key！')

        data = {'key': super_key}
        result = AdminClientService().http_post(
            api='/open/key/info',
            data=data,
            timeout=None,
            ttl=None
        )

        expire_date = result.get('expire_date')
        if expire_date:
            expire_time = datetime.strptime(expire_date, '%Y-%m-%d %H:%M:%S')
            if datetime.now() > expire_time:
                raise Exception('授权已经过期！')
        else:
            raise Exception('授权异常！')

        return result