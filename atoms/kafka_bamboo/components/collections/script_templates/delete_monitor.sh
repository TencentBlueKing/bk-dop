#!/bin/bash

###  kafka删除监控脚本

time_format="date +'%Y-%m-%d %H:%M:%S'"
NOW="echo [\`$time_format\`][PID:$$]"

##### 可在脚本执行成功的逻辑分支处调用，打印当时的时间戳及PID。
job_success()
{
    MSG="$*"
    echo "$(eval "${NOW}") job_success:[$MSG]"

}

##### 可在脚本执行失败的逻辑分支处调用，打印当时的时间戳及PID。
job_fail()
{
    MSG="$*"
    echo "$(eval "${NOW}") job_fail:[$MSG]"

}

delete_crontab(){
   sed -i '/# kafka push metrics per min/d' /var/spool/cron/root
   sed -i '/kafka_get_metrics.py/d' /var/spool/cron/root
   job_success "delete monitor crontab success"
}

delete_crontab
exit 0
