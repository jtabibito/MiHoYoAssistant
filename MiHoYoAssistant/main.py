#!/usr/bin/env python3

import os
import sys
import src.requests as request
from pubmodules import log
from src.configs import version

def main():
    cookies = ''
    if os.environ.get('COOKIE', '') == '':
        log.info(f'未配置账号cookies...')
        exit(0)
    cookies = os.environ['COOKIE']
    
    log.info(f'🌀原神签到小助手 {version}')   
    log.info(f'用户已配置账号cookies数量{len(cookies)}')
    ret = success = failed = 0
    for i in range(len(cookies)):
        try:
            sign = request.SignRequest(cookies[i]).sign()
            print(sign)
            log.info(f'已帮助第{i + 1}个用户签到完成')
            success += 1
        except Exception as e:
            log.error(f'为第{i + 1}个用户签到时出现错误: {e}')
            failed += 1
            ret = -1
    log.info(f'所有用户签到完成: 成功数:{success} | 失败数:{failed}')
    if ret != 0:
        log.error('异常退出')
        exit(ret)
    log.info('任务结束')

if __name__ == '__main__':
    main()
