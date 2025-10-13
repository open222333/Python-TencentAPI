from tencentcloud.common import credential
from tencentcloud.billing.v20180709 import billing_client, models
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
import json


class TencentAPI():
    """
    騰訊雲 API 示例
    """

    def __init__(self, secret_id, secret_key):
        """初始化騰訊雲 API 客户端
        Args:
            secret_id (str): 騰訊雲 SecretId
            secret_key (str): 騰訊雲 SecretKey
        """
        # 初始化
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "billing.tencentcloudapi.com"
        clientProfile = ClientProfile(httpProfile=httpProfile)
        self.client = billing_client.BillingClient(cred, "", clientProfile)

    # ---------- L2：按產品匯總 ----------

    def get_l2_bill(self, month):
        """L2：按產品匯總

        Args:
            month (_type_): 帳單月份 (格式: YYYY-MM) 範例: 2025-09
        """
        req = models.DescribeBillSummaryByProductRequest()
        req.Month = month
        req.NeedRecordNum = 1
        req.Limit = 100  # 每頁最大100筆
        req.Offset = 0   # 起始偏移量

        resp = self.client.DescribeBillSummaryByProduct(req)
        print("=== L2 按產品匯總 ===")
        print(json.dumps(json.loads(resp.to_json_string()),
                         indent=2, ensure_ascii=False))

    # ---------- L3：帳單明細 ----------

    def get_l3_bill(self, month):
        """L3：帳單明細

        Args:
            month (_type_): 帳單月份 (格式: YYYY-MM) 範例: 2025-09
        """
        req2 = models.DescribeBillDetailRequest()
        req2.Month = month
        req2.Limit = 100  # 每頁最大100筆
        req2.Offset = 0   # 起始偏移量

        resp2 = self.client.DescribeBillDetail(req2)
        print("=== L3 帳單明細 ===")
        print(json.dumps(json.loads(resp2.to_json_string()),
                         indent=2, ensure_ascii=False))
