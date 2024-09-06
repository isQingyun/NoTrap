import json

from tencentcloud.common import credential  # 这里需要安装腾讯翻译sdk
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import models, tmt_client

try:
    cred = credential.Credential(
        "api_id", "api_secret"
    )
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tmt.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

    req = models.TextTranslateRequest()
    req.SourceText = "We will know, we must know."  # 要翻译的语句
    req.Source = "en"  # 源语言类型
    req.Target = "zh"  # 目标语言类型
    req.ProjectId = 0

    resp = client.TextTranslate(req)
    data = json.loads(resp.to_json_string())
    print(data["TargetText"])


except TencentCloudSDKException as err:
    print(err)
