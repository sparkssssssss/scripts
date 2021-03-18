#coding:utf-8
import requests
import json
import datetime
import time
import random
import sys
import os
import re
import mylog

reload(sys)
sys.setdefaultencoding('utf-8')

logger = mylog.Mylog("pdd","/home/docker/jd/log/signlog/sign.log")


def sign():
    #参考格式
    headers = '''
Host: api.pinduoduo.com
accept: application/json, text/plain, */*
etag: 
referer: https://mobile.yangkeduo.com/hub_free_trial_task_result.html?sub_page=onix_miner&_pdd_fs=1&refer_page_id=13125_1615368030067_63p0sofh3x&refer_page_sn=13125&refer_page_name=hub_monthly_card
p-mode: 1
p-appname: pinduoduo
user-agent: android Mozilla/5.0 (Linux; Android 9; Redmi K20 Pro Premium Edition Build/PKQ1.190616.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36  phh_android_version/4.87.0 phh_android_build/8a101be6756ffbbf2eda2e44a3d3ae5170b72c44 phh_android_channel/google pversion/0
content-type: application/json;charset=UTF-8
content-length: 819
accept-encoding: gzip
    '''
    header = headers.strip().split('\n')
    header = {x.split(':')[0].strip(): ("".join(x.split(':')[1:])).strip().replace('//', "://") for x in header}
    urlsign = "https://api.pinduoduo.com/api/wizard/month/cash/miner/dig?pdduid=xxxx"
    #挖土data,过滤上面的url
    payload = ''
    gturl = 'https://api.pinduoduo.com/api/wizard/gather/cash/coupon/page?pdduid=xxxxx'
    #获取任务列表data,过滤上面的url
    gtpayload = ''
    murl = "https://api.pinduoduo.com/api/wizard/month/cash/mission/reward?pdduid=xxxx"
    mcurl = "https://api.pinduoduo.com/api/wizard/month/cash/mission/complete?pdduid=xxxx"
    #体力3的签到data,手动做一次,抓
    m1payload = ''
    s = requests.Session()
    try:
        gt = s.post(url=gturl,headers=header,data=gtpayload)
        if 'mission_list' in gt.text:
            gtres = json.loads(gt.text)
            #print gtres
            try:
                m2type = [ x["mission_type"] for x in gtres["cash_miner"]["mission_list"] if x["reward_amount"] == 4 ][0]
            except:
                m2type = 4
        else:
            m2type = 4
    except Exception, e:
        logger.error(str(e))
        m2type = 4
    try:
        m1 = s.post(url=murl,headers=header,data=m1payload)
        if 'reward_amount' in m1.text:
            res1 = json.loads(m1.text)
            logger.info("获得{}体力".format(str(res1["reward_amount"])))
        else:
            logger.error(m1.text)
        time.sleep(6)
    except Exception, e:
        logger.error(str(e))
        pass
    try:
        m2cpayload ={"mission_type":m2type,"timeout":10000}
        m2c = s.post(url=mcurl,headers=header,data=json.dumps(m2cpayload))
        #此处为完成体力4的任务数据,手动抓一次,因需要传参,所以,手动替换anti_content即可
        m2payload = {"mission_type":m2type,"anti_content":"","timeout":10000}
        m2 = s.post(url=murl,headers=header,data=json.dumps(m2payload))


        if 'reward_amount' in m2.text:
            res2 = json.loads(m2.text)
            logger.info("获得{}体力".format(str(res2["reward_amount"])))
        else:
            logger.error(m2.text)
        time.sleep(1)
    except Exception, e:
        logger.error(str(e))
        pass
    while True:
        signact = s.post(url=urlsign,headers=header,data=payload)
        time.sleep(5)
        res = json.loads(signact.text)
        if 'error_msg' in signact.text:
            logger.info(str(res["error_msg"]))
            sys.exit(9)
        
        if  'current_energy' in signact.text:
            logger.info("当前体力值: " + str(res["current_energy"]))
            if res["current_energy"] < 2:
                logger.info("挖宝体力值不够")
                break
        else:
            logger.info(signact.text)
            break


if __name__ == "__main__":
    num=random.randint(1,300)
    time.sleep(num)
    sign()

