#!/usr/bin/env bash
# version: 1.0
# modify:
# function:
# 利用蓝鲸JOD平台去快速执行初始化脚本,机器之间建立用户免认证登录。
# 执行状态码不同错代表不同情况：
# 0  ：脚本执行成功
# 128：没有key需要同步authorized_keys文件
# 129：ssh免认证检测失败

# shellcheck disable=SC1083

hadoop_user=$1
hadoop_ssh_authorized_keys="/home/${hadoop_user}/.ssh/authorized_keys"
hadoop_ssh_id_rsa_path="/data/package/hadoop/ssh/"

create_auth_free_login() {

	# 检查authorized_keys文件是否存在
	if [ ! -f ${hadoop_ssh_authorized_keys} ]; then
		touch $hadoop_ssh_authorized_keys
	fi
	chmod 600 $hadoop_ssh_authorized_keys
	chown -R ${hadoop_user}:${hadoop_user} "/home/${hadoop_user}/.ssh/"

	# 追加机器公钥到authorized_keys文件
  # shellcheck disable=SC2045
  for file_name in $(ls "$hadoop_ssh_id_rsa_path")
      do
          local file="$hadoop_ssh_id_rsa_path""$file_name"
          local exist_flag
          exist_flag=$(grep -c -f "$file" "$hadoop_ssh_authorized_keys")
          if [[ ${exist_flag} -lt 1 ]]; then
            cat "$file" >>"$hadoop_ssh_authorized_keys"
          else
            echo "id_rsa already add into authorized_keys"
          fi

          rm -f "$file"
      done


}



main() {
	create_auth_free_login
	
}
main
echo "success"
exit 0
