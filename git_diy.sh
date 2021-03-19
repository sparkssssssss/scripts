#!/usr/bin/env bash
#author:spark
#需要docker环境,下载本文件到容器内任意位置,以下示例是放到了/jd/scripts
#举个栗子,我们要拉取大佬i-chenzhe的qx脚本仓库,则在计划任务内添加以下任务(半小时拉取一次,时间自定):
###-> */30 * * * *  /bin/bash /jd/scripts/git_diy.sh  i-chenzhe  qx     <-###
#或者添加到到diy.sh最后一行即可,跟随pull的频率,不过pull的频率远远跟不上柘大佬的节奏!
#如果仓库内有不想执行的脚本,注释即可!
#群文件sendinfo.js sendinfo.sh两个文件请放到scripts映射目录下,如没有,则没有通知消息

#操作之前请备份,信息丢失,概不负责.
#操作之前请备份,信息丢失,概不负责.
#操作之前请备份,信息丢失,概不负责.

declare -A BlackListDict
author=$1
repo=$2
#指定仓库屏蔽关键词,不添加计划任务,多个按照格式二
BlackListDict['i-chenzhe']="_get"
BlackListDict['sparkssssssss']="smzdm|tg|xxxxxxxx"

blackword=${BlackListDict["${author}"]}
blackword=${blackword:-"wojiushigejimo"}

if [ $# != 2 ] ; then
  echo "USAGE: $0 author repo"
  exit 0;
fi

diyscriptsdir=/jd/diyscripts
mkdir -p ${diyscriptsdir}

if [ ! -d "$diyscriptsdir/${author}_${repo}" ]; then
  echo -e "${author}本地仓库不存在,从gayhub拉取ing..."
  cd ${diyscriptsdir} &&  git clone https://github.com/${author}/${repo}.git ${author}_${repo}
  gitpullstatus=$?
  [ $gitpullstatus -eq 0 ] && echo -e "${author}本地仓库拉取完毕"
  [ $gitpullstatus -ne 0 ] && echo -e "${author}本地仓库拉取失败,请检查!" && exit 0
else
  cd ${diyscriptsdir}/${author}_${repo}
  branch=`git symbolic-ref --short -q HEAD`
  git fetch --all
  git reset --hard origin/$branch
  git pull
  gitpullstatus=$?
fi

rand(){
    min=$1
    max=$(($2-$min+1))
    num=$(cat /proc/sys/kernel/random/uuid | cksum | awk -F ' ' '{print $1}')
    echo $(($num%$max+$min))
}

function addnewcron {
  addname=""
  cd ${diyscriptsdir}/${author}_${repo}
  for js in `ls *.js|egrep -v $blackword`;
    do 
      croname=`echo "${author}_$js"|awk -F\. '{print $1}'`
      script_date=`cat  $js|grep ^[0-9]|awk '{print $1,$2,$3,$4,$5}'|egrep -v "[a-zA-Z]|:|\."|sort |uniq|head -n 1`
      [ -z "${script_date}" ] && script_date=`cat  $js|grep -Eo "([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9][,-].*)"|sort |uniq|head -n 1`
      [ -z "${script_date}" ] && cron_min=$(rand 1 59) && cron_hour=$(rand 7 9) && script_date="${cron_min} ${cron_hour} * * *"
      [ $(grep -c -w "$croname" /jd/config/crontab.list) -eq 0 ] && sed -i "/hangup/a${script_date} bash jd $croname"  /jd/config/crontab.list && addname="${addname}\n${croname}" && echo -e "添加了新的脚本${croname}." && bash jd ${croname} now >/dev/null &
      if [ ! -f "/jd/scripts/${author}_$js" ];then
        \cp $js /jd/scripts/${author}_$js
      else
        change=$(diff $js /jd/scripts/${author}_$js)
        [ -n "${change}" ] && \cp $js /jd/scripts/${author}_$js && echo -e "${author}_$js 脚本更新了."
      fi
  done
  [ "$addname" != "" ] && [ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh "${author}新增自定义脚本" "${addname}"

}

function delcron {
  delname=""
  cronfiles=$(grep "$author" /jd/config/crontab.list|grep -v "^#"|awk '{print $8}'|awk -F"${author}_" '{print $2}')
  for filename in $cronfiles;
    do
      if [ ! -f "${diyscriptsdir}/${author}_${repo}/${filename}.js" ]; then 
        sed -i "/\<bash jd ${author}_${filename}\>/d" /jd/config/crontab.list && echo -e "删除失效脚本${filename}."
	delname="${delname}\n${author}_${filename}"
      fi
  done
  [ "$delname" != "" ] && [ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh  "${author}删除失效脚本" "${delname}" 
}

if [[ ${gitpullstatus} -eq 0 ]]
then
  addnewcron
  delcron
else
  echo -e "$author 仓库更新失败了."
  [ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh "自定义仓库更新失败" "$author"
fi

exit 0
