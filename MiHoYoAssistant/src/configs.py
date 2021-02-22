#!/usr/bin/env python3

import os
import LogWrapper.src.LogManager as logger

version = 'v1.0.0.0'

class Config:
    ACT_ID = 'e202009291139501'
    APP_VERSION = '2.3.0'
    REFERER_URL = 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?' \
                  'bbs_auth_required={}&act_id={}&utm_source={}&utm_medium={}&' \
                  'utm_campaign={}'.format('true', ACT_ID, 'bbs', 'mys', 'icon')
    AWARD_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}'.format(ACT_ID)
    ROLE_URL = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('hk4e_cn')
    INFO_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={}&act_id={}&uid={}'
    SIGN_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
    USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                 'miHoYoBBS/{}'.format(APP_VERSION)

class ProductConfig(Config):
    log_level = logger.__log_level__[logger.LogLevel.Info]

class DevelopConfig(Config):
    log_level = logger.__log_level__[logger.LogLevel.Debug]

runningEnv = 'Dev'
if runningEnv == 'Dev' or runningEnv == 'DEV':
    userConfig = DevelopConfig()
else:
    userConfig = ProductConfig()


MESSGAE_TEMPLATE = '''
    {today:#^28}
    🔅[{region_name}]{uid}{unm}
    今日奖励: {awardnm} × {award_cnt}
    本月累签: {total_sign_day} 天
    签到结果: {sign_state}
    {end:#^28}'''

userConfig.MESSGAE_TEMPLATE = MESSGAE_TEMPLATE