import json
import os
import random
import re
import requests
import sys
import time

from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

# Check files
if not os.path.isfile("config.json"):
    print('配置文件不存在,无法运行.')
    input('按回车退出.')
    sys.exit()


with open('config.json') as f:
    cfg = json.load(f)
last_msg = ''
video_path = cfg["video_path"]
audio_path = cfg["audio_path"]
ffmpeg_path = cfg["ffmpeg_path"]
log_path = cfg["log_path"]
start_hour = cfg["start_hour"]
end_hour = cfg["end_hour"]
user_id = cfg["user_id"]
yzb_url = cfg["yzb_url"] + str(user_id)
CORP_ID = cfg["CORP_ID"]
CORP_SECRET = cfg["CORP_SECRET"]
AgentId = cfg["AgentId"]
tt0 = cfg["tt0"]

if not os.path.isfile(ffmpeg_path):
    print("ffmpeg.exe路径错误.")
    input('按回车退出')
    sys.exit()

class WxNotify:

    def __init__(self, corpid, corpsecret, agentid):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = self._get_access_token(corpid, corpsecret)

    def send(self, text):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.access_token
        payload = {'touser': '@all',
                   'msgtype': 'text',
                   'agentid': self.agentid,
                   'text': {'content': text},
                   'safe': 0,
                   'enable_id_trans': 0,
                   'enable_duplicate_check': 0,
                   'duplicate_check_interval': 1800}
        resp = requests.post(url, data=(json.dumps(payload)))
        resp.raise_for_status()
        return resp.json()

    def _get_access_token(self, corpid, corpsecret):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        params = {'corpid': corpid,
                  'corpsecret': corpsecret}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        resp_json = resp.json()
        if 'access_token' in resp_json.keys():
            return resp_json['access_token']
        raise Exception('Please check if corpid and corpsecret are correct \n' + resp.text)


def log(msg):
    global last_msg
    if last_msg == msg:
        return
    last_msg = msg
    time_fmt1 = '%Y-%m-%d'
    f = open(os.path.join(log_path, time.strftime(time_fmt1) + '.log'), 'a')
    f.write(time.ctime() + ' : ' + str(msg) + '\n')
    try:
        t = WxNotify(CORP_ID, CORP_SECRET, AgentId)
        res = t.send(str(msg))
        f.write(time.ctime() + ' : ' + str(res) + '\n')
        pass
    finally:
        f.close()


def fill_date(_dd='202111'):
    from datetime import datetime as dt
    _dd = str(_dd)
    if _dd.__contains__('-'):
        return _dd.replace('-', '')
    month = dt.now().month
    if len(_dd) == 6:
        _dd = _dd[0:4] + '0' + _dd[4:5] + '0' + _dd[5:6]
    else:
        if len(_dd) == 7:
            if _dd[5:6] == '0':
                _dd = _dd[0:4] + _dd[4:6] + '0' + _dd[6:7]
            else:
                if not int(_dd[4:5]) >= 2:
                    if _dd[6:7] == '0' or _dd[5:6] == '3':
                        _dd = _dd[0:4] + '0' + _dd[4:5] + _dd[5:7]
                elif month < 9:
                    _dd = _dd[0:4] + '0' + _dd[4:5] + _dd[5:7]
                else:
                    _dd = _dd[0:4] + _dd[4:6] + '0' + _dd[6:7]
        else:
            if len(_dd) == 8:
                pass
            else:
                log('Error!' + _dd + '.')
    return _dd


def create_folder(path):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)


def query_url(url):
    try:
        try:
            i_headers = {
                'User-Agent':
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68"
            }
            s = requests.Session()
            s.mount('http: //', HTTPAdapter(max_retries=2))
            s.mount('https: //', HTTPAdapter(max_retries=2))
            content = s.get(url, timeout=30, headers=i_headers)
            if content.status_code == 200:
                return content.content
            return
        except Exception as e:
            try:
                log('Query_url : ' + str(e))
            finally:
                e = None
                del e
    finally:
        pass


def download_video(m3u8_url, filename, audio_path_name):
    st1 = time.time()
    os.system(
        ffmpeg_path + ' -hwaccel ' + cfg["hwaccel"] + ' -codec:v:0 ' + cfg[
            "decoder"] + ' -i "' + m3u8_url + '" -codec:v:0 ' + cfg["encoder"] + ' "' + filename + '"')
    st2 = time.time()
    stake = round(st2 - st1)
    log('视频已下载!耗时 {} 秒'.format(stake))
    time.sleep(5)
    os.system(ffmpeg_path + ' -i "' + filename + '" -filter:a "atempo=1.5" -vn "' + audio_path_name + '"')
    log('音频已转码!')


def get_m3u8(url):
    video_id = url[url.rfind('/') + 1:].split('.')[0]
    json_request_url = 'http://www.yizhibo.com/live/h5api/get_basic_live_info?scid={}'.format(video_id)
    content = query_url(json_request_url)
    data = json.loads(content)
    status = data.get('data')['status']
    title = data.get('data')['live_title']
    if title == '':
        title = data.get('data')['nickname']
    m3u8_content = query_url(url)
    m3u8_url = re.search(r"http[s]*://[a-zA-Z0-9/_.]+\.m3u8", m3u8_content.decode('utf-8'))
    date_str = re.search(r"\d{4}-\d{2}-\d{2}", m3u8_content.decode('utf-8'))[0]
    # print(date_str)
    if date_str == 'live':
        log('直播中...')
        return '', '', ''
    filename = fill_date(date_str) + '_' + format_filename(title) + '_' + video_id + '.mp4'
    audio_file_name = fill_date(date_str) + '_' + format_filename(title) + '_' + video_id + '.aac'
    download_path = os.path.join(video_path, filename)
    audio_file_path = os.path.join(audio_path, audio_file_name)
    # print(download_path)
    if os.path.isfile(download_path):
        return '', '', ''
    if status == 11:
        log('找到一个视频' + filename)
        return m3u8_url[0], download_path, audio_file_path
    elif status == 10:
        log('直播中...')
    return '', '', ''


def format_filename(name):
    return re.sub('[！!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ ]+', '', name)


if __name__ == '__main__':
    create_folder(video_path)
    create_folder(audio_path)
    create_folder(log_path)
    log('开始检查视频...')
    while 1:
        now_hour = int(time.strftime('%H'))
        if start_hour <= now_hour <= end_hour:
            soup = BeautifulSoup(query_url(yzb_url), 'html.parser')
            aa = soup.select('a')
            if len(aa) <= 5:
                log('没有直播')
                time.sleep(random.uniform(60, 90))
            else:
                for a_link in aa:
                    if len(a_link['href']) < 40:
                        web_url = '{}{}'.format('https://www.yizhibo.com', a_link['href'])
                        m3u8, file_path, audio_name = get_m3u8(web_url)
                        if len(m3u8) + len(file_path) > 10:
                            log(m3u8)
                            download_video(m3u8, file_path, audio_name)
                        else:
                            time.sleep(random.uniform(tt0 - 3, tt0 + 3))
        else:
            log('退出检查...')
            time.sleep(10)
            sys.exit()
