#!/usr/bin/env bash
#author:spark
#需要docker环境,下载本文件到容器内任意位置,以下示例是放到了/jd/scripts
#举个栗子,我们要拉取大佬i-chenzhe的脚本仓库,则在计划任务内添加以下任务(半小时拉取一次,时间自定):
#github:https://github.com/monk-coder/dust/tree/dust/i-chenzhe,
#仓库作者为monk-coder
#仓库repo为dust
#仓库文件夹为i-chenzhe
#添加以下命令到计划任务↓
#########-> */30 * * * *  bash /jd/scripts/git_diy.sh monk-coder dust i-chenzhe     <-########
#或者添加到到diy.sh最后一行即可,跟随pull的频率,不过pull的频率远远跟不上柘大佬的节奏!
#脚本每次运行会检测脚本内的定时任务是否更新,如果有自定义脚本执行时间,不想随脚本更新,请在脚本计划任务后>添加注释 #nochange
#如果仓库内有不想执行的脚本,注释即可!
#群文件sendinfo.js sendinfo.sh两个文件请放到scripts映射目录下,如没有,则没有通知消息

#操作之前请备份,信息丢失,概不负责.
#操作之前请备份,信息丢失,概不负责.
#操作之前请备份,信息丢失,概不负责.

declare -A BlackListDict
author=$1
repo=$2
dir=$3
#指定仓库屏蔽关键词,不添加计划任务,多个按照格式二
BlackListDict['i-chenzhe']="_get|backup"
BlackListDict['sparkssssssss']="smzdm|tg|xxxxxxxx"

blackword=${BlackListDict["${author}"]}
blackword=${blackword:-"wojiushigejimo"}

if [ $# -lt 2 ] && [ $# -gt 3 ] ; then
  echo "USAGE: $0 author repo         #for all repo"
  echo "USAGE: $0 author repo  dir    #for special dir of the repo"
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
  if [ -n $dir ];then
    cd ${diyscriptsdir}/${author}_${repo}/$dir
    author=${author}_${dir}
  else
    cd ${diyscriptsdir}/${author}_${repo}
  fi
  [ $(grep -c "#${author}" /jd/config/crontab.list) -eq 0 ] && sed -i "/hangup/a#${author}" /jd/config/crontab.list
  
  for jspath in `ls *.js|egrep -v $blackword`; 
  #for jspath in `find ./ -name  "*.js"|egrep -v $blackword`; 
  #for js in `ls *.js|egrep -v $blackword`;
    do 
      newflag=0
      js=`echo $jspath|awk -F'/' '{print $NF}'` 
      croname=`echo "${author}_$js"|awk -F\. '{print $1}'`
      script_date=`cat  $js|grep ^[0-9]|awk '{print $1,$2,$3,$4,$5}'|egrep -v "[a-zA-Z]|:|\."|sort |uniq|head -n 1`
      [ -z "${script_date}" ] && script_date=`cat  $jspath|grep -Eo "([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9][,-].*)"|sort |uniq|head -n 1`
      [ -z "${script_date}" ] && cron_min=$(rand 1 59) && cron_hour=$(rand 7 9) && script_date="${cron_min} ${cron_hour} * * *"
      [ $(grep -c -w "$croname" /jd/config/crontab.list) -eq 0 ] && sed -i "/#${author}/a${script_date} bash jd $croname"  /jd/config/crontab.list && addname="${addname}\n${croname}" && echo -e "添加了新的脚本${croname}." && newflag=1;
      [ $newflag -eq 1 ] && bash jd ${croname} now >/dev/null &

      if [ $(egrep -v "^#|nochange" /jd/config/crontab.list|grep -c -w "$croname" ) -eq 1 ];then
          old_script_date=$(grep -w "$croname" /jd/config/crontab.list|awk '{print $1,$2,$3,$4,$5}')
	  [ "${old_script_date}" != "${script_date}" ] && sed -i "/bash jd $croname/d" /jd/config/crontab.list && sed -i "/#${author}/a${script_date} bash jd $croname"  /jd/config/crontab.list
      fi

      if [ ! -f "/jd/scripts/${author}_$js" ];then
        \cp $jspath /jd/scripts/${author}_$js
      else
        change=$(diff $jspath /jd/scripts/${author}_$js)
        [ -n "${change}" ] && \cp $jspath /jd/scripts/${author}_$js && echo -e "${author}_$js 脚本更新了."

      fi
  done
  [ "$addname" != "" ] && [ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh "${author}新增自定义脚本" "${addname}"

}

function delcron {
  delname=""
  if [ -n $dir ];then
    jspath=${diyscriptsdir}/${author}_${repo}/$dir
    author=${author}_${dir}
  else
    jspath=${diyscriptsdir}/${author}_${repo}
  fi
  cronfiles=$(grep "$author" /jd/config/crontab.list|grep -v "^#"|awk '{print $8}'|awk -F"${author}_" '{print $2}')
  for filename in $cronfiles;
    do
      if [ ! -f "$jspath/${filename}.js" ]; then 
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
