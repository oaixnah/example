# coding:utf-8

"""
    腾讯云 云监控数据 保存为 图片
"""

import json
import time
import io
import hashlib
import base64
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.font_manager as fm

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.monitor.v20180724 import monitor_client, models

SecretId = ''
SecretKey = ''


def get_monitor_data(name_space, metric_name, instances, start_time, end_time=None, region='ap-beijing'):
    """
    拉取指标监控数据
    https://cloud.tencent.com/document/api/248/31014
    :param str name_space:          QCE/CDB
    :param str metric_name:         MemoryUseRate
    :param list instances:          [{"Dimensions": [{"Name": "InstanceId", "Value": "ins-***"}, ...]}]
    :param str start_time:          2021-05-26T00:00:00+08:00
    :param str end_time:            2021-05-26T00:00:00+08:00
    :param str region:              ap-beijing
    :return:
    """
    try:
        cred = credential.Credential(SecretId, SecretKey)
        http_profile = HttpProfile()
        http_profile.endpoint = "monitor.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = monitor_client.MonitorClient(cred, region, client_profile)

        req = models.GetMonitorDataRequest()
        params = {
            "Namespace": name_space,
            "MetricName": metric_name,
            "StartTime": start_time,
            "EndTime": end_time,
            "Instances": instances,
            "Period": 60
        }
        req.from_json_string(json.dumps(params))

        return json.loads(client.GetMonitorData(req).to_json_string())

    except TencentCloudSDKException as err:
        print(err)
        return []


def data_to_img(m_data, fig_size=(6, 3), dpi=200):
    """
    保存成图片 或 返回图片
    :param dict m_data:
    :param tuple fig_size:      图片宽高比
    :param int dpi:             dpi
    :return:
    """
    for d in m_data["DataPoints"]:
        fig, ax = plt.subplots(figsize=fig_size)
        x = [time.strftime('%H:%M', time.localtime(i)) for i in d['Timestamps']]
        ax.plot(x, d['Values'])
        ax.xaxis.set_major_locator(ticker.MultipleLocator(len(x) // 6))
        plt.title(d["Dimensions"][0]["Value"])
        plt.grid(True)
        plt.ylabel(m_data.get('MetricName'), fontproperties=fm.FontProperties())

        # ins-***_CPUUsage.png
        plt.savefig(f'{d["Dimensions"][0]["Value"]}_{m_data["MetricName"]}.png', dpi=dpi)

        # 通过其他方式存储
        # s = io.BytesIO()
        # plt.savefig(s, dpi=200, format='png')
        # return s.getvalue(), hashlib.md5(s.getvalue()).hexdigest()

        # 返回base64信息，例如 利用企业微信发送图片
        # return base64.b64encode(s.read()), hashlib.md5(s.getvalue()).hexdigest()


if __name__ == '__main__':
    # 例子如下
    ins = [
            {
                "Dimensions": [
                    {
                        "Name": "InstanceId",
                        "Value": "ins-***"
                    }
                ]
            }
        ]
    data = get_monitor_data(
        'QCE/CVM',
        'CPUUsage',
        ins,
        '2022-03-27T00:00:00+08:00',
        '2022-03-27T08:00:00+08:00',
    )
    data_to_img(data)
