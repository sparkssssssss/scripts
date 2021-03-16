#!/usr/bin/env bash
#author:spark
#需要docker环境
#copy本文件到scripts映射的文件夹
#新建diyscripts文件夹,并映射到容器目录/jd/diyscripts
#需要同步的仓库,比如i-chenzhe,则进入diyscripts 运行 git clone https://github.com/i-chenzhe/qx.git i-chenzhe 
#/bin/bash /jd/scripts/git_diy.sh  i-chenzhe       copy到diy.sh最后一行即可
#群文件sendinfo.js sendinfo.sh两个文件请放到scripts映射目录下,如没有,则没有通知消息

#操作之前请备份,信息丢失,概不负责.
#操作之前请备份,信息丢失,概不负责.
#操作之前请备份,信息丢失,概不负责.

if [ $# != 1 ] ; then
  echo "USAGE: $0 author"
  exit 1;
fi

author=$1
diyscripts=/jd/diyscripts/${author}
if [ ! -d "$diyscripts" ]; then
  echo -e "${author}仓库不存在,确认后重试!"
  exit 0
fi
cd ${diyscripts}
branch=`git symbolic-ref --short -q HEAD`
git fetch --all
git reset --hard origin/$branch
git pull
gitpullstatus=$?

rand(){
    min=$1
    max=$(($2-$min+1))
    num=$(cat /proc/sys/kernel/random/uuid | cksum | awk -F ' ' '{print $1}')
    echo $(($num%$max+$min))
}

function addnewcron {
  addname=""
  cd ${diyscripts}
  for js in `ls *.js`;
    do 
      croname=`echo "${author}_$js"|awk -F\. '{print $1}'`
      script_date=`cat  $js|grep ^[0-9]|awk '{print $1,$2,$3,$4,$5}'|egrep -v "[a-zA-Z]|:|\."|sort |uniq|head -n 1`
      [ -z "${script_date}" ] && script_date=`cat  $js|grep -Eo "([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9]+[,-].*) ([0-9]+|\*|[0-9][,-].*)"|sort |uniq|head -n 1`
      [ -z "${script_date}" ] && cron_min=$(rand 1 59) && cron_hour=$(rand 7 9) && script_date="${cron_min} ${cron_hour} * * *"
      [ $(grep -c -w "$croname" /jd/config/crontab.list) -eq 0 ] && sed -i "/hangup/a${script_date} bash jd $croname"  /jd/config/crontab.list && addname="${addname}\n${croname}" && echo -e "添加了新的脚本${croname}." && bash jd ${croname} now
      if [ ! -f "/jd/scripts/${author}_$js" ];then
        \cp $js /jd/scripts/${author}_$js
      else
        change=$(diff $js /jd/scripts/${author}_$js)
        [ -n "${change}" ] && \cp $js /jd/scripts/${author}_$js && echo -e "${author}_$js 脚本更新了."
      fi
  done
  #[ "$addname" != "" ] && [ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh "${author}新增自定义脚本" "${addname}"

}

function delcron {
  delname=""
  cronfiles=$(grep "$author" /jd/config/crontab.list|grep -v "^#"|awk -F"${author}_" '{print $2}')
  for filename in $cronfiles;
    do
      if [ ! -f "${diyscripts}/${filename}.js" ]; then 
        sed -i "/\<bash jd ${author}_${filename}\>/d" /jd/config/crontab.list && echo -e "删除失效脚本${filename}."
	    delname="${delname}\n${author}_${filename}"
      fi
  done
  #[ "$delname" != "" ] && [ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh  "${author}删除失效脚本" "${delname}" 
}

if [[ ${gitpullstatus} -eq 0 ]]
then
  addnewcron
  delcron
else
  echo -e "$author 仓库更新失败了."
  #[ -f "/jd/scripts/sendinfo.sh" ] && /bin/bash  /jd/scripts/sendinfo.sh "自定义仓库更新失败" "$author"
fi

exit 0
