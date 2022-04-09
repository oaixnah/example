# coding:utf-8

"""
    更新 企业微信 回调 安全组
"""

import requests


import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.vpc.v20170312 import vpc_client, models

SecretId = ''
SecretKey = ''


def modify_security_group_policies(region: str, sg_id: str, ip_list: list, post: list) -> dict:
    """
    修改安全组出站和入站规则
    https://cloud.tencent.com/document/product/215/15810
    :param str region:      ap-beijing
    :param str sg_id:       sg-***
    :param list ip_list:    ['119.147.179.37', '120.232.65.26', ...]
    :param list post:       ['80', '443', ...]
    :return:
    """
    ingress = [{"Protocol": "TCP", "Port": j, "CidrBlock": i, "Action": "ACCEPT"} for i in ip_list for j in post]
    try:
        cred = credential.Credential(SecretId, SecretKey)
        http_profile = HttpProfile()
        http_profile.endpoint = "vpc.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = vpc_client.VpcClient(cred, region, client_profile)

        req = models.ModifySecurityGroupPoliciesRequest()
        params = {
            "SecurityGroupId": sg_id,
            "SecurityGroupPolicySet": {
                "Ingress": ingress
            }
        }
        req.from_json_string(json.dumps(params))

        resp = client.ModifySecurityGroupPolicies(req)
        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)


def get_callback_ip(access_token: str) -> list:
    """
    获取企业微信服务器的ip段
    https://developer.work.weixin.qq.com/document/path/90930
    :param str access_token:
    :return:    ['119.147.179.37', '120.232.65.26', ...]
    """
    req = requests.get(f'https://qyapi.weixin.qq.com/cgi-bin/getcallbackip?access_token={access_token}')
    return req.json().get('ip_list')
