from argparse import ArgumentParser
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from src.tencent import TencentAPI
from datetime import datetime, timedelta
import json
import logging
import os


if __name__ == '__main__':
    parser = ArgumentParser(description='TencentAPI 指令列介面')
    parmas_group = parser.add_argument_group("params", "參數相關參數")
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    parmas_group.add_argument('--month', type=str, default=last_month, help='查詢月份（預設：上個月，例如 2025-09）')
    config_group = parser.add_argument_group("config", "設定相關參數")
    config_group.add_argument('--config_path', type=str,
                              default=os.path.join('conf', 'config.ini'),
                              help='路徑至設定檔（預設：conf/config.ini）')
    log_group = parser.add_argument_group("log", "日誌相關參數")
    log_group.add_argument('--log_path', type=str,
                           default=os.path.join('logs', 'TencentAPIMain.log'),
                           help='路徑至日誌檔（預設：logs/TencentAPIMain.log）')
    log_group.add_argument('--log_level', type=str,
                           choices=['DEBUG', 'INFO',
                                    'WARNING', 'ERROR', 'CRITICAL'],
                           default='DEBUG',
                           help='日誌等級（預設：DEBUG）')
    log_group.add_argument('--no_console', action='store_true',
                           help='不輸出日誌至控制台')
    log_group.add_argument('--no_file', action='store_true',
                           help='不輸出日誌至檔案')
    log_group.add_argument('--max_bytes', type=int,
                           default=10 * 1024 * 1024,
                           help='單一日誌檔最大位元組數（預設：10MB）')
    log_group.add_argument('--backup_count', type=int,
                           default=5,
                           help='保留的舊日誌檔案數量（預設：5）')
    json_group = parser.add_argument_group("json", "JSON 相關參數")
    json_group.add_argument('--info_path', type=str,
                            default=os.path.join('conf', 'tencent.json'),
                            help='路徑至資訊檔（預設：conf/tencent.json）')

    args = parser.parse_args()

    logger = logging.getLogger('TencentAPIMain')
    logger.setLevel(getattr(logging, args.log_level))
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.propagate = False

    if not args.no_file:
        log_path = os.path.abspath(args.log_path)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=args.max_bytes,
            backupCount=args.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_formatter)
        # 只記錄 ERROR+
        file_handler.setLevel(logging.ERROR)

    if not args.no_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    if args.no_file and args.no_console:
        logger.warning("日誌輸出已全部停用（no_file 和 no_console 均為 True）")

    infos = json.loads(open(args.info_path, 'r', encoding='utf-8').read())


    for info in infos:
        logger.info(f"處理帳號：{info.get('name', 'unknown')}")
        if 'secret_id' not in info or 'secret_key' not in info:
            logger.error("資訊檔中缺少 secret_id 或 secret_key，跳過此帳號")
            continue
        try:
            tencent = TencentAPI(
                secret_id=info['secret_id'],
                secret_key=info['secret_key']
            )
            l2 = tencent.get_l2_bill(month=args.month)
            if l2 is not None:
                logger.info(f"L2 帳單（{args.month}）：")
                for item in l2:
                    logger.info(item)
            else:
                logger.info(f"L2 帳單（{args.month}）無資料")

            l3 = tencent.get_l3_bill(month=args.month)
            if l3 is not None:
                logger.info(f"L3 帳單（{args.month}）：")
                for item in l3:
                    logger.info(item)
            else:
                logger.info(f"L3 帳單（{args.month}）無資料")
        except Exception as e:
            logger.error(f"TencentAPI 初始化失敗：{e}")
            continue
