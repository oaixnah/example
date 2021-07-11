import requests


def get_token(corp_id: str, corp_secret: str):
    """获取access_token
    https://open.work.weixin.qq.com/api/doc/90000/90135/91039
    """
    req = requests.get(
        f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}'
    )
    return req.json().get('access_token')
