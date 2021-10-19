# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import argparse
import requests
import urllib3
import logging

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

urllib3.disable_warnings()

# 全局session
session = requests.Session()

# 全局参数
COS_SECRETID = ""
COS_SECRETKEY = ""
COS_REGION = ""
BUCKET_NAME = ""
FILE_URL = ""


class BasicException(Exception):
    """异常"""

    pass


class UploadException(BasicException):
    pass


def get_logger(name='python-console'):
    log_fmt = "%(asctime)s %(lineno)-4s %(levelname)-6s %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(format=log_fmt, datefmt=date_fmt, level=logging.INFO)

    return logging.getLogger(name)


def get_client(secret_id=COS_SECRETID, secret_key=COS_SECRETKEY, region=COS_REGION):
    """获取cos客户端"""

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=None, Scheme='https')

    return CosS3Client(config)


# ================================================================================================

logger = get_logger()
client = get_client()


def delete_files(files, bucket=BUCKET_NAME):
    """"""

    objects = {'Object': [{'Key': cos_file, } for cos_file in files], 'Quiet': 'true'}

    response = client.delete_objects(Bucket=bucket, Delete=objects)
    logger.info(response)


def upload_file(file_path, cos_path, cos_dir='/', bucket=BUCKET_NAME):
    """
    根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    """

    response = client.upload_file(
        Bucket=bucket,
        LocalFilePath=file_path,
        Key=os.path.join(cos_dir, cos_path),
        PartSize=1,
        MAXThread=10,
        EnableMD5=False,
    )

    logger.info(response)


def list_files(bucket=BUCKET_NAME, prefix=None):
    response = client.list_objects(
        Bucket=bucket,
        # Prefix=prefix
    )
    logger.info(response)


def sync_files(src_dir, cos_dir, bucket=BUCKET_NAME, mode='overwrite'):
    """
    目录文件同步
    :param src_dir: 源目录
    :param cos_dir: 目标目录
    :param mode: overwrite|smart
    """
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="publish static assets files to cos")
    parser.add_argument("app_code", help="app_code in paas developer center")
    parser.add_argument("env", choices=["test", "prod"], default="test", help="deploy to test/prod")
    parser.add_argument("src", help="cos file path")
    parser.add_argument("dst", type=str, help="static assets file path")

    parser.add_argument("-i", "--sid", help="COS SecretId", required=False)
    parser.add_argument("-k", "--skey", help="COS SecretKey", required=False)
    parser.add_argument("-r", "--region", help="COS Region", required=False)
    parser.add_argument("-b", "--bucket", help="COS Bucket Name", required=False)

    args = parser.parse_args()

    app_code, env, src, dst, sid, skey, region, bucket = (
        args.app_code,
        args.env,
        args.src,
        args.dst,
        args.sid,
        args.skey,
        args.region,
        args.bucket,
    )

    logger.info(
        """
        ===========================
        app_code:       {},
        env:            {},
        src:            {},
        dst:            {}
        ===========================
    """.format(
            app_code, env, src, dst
        )
    )

    delete_files(['mime.types'])
    list_files()
    upload_file('./merge_ci.sh', 'merge_ci.sh', 'test')
