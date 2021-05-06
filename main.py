# Author: leeyiding(乌拉)
# Date: 2020-05-05
# Link: https://github.com/leeyiding/get_CCB
# Version: 0.1.4
# UpdateDate: 2020-05-05 12:35
# UpdateLog: 修复车主分会场未增加三次抽奖机会Bug

import requests
import json
import os
import time
import re
import random
import datetime
import urllib.parse

try:
    commonres = requests.get("http://47.100.61.159:10080/ccbcommon")
    commoncode = commonres.text.split('@')
except:
    commoncode = []
try:
    motherres = requests.get("http://47.100.61.159:10080/ccbmother")
    mothercode = motherres.text.split('@')
except:
    mothercode = []

class getCCB():
    def __init__(self,cookies,shareCode):
        self.cookies = cookies
        self.commonShareCode = shareCode['common'] + commoncode
        print('建筑互助码:{}'.format(self.commonShareCode))
        self.motherDayShareCode = shareCode['motherDay'] + mothercode
        print('母亲节互助码:{}'.format(self.motherDayShareCode))
        self.xsrfToken = self.cookies['XSRF-TOKEN'].replace('%3D','=')
        self.currentTime = int(time.time())

    def getApi(self,functionId,activityId='lPYNjdmN',params=()):
        '''
        GET请求接口
        '''
        url = 'https://jxjkhd.kerlala.com/{}/91/{}'.format(functionId,activityId)
        headers = {
            'authority': 'jxjkhd.kerlala.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; Redmi K30 5G Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045613 Mobile Safari/537.36 MMWEBID/6824 micromessenger/8.0.1.1841(0x28000151) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
            'referer': 'https://jxjkhd.kerlala.com/a/91/lPYNjdmN/fdtopic_v1/index',
        }
        try:
            r = requests.get(url, headers=headers, params=params, cookies=self.cookies)
            if re.findall('DOCTYPE',r.text):
                return r.text
            else:
                return r.json()
        except:
            print('调用接口失败，等待10秒重试')
            time.sleep(10)
            r = requests.get(url, headers=headers, cookies=self.cookies)
            return r.json()


    def postApi(self,functionId,data,activityId='lPYNjdmN'):
        '''
        POST请求接口
        '''
        url = 'https://jxjkhd.kerlala.com/{}/91/{}'.format(functionId,activityId)
        headers = {
            'authority': 'jxjkhd.kerlala.com',
            'x-xsrf-token': self.xsrfToken,
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; Redmi K30 5G Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045613 Mobile Safari/537.36 MMWEBID/6824 micromessenger/8.0.1.1841(0x28000151) Process/tools WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
            'origin': 'https://jxjkhd.kerlala.com',
            'referer': 'https://jxjkhd.kerlala.com/a/91/lPYNjdmN/fdtopic_v1/index',
            'content-type': 'application/json;charset=UTF-8',
        }
        try:
            r = requests.post(url, headers=headers, data=data, cookies=self.cookies)
            if re.findall('DOCTYPE',r.text):
                print('Cookie已失效，请更新Cookie')
                return False
            else:
                return r.json()
        except:
            print('调用接口失败，等待10秒重试')
            time.sleep(10)
            r = requests.post(url, headers=headers, data=data, cookies=self.cookies)
            return r.json()


    def getUserInfo(self):
        '''
            获取账户信息
        '''
        userInfo = self.getApi('activity/fbtopic/userInfo')
        if userInfo != False:
            print('\n用户{}信息获取成功'.format(userInfo['data']['nickname']))
            print('已获得CC币总量{}，剩余CC币总量{}'.format(userInfo['data']['ccb_money'],userInfo['data']['remain_ccb_money']))
            print('当前建筑等级{}级，已获得建设值总量{},升级还需建设值{}'.format(userInfo['data']['grade'],userInfo['data']['build_score'],userInfo['data']['need_build_score']))
            print('您的助力码为：{}'.format(userInfo['data']['ident']))
            try:
                print('提交地址为:' + 'http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(userInfo['data']['nickname'],userInfo['data']['ident'],"ccbcommon"))
                user_name = urllib.parse.quote(userInfo['data']['nickname'])
                requests.get('http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(user_name,userInfo['data']['ident'],"ccbcommon"))
            except Exception as e:
                print(e)
            return True
        else:
            return False
        

    def acceptCCB(self):
        '''
            领取每日CCB或建设值
        '''
        # 查询可领取的CC币
        ccbList = self.postApi('activity/fbtopic/ccbList',{})
        for i in range(len(ccbList['data'])):
            data = '{"id":"' + str(ccbList['data'][i]['task_id']) + '","result_id": "' + str(ccbList['data'][i]['id']) + '"}'
            if ccbList['data'][i]['type'] == 'dailyCcb':
                acceptCcbResult = self.postApi('activity/fbtopic/acceptCcb',data)
                print('领取{}个每日CCB成功'.format(ccbList['data'][i]['ccb_num']))
            elif ccbList['data'][i]['type'] == 'task':
                acceptCcbResult = self.postApi('Component/task/draw',data)
                print('领取{}建设值成功'.format(ccbList['data'][i]['ccb_num']))


    def doTask(self):
        '''
        主会场完成任务
        '''
        print('\n开始做日常任务')
        activityInfo = self.getApi('Common/activity/getActivityInfo')
        if self.currentTime < activityInfo['data']['end_time']:
            # 获取任务列表
            taskList = self.getApi('Component/task/lists')
            print('共获取到{}个任务'.format(len(taskList['data']['task'])))
            for i in range(len(taskList['data']['task'])):
                print('\n开始做任务{}【{}】'.format(i+1,taskList['data']['task'][i]['show_set']['name']))
                # 判断任务状态
                if taskList['data']['userTask'][i]['finish'] ==1:
                    print('该任务已完成，无需重复执行')
                else:
                    # 判断任务类型
                    if taskList['data']['task'][i]['type'] == 'visit' or taskList['data']['task'][i]['type'] == 'other':
                        # 浏览类型任务
                        data = '{"id": "' + taskList['data']['task'][i]['id'] + '"}'
                        doTaskResult = self.postApi('Component/task/do',data)
                        print(doTaskResult['message'])
                    elif taskList['data']['task'][i]['type'] == 'signin':
                        # 签到任务
                        signinResult = self.postApi('activity/autographnew/qdEvery',{},'5Z9WJoPK')
                        print(signinResult['message'])
                        if signinResult['status'] == 'success':
                            print('获得{}'.format(signinResult['data']['prize_name']))
                    elif taskList['data']['task'][i]['type'] == 'share':
                        # 助力任务
                        print('助力逻辑未知')
                    # 领取奖励
                    if taskList['data']['task'][i]['draw_type'] == 'number':
                        # 气泡类型奖励
                        self.acceptCCB()
                    elif taskList['data']['task'][i]['draw_type'] == 'accept':
                        # 按钮类型奖励
                        data = '{"id":"' + taskList['data']['task'][i]['id'] + '"}'
                        acceptResult = self.postApi('Component/task/draw',data)
                        print(acceptResult['message'])
                    # 休息五秒，防止接口提示频繁 
                    time.sleep(5)
            # 升级建筑
            self.buildingUp()
        else:
            print('抱歉，该活动已结束')


    def buildingUp(self):
        '''
        升级建筑
        '''
        print('\n开始升级建筑')
        userInfo = self.getApi('activity/fbtopic/userInfo')
        if userInfo['data']['remainder_build_score'] >= userInfo['data']['next_grade_build_score']:
            buildingUpResult = self.postApi('activity/fbtopic/buildingUp',{})
            if len(buildingUpResult['data']['up_awards']['up_awards']) > 0:
                upAwardsName = buildingUpResult['data']['up_awards']['up_awards'][0]['name']
                print('升级{}成功，获得奖励{}'.format(buildingUpResult['data']['up_building']['name'],upAwardsName))
            else:
                print('升级{}成功，无奖励'.format(buildingUpResult['data']['up_building']['name']))
            # 继续检查是否能升级
            time.sleep(5)
            self.buildingUp()
        else:
            print('建设值不足,距下一等级还需{}建设值'.format(userInfo['data']['need_build_score']))


    def doCarTask(self):
        '''
            车主分会场做任务、抽奖
        '''
        print('\n开始做车主分会场任务')
        activityInfo = self.getApi('Common/activity/getActivityInfo','dmRe4rPD')
        if self.currentTime < activityInfo['data']['end_time']:
            # 访问首页，获得三次抽奖机会
            self.getApi('a','dmRe4rPD/parallelsessions_v1/index',(('CCB_Chnl', '6000213'),))
            # 获取任务列表
            taskList = self.getApi('activity/parallelsessions/getIndicatorList','dmRe4rPD')
            print('共获取到{}个任务'.format(len(taskList['data']['task'])))
            for i in range(len(taskList['data']['task'])):
                print('\n开始做任务【{}】'.format(taskList['data']['task'][i]['indicator']['show_name']))
                if taskList['data']['task'][i]['day_complete'] == 1:
                    print('该任务今日已完成，无需重复执行')
                elif taskList['data']['task'][i]['day_complete'] == 0:
                    data = '{"code": "' + taskList['data']['task'][i]['indicator']['code'] + '"}'
                    doTaskResult = self.postApi('activity/parallelsessions/visit',data,'dmRe4rPD')
                    print(doTaskResult['message'])
            # 获取抽奖次数
            carIndexInfo = self.getApi('activity/parallelsessions/index','dmRe4rPD')
            print('车主分会场剩余抽奖次数{}'.format(carIndexInfo['data']['remain_num']))
            # 抽奖
            if int(carIndexInfo['data']['remain_num']) > 0:
                for i in range(int(carIndexInfo['data']['remain_num'])):
                    drawResult = self.postApi('activity/parallelsessions/draw',{},'dmRe4rPD')
                    if drawResult['status'] == 'success':
                        print(drawResult['data']['prizename'])
                    else:
                        print(drawResult['message'])
                    # 休息四秒，防止接口频繁
                    time.sleep(4)
        else:
            print('抱歉，该活动已结束')


    def draw(self):
        '''
        抽奖，每日10次机会
        抽奖策略：
        1. 若已进行抽奖次数小于等于3，则执行抽奖
        2. 剩余次数小于等于7次 总盈利达20 CC币跳出抽奖
        3. 剩余次数大于7次，总盈利达30 CC币跳出抽奖
        '''
        print('\n开始天天抽奖')
        activityInfo = self.getApi('Common/activity/getActivityInfo','03ljx6mW')
        if self.currentTime < activityInfo['data']['end_time']:
            # 检查报名状态
            drawStatus = self.getApi('Component/signup/status','03ljx6mW')
            if drawStatus['status'] == 'fail':
                print('未报名，请前往天天抽奖进行报名')
            else:
                getUserCCBResult = self.getApi('Component/draw/getUserCCB','03ljx6mW')
                userRemainDrawNum = getUserCCBResult['data']['draw_day_max_num'] - int(getUserCCBResult['data']['user_day_draw_num'])
                if int(getUserCCBResult['data']['user_day_draw_num']) <= 3:
                    print('今日已抽奖次数小于3，开始执行抽奖')
                    if userRemainDrawNum > 7:
                        breakTotalCCB = 30
                    else:
                        breakTotalCCB = 20
                    drawTotalCCB = 0
                    for i in range(userRemainDrawNum):
                        drawResult = self.postApi('Component/draw/commonCcbDrawPrize',{},'03ljx6mW')
                        if drawResult['data']['prize_type'] == 'jccb':
                            print(drawResult['message'] + drawResult['data']['prizename'])
                            prizeNum = int(re.findall('[0-9]*',drawResult['data']['prizename'])[0]) - 30
                            drawTotalCCB += prizeNum
                        else:
                            print(drawResult['message'] + drawResult['data']['prizename'])
                        # 判断总盈利
                        if drawTotalCCB >= breakTotalCCB:
                            print('本轮抽奖总盈利已达{}CC币，退出抽奖'.format(breakTotalCCB))
                            break
                        # 休息5秒，避免接口频繁
                        time.sleep(5)
                else:
                    print('今日已进行过{}次抽奖了,若有剩余次数可手动执行'.format(getUserCCBResult['data']['user_day_draw_num']))
        else:
            print('抱歉，该活动已结束')


    def dayAnswer(self):
        '''
            奋斗学院每日一答
            无论对错，奖励均为10建设值
        '''
        print('\n开始每日一答')
        activityInfo = self.getApi('Common/activity/getActivityInfo','jmX0aKmd')
        if self.currentTime < activityInfo['data']['end_time']:
            # 获取用户答题信息
            userDataInfo = self.getApi('activity/dopanswer/getUserDataInfo','jmX0aKmd')
            if userDataInfo['data']['remain_num'] == 1:
                # 获取题目
                question = self.getApi('activity/dopanswer/getQuestion','jmX0aKmd')
                questionTitle =question['data']['all_question'][0]['question']['title']
                questionId = question['data']['all_question'][0]['question']['id']
                print('问：{} id:{}'.format(questionTitle,questionId))
                for i in range(len(question['data']['all_question'][0]['option'])):
                    print('选项{}：{}'.format(i+1,question['data']['all_question'][0]['option'][i]['title']))
                # 随机答题
                randomOption = random.randint(1,len(question['data']['all_question'][0]['option']))
                print('随机选择选项{}'.format(randomOption))
                data = '{"answerId":"' + str(randomOption) +'","questionId":"' + str(questionId) + '"}'
                answerQuestionResult = self.postApi('activity/dopanswer/answerQuestion',data,'jmX0aKmd')
                print('正确答案：选项{}'.format(answerQuestionResult['data']['right']))
                print(answerQuestionResult['message'])
            else:
                print('今日答题机会已用尽')
        else:
            print('抱歉，该活动已结束')


    def mothersDayTask(self):
        '''
        母亲节晒妈活动
        '''
        print('\n开始做 母亲节集赞得520CC币 活动')
        activityInfo = self.getApi('Common/activity/getActivityInfo','jmX08Ymd')
        if self.currentTime < activityInfo['data']['end_time']:
            # 获取用户信息
            userInfo = self.getApi('activity/mumbit/getUserInfo','jmX08Ymd')
            print('您的活动助力码为：{}'.format(userInfo['data']['ident']))
            try:
                print('提交地址为:' + 'http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(userInfo['data']['nickname'],userInfo['data']['ident'],"ccbmother"))
                user_name = urllib.parse.quote(userInfo['data']['nickname'])
                requests.get('http://47.100.61.159:10080/add?user={}&code={}&type={}'.format(user_name,userInfo['data']['ident'],"ccbmother"))
            except Exception as e:
                print(e)
            judgeStatus = self.getApi('activity/mumbit/judgeStatus','jmX08Ymd')
            if judgeStatus['data']['ext'] == '':
                print('您从未参加该活动，开始初始化活动')
                 # 设置标签
                data = '{"ext":"[{\\"title\\":\\"\u89C9\u5F97\u6211\u6C38\u8FDC\u5403\u4E0D\u9971\\",\\"thumbnail_url\\":\\"https://ccbhdimg.kerlala.com/hd/users/10461/20210430/8645701907.png\\",\\"isChoosed\\":true,\\"left\\":\\"0rem\\",\\"top\\":\\"2.6rem\\"}]"}'.encode("utf-8").decode("latin1")
                updatePhraseResult = self.postApi('activity/mumbit/updatePhrase',data,'jmX08Ymd')
                print('初始化活动结果：'.format(updatePhraseResult['message']))
            userLaunchInfo = self.getApi('activity/mumbit/getUserLaunchInfo','jmX08Ymd',(('share_ident', userInfo['data']['ident']),))
            if userLaunchInfo['code'] == 2101:
                # 开启分享
                doUserLaunchResult = self.postApi('activity/mumbit/doUserLaunch',{},'jmX08Ymd',)
                print('开启分享结果：'.format(doUserLaunchResult['message']))
            print('当前账号已获赞{}，还需{}个点赞'.format(judgeStatus['data']['help_num'],judgeStatus['data']['need_help_num']))

            # 领取满助力奖励
            if int(judgeStatus['data']['help_num']) >= 20:
                print('已达到领奖条件，开始领取奖励')
                getRewardResult = self.getApi('activity/mumbit/draw','jmX08Ymd')
                print(getRewardResult['message'])

            # 助力好友
            print('开始助力好友')
            if len(self.motherDayShareCode) == 0:
                print('未发现任何助力码')
            for i in range(len(self.motherDayShareCode)):
                userLaunchInfo = self.getApi('activity/mumbit/getUserLaunchInfo','jmX08Ymd',(('share_ident', self.motherDayShareCode[i]),))
                if userLaunchInfo['code'] == 2101:
                    print('该好友未开启分享')
                else:
                    friendName = userLaunchInfo['data']['nickname']
                    launchId = userLaunchInfo['data']['launchId']
                    data = '{"launch_id":"' + str(launchId) +'","share_ident":"' + self.motherDayShareCode[i] + '"}'
                    doUserHelpResult = self.postApi('activity/mumbit/doUserHelp',data,'jmX08Ymd')
                    print('助力好友{}结果：{}'.format(friendName,doUserHelpResult['message']))
                    # 休息5秒，防止接口频繁
                    time.sleep(5)
        else:
            print('抱歉，该活动已结束')


    def main(self):
        try:
            # 主会场活动
            self.doTask()
            # 车主分会场活动
            self.doCarTask()
            # 天天抽奖活动
            self.draw()
            # 每日一答
            self.dayAnswer()
            # 母亲节晒妈活动
            self.mothersDayTask()
        except:
            pass
    
def readConfig(configPath):
    with open(configPath,encoding='UTF-8') as fp:
        config = json.load(fp)
    return config

if __name__ == '__main__':
    rootDir = os.path.dirname(os.path.abspath(__file__))
    configPath = rootDir + "/config.json"
    config = readConfig(configPath)
    for i in range(len(config['cookie'])):
        user = getCCB(config['cookie'][i],config['shareCode'])
        if user.getUserInfo():
            user.main()
        else:
            print('\n账号{}已失效，请及时更新Cookie'.format(i+1))
