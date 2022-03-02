#!/bin/bash
checkPython()
{
    V1=3
    V2=8

    echo -e "\033[34m Checking the Python version... \033[0m"
    echo "need python version is : $V1.$V2+"
    
    U_V1=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $1}'`
    U_V2=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $2}'`
    U_V3=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $3}'`
    
    echo "your python version is : $U_V1.$U_V2.$U_V3"
    
    if [ $U_V1 -lt $V1 ];then
        echo -e "\033[31m Your Python version does not meet the minimum requirements, Madoka requires python version 3.8 and above! \033[0m"
        exit 1
    elif [ $U_V1 -eq $V1 ];then     
        if [ $U_V2 -lt $V2 ];then 
            echo -e "\033[31m Your Python version does not meet the minimum requirements, Madoka requires python version 3.8 and above! \033[0m"
            exit 1
        fi    
    fi

    echo -e "\033[32m Your Python version meets the requirements \033[0m"
}
checkPython

echo -e "\033[34m Madoka Base Configuration \033[0m"
read -p "Please enter the Madoka repository directory: ($PWD/Madoka) " madoka_dir
[ ! $madoka_dir ] && madoka_dir="$PWD/Madoka"
read -p "Please enter the mirai-api-http host: (127.0.0.1) " mcl_host
[ ! $mcl_host ] && mcl_host="127.0.0.1"
read -p "Please enter the mirai-api-http port: (8080) " mcl_port
[ ! $mcl_port ] && mcl_port="8080"
read -p "Please enter the mirai login QQ number: " qq
[ ! $qq ] && echo -e "\033[31m QQ number cannot be empty! \033[0m" && exit
read -p "Please enter the mirai-api-http verify_key: " verify_key
read -p "Please enter the robot name: " bot_name
[ ! $bot_name ] && echo -e "\033[31m Robot name cannot be empty! \033[0m" && exit
read -p "Please enter the QQ number of the robot owner: " master_qq
[ ! $master_qq ] && echo -e "\033[31m Robot owner QQ number cannot be empty! \033[0m" && exit
read -p "Please enter the robot owner nickname: " master_name
[ ! $master_name ] && echo -e "\033[31m Robot owner nickname cannot be empty! \033[0m" && exit

echo -e "\033[34m MySQL Configuration \033[0m"
read -p "Please enter the mysql host: (127.0.0.1) " mysql_host
[ ! $mysql_host ] && mysql_host="127.0.0.1"
read -p "Please enter the mysql port: (3306) " mysql_port
[ ! $mysql_port ] && mysql_port="8080"
read -p "Please enter the mysql username: (root) " mysql_username
[ ! $mysql_username ] && mysql_username="root"
read -p "Please enter the mysql password: " -s mysql_password
echo
[ ! $mysql_password ] && echo -e "\033[31m MySQL password cannot be empty! \033[0m" && exit
read -p "Please enter the mysql database: " mysql_database
[ ! $mysql_database ] && echo -e "\033[31m MySQL database cannot be empty! \033[0m" && exit

echo -e "\033[34m Economic System Configuration \033[0m"
read -p "please enter currency name: (金币) " coin_name
[ ! $coin_name ] && coin_name="金币"

echo -e "\033[34m WebServer configuration \033[0m"
read -p "please enter host: (0.0.0.0) " web_host
[ ! $web_host ] && web_host="0.0.0.0"
read -p "please enter port: (8080) " web_port
[ ! $web_port ] && web_port="8080"

madoka_repo="https://github.com/MadokaProject/Madoka.git"
madoka_branch="master"

git clone -b $madoka_branch $madoka_repo $madoka_dir
cd $madoka_dir

echo "[bot]
host = $mcl_host
port = $mcl_port
qq = $qq
verify_key = $verify_key
bot_name = $bot_name
master_qq = $master_qq
master_name = $master_name

[mysql]
host = $mysql_host
port = $mysql_port
user = $mysql_username
password = $mysql_password
database = $mysql_database

[coin_settings]
name = $coin_name

[webserver]
host = $web_host
port = $web_port
debug = False" > $madoka_dir/app/core/config.ini

read -p "Install the pip package in the current environment: (yes/no) " flag
[ ! $flag ] && flag="no"
if [ $flag == "yes" ];then
    echo -e "\033[32m Installing the pip package... \033[0m"
    pip install -r $madoka_dir/requirements.txt
else
    echo -e "\033[31m pip package is not installed \033[0m"
fi

echo -e "\033[32m Successfully! \033[0m"

python main.py