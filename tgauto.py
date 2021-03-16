#author:spark
#20210316

from telethon import TelegramClient
import os
import re
import time
import datetime
import random

#填自己的
api_id = 12345
api_hash = '0123456789abcdef0123456789abcdef'
client = TelegramClient('anon', api_id, api_hash)

#日志路径,按照以下示例
logdir = '/home/docker/jd/log/qq34347476_format_share_jd_code/'
flist = os.listdir(logdir)
log = logdir + flist[0]
Tdays = [1,8,16,24]
today = datetime.date.today().day

async def main():
    with open(log,'r') as f:
        res = f.read()
    #@LvanLamCommitCodeBot
    Llists = re.findall(r'/jd[a-z]+\s.*?[a-zA-Z0-9-_&=]+',res)
    #@TuringLabbot
    Tlists =  re.findall(r'/submit_activity_codes\s.*?[a-z]+.*?[a-zA-Z0-9-_&=]+',res)
    #for diy,自定义发送语句
    Dlists = ['xxxx','xxxxxx']
    
    if today in Tdays:
        for msg in Tlists:
            await client.send_message('@TuringLabbot', msg)
            #time.sleep(1)  
    for msg in Llists:
        await client.send_message('@LvanLamCommitCodeBot', msg)
        #time.sleep(1)
    ##如有需要,取消注释,并修改联系人.
    #for msg in Dlists:      
    #   await client.send_message('@LvanLamCommitCodeBot', msg)
        #time.sleep(1)

with client:
    client.loop.run_until_complete(main())
