from tencentcloud.common import credential
from tencentcloud.billing.v20180709 import billing_client, models
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import logging
import json
import os


class TencentAPI():
    """
    騰訊雲 API 示例
    """

    def __init__(self, secret_id, secret_key, logger=None, **args):
        """初始化騰訊雲 API 客户端
        Args:
            secret_id (str): 騰訊雲 SecretId
            secret_key (str): 騰訊雲 SecretKey
            logger (logging.Logger, optional): 日誌記錄器. Defaults to None.
            **args: 其他參數
            參數說明：
                log_level (str): 日誌等級 (預設: INFO)
                log_path (str): 日誌檔案路徑 (預設: logs/tencent_api.log)
                max_bytes (int): 單個日誌檔案最大字節數 (預設: 5*1024*1024)
                backup_count (int): 保留的備份日誌檔案數量 (預設: 3)
        """
        # 初始化
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "billing.tencentcloudapi.com"
        clientProfile = ClientProfile(httpProfile=httpProfile)
        self.client = billing_client.BillingClient(cred, "", clientProfile)
        self.logger = logger or logging.getLogger(__name__)
        if logger == None:
            self.logger = logging.getLogger('TencentAPIMain')
            self.logger.setLevel(getattr(logging, args.get("log_level", "INFO")))
            log_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.logger.propagate = False

            log_path = os.path.abspath(args.get("log_path", os.path.join("logs", "tencent_api.log")))
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=args.get("max_bytes", 5*1024*1024),
                backupCount=args.get("backup_count", 3),
                encoding='utf-8'
            )
            file_handler.setFormatter(log_formatter)
            # 只記錄 ERROR+
            file_handler.setLevel(logging.ERROR)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            self.logger.addHandler(console_handler)

    def get_bill_time_range(self, month_str: str):
        """
        根據輸入月份 (YYYY-MM)，返回該月份的開始與結束時間。
        例如輸入 "2025-09" ->
            begin_time = "2025-09-01 00:00:00"
            end_time   = "2025-09-30 23:59:59"
        """
        # 將字串轉成 datetime 物件
        first_day = datetime.strptime(month_str, "%Y-%m")

        # 取得下個月的第一天，再往前一天 -> 本月最後一天
        next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = next_month - timedelta(days=1)

        begin_time = first_day.strftime("%Y-%m-%d 00:00:00")
        end_time = last_day.strftime("%Y-%m-%d 23:59:59")

        return begin_time, end_time

    # ---------- L2：按產品匯總 ----------

    def get_l2_bill(self, month):
        """L2：按產品匯總

        Args:
            month (_type_): 帳單月份 (格式: YYYY-MM) 範例: 2025-09
        """
        begin_time, end_time = self.get_bill_time_range(month)
        self.logger.info(f"查詢月份: {month}，時間範圍: {begin_time} ~ {end_time}")
        req = models.DescribeBillSummaryByProductRequest()
        # req.Month = month
        # req.NeedRecordNum = 1
        req.BeginTime = begin_time
        req.EndTime = end_time
        # req.Limit = 100  # 每頁最大100筆
        # req.Offset = 0   # 起始偏移量

        resp = self.client.DescribeBillSummaryByProduct(req)
        self.logger.info("=== L2 按產品匯總 ===")
        self.logger.info(json.dumps(json.loads(resp.to_json_string()),
                         indent=2, ensure_ascii=False))

    # ---------- L3：帳單明細 ----------

    def get_l3_bill(self, month):
        """L3：帳單明細

        Args:
            month (_type_): 帳單月份 (格式: YYYY-MM) 範例: 2025-09
        """
        begin_time, end_time = self.get_bill_time_range(month)
        self.logger.info(f"查詢月份: {month}，時間範圍: {begin_time} ~ {end_time}")
        req = models.DescribeBillDetailRequest()
        req.Month = month
        req.BeginTime = begin_time
        req.EndTime = end_time
        req.Limit = 100  # 每頁最大100筆
        req.Offset = 0   # 起始偏移量

        resp = self.client.DescribeBillDetail(req)
        self.logger.info("=== L3 帳單明細 ===")
        self.logger.info(json.dumps(json.loads(resp.to_json_string()),
                         indent=2, ensure_ascii=False))
