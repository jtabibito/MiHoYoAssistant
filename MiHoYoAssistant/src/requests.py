#!/usr/bin/env python3

import requests
import json
import string
import uuid
import time
import random
import hashlib
from pubmodules import log
from src.configs import userConfig

def hexdigest(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

class HttpRequest:
    @staticmethod
    def toPython(data):
        return json.loads(data)

    @staticmethod
    def toJson(data, indent=None, ensure_ascii=True):
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

    def sendRequest(self, method, url, maxRetry:int=2,
        params=None, data=None, json=None, headers=None, **kwargs):
        for i in range(maxRetry + 1):
            try:
                session = requests.Session()
                result = session.request(method=method, url=url,
                    params=params, data=data, headers=headers, **kwargs)
            except HTTPError as e:
                log.error(f'Http error:{e}')
                log.error(f'Request {i + 1} failed, retrying...')
            except KeyError as e:
                log.error(f'Response error:{e}')
                log.error(f'Request {i + 1} failed, retrying...')
            except Exception as e:
                log.error(f'Unknown error:{e}')
                log.error(f'Request {i + 1} failed, retrying...')
            else:
                return result
        log.error(f'Http request failed...')

req = HttpRequest()

class BaseRequest(object):
    def __init__(self, cookies: str=None):
        if not isinstance(cookies, str):
           log.error("Type Error: %s want a %s but got a %s"
               .format(self.__class__, type(__name__), type(cookies)))
           return
        self._cookies = cookies

    def getHeader(self):
        header = {
            'User-Agent': userConfig.USER_AGENT,
            'Referer': userConfig.REFERER_URL,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookies
        }
        return header

class SignRequest(BaseRequest):
    def __init__(self, cookies=None):
        super().__init__(cookies=cookies)
        self._regions = []
        self._region_names = []
        self._uids = []
        self._unms = []

    @staticmethod
    def getDigest():
        # v2.3.0-web @povsister & @journey-ad
        n = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = hexdigest('salt=' + n + '&t=' + i + '&r=' + r)
        return '{},{},{}'.format(i, r, c)

    def getHeader(self):
        header = super().getHeader()
        header.update({
            'x-rpc-device_id':str(uuid.uuid3(
                uuid.NAMESPACE_URL, self._cookies)).replace('-', '').upper(),
            # 1:  ios
            # 2:  android
            # 4:  pc web
            # 5:  mobile web
            'x-rpc-client_type': '5',
            'x-rpc-app_version': userConfig.APP_VERSION,
            'DS': self.getDigest(),
        })
        return header

    def getSignInfo(self):
        log.info('获取账号绑定角色信息...')
        roles = RoleRequest(self._cookies).getRole().get('data', {}).get('list', [])
        if not roles:
            return None
        log.info(f'当前账号共绑定{len(roles)}个角色')
        self._regions = [(it.get('region', 'NA')) for it in roles]
        self._region_names = [(it.get('region_name', 'NA')) for it in roles]
        self._uids = [(it.get('game_uid', 'NA')) for it in roles]
        self._unms = [(it.get('nickname', 'NA')) for it in roles]

        log.info('开始获取签到信息...')
        infos = []
        for i in range(len(self._uids)):
            info_url = userConfig.INFO_URL.format(self._regions[i], userConfig.ACT_ID, self._uids[i])
            try:
                infos.append(HttpRequest.toPython(req.sendRequest('get', info_url, headers=self.getHeader()).text))
            except Exception as e:
                log.error(f'{e}')
                raise Exception('Http request error...')
        if not infos:
            log.info('获取签到信息失败')
        else:
            log.info('获取签到信息成功')
        return infos

    def sign(self):
        infos = self.getSignInfo()
        awards = RoleRequest(self._cookies).getAward()['data']['awards']
        msg_infos = []
        for i in range(len(infos)):
            today = infos[i]['data']['today']
            total_sign_day = infos[i]['data']['total_sign_day']
            uid = str(self._uids[i]).replace(str(self._uids[i])[1:8], '******', 1)
            log.info(f'开始为旅行者{self._unms[i]}签到')
            time.sleep(1.5)
            message = {
                'today': today,
                'region_name': self._region_names[i],
                'uid': uid,
                'unm': self._unms[i],
                'total_sign_day': total_sign_day,
                'end': '',
            }
            if infos[i]['data']['is_sign'] is True:
                state = f'👀旅行者{self._unms[i]}已经签过到了'
                log.info(state)
                message['sign_state'] = True
                message['awardnm'] = awards[total_sign_day - 1]['name']
                message['award_cnt'] = awards[total_sign_day - 1]['cnt']
                msg_infos.append(self.message.format(**message))
                continue
            else:
                message['sign_state'] = False
                message['awardnm'] = awards[total_sign_day]['name']
                message['award_cnt'] = awards[total_sign_day]['cnt']
            if infos[i]['data']['first_bind'] is True:
                message['sign_state'] = f'💪请先前往米游社App为旅行者{self._unms[i]}手动签到一次'
                msg_infos.append(self.message.format(**message))
                continue

            sign_data = {
                'act_id': userConfig.ACT_ID,
                'region': self._regions[i],
                'uid': self._uids[i]
            }
            try:
                response = req.sendRequest('post', userConfig.SIGN_URL, headesr=self.getHeader(), data=HttpRequest.toJson(sign_data, ensure_ascii=False))
            except Exception as e:
                log.error(f'{e}')
                raise Exception('Http request error...')
            if not response:
                log.error('Http response is None...')
                continue
            code = response.get('retcode', 9999)
            print(response)
            if code != 0:
                msg_infos.append(response)
                continue
            message['total_sign_day'] = total_sign_day + 1
            message['sign_state'] = response['message']
            msg_infos.append(self.message.format(**message))
        log.info('签到完成')
        return ''.join(msg_infos)

    @property
    def message(self):
        return userConfig.MESSGAE_TEMPLATE

class RoleRequest(BaseRequest):
    def getAward(self):
        log.info('获取账号奖励...')
        response = {}
        response = HttpRequest.toPython(req.sendRequest('get', userConfig.AWARD_URL, headers=self.getHeader()).text)
        if response is None:
            log.error('Http response error...')
        elif response.get('retcode', 1) != 0 or response.get('data', None) is None:
            log.info('奖励获取失败')
        else:
            log.info('账号奖励获取成功')
            return response
        return None

    def getRole(self):
        log.info('获取账号信息...')
        response = {}
        try:
            response = HttpRequest.toPython(req.sendRequest('get', userConfig.ROLE_URL, headers=self.getHeader()).text)
            message = response['message']
        except Exception as e:
            log.error(f'{e}')
            raise Exception('Http request error...')
        if response.get('retcode', 1) != 0 or response.get('data', None) is None:
            log.error(message)
            log.info('账号信息获取失败')
        else:
            log.info('账号信息获取成功')
            return response
        return None
