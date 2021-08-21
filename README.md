# QQ-bot

## Build Setup

```bash
# install dependencies
$ pip install -r requirements.txt

# Start the mirai service and Configuration profile
# Native debug
$ python main.py

# Run on the server
$ screen -S qq-bot
$ sh run.sh
```

## 部署流程

### 运行前配置

本应用与数据库相关联，使用前需要先运行 `qq-bot_mysql`，并补全 `app/core/env.config.py` → `app/core/config.py` 文件

> 请注意您需要拥有 MySQL 数据库服务，否则无法正常使用本应用

### 克隆项目

``` bash
git clone https://e.coding.net/jxsfgz/qq-bot/python.git QQ-bot
```

### 安装依赖

``` bash
pip install -r requirements.txt
```

### 运行

#### Linux

``` bash
sh run.sh
```

#### Windows

``` cmd
python main.py
```

## 项目版本管理

1. [Git 分支开发工作流](./docs/GIT_BRANCH_FLOW.md)

## 项目目录结构说明

```
├───app                         程序主体
│   ├───api                     api 存放目录
│   │   └───sign.py             api: 腾讯AI请求之前或之后处理函数
│   ├───core                    核心目录
│   │   └───config.py           项目配置文件
│   │   └───controller.py       核心控制器
│   ├───entities                实体控制
│   ├───event                   其他监听事件存放目录
│   ├───extend                  定时、循环执行事件存放目录
│   ├───plugin                  插件（指令）存放目录
│   └───util                    工具函数存放目录
│       └───dao.py              数据访问接口
│       └───decorator.py        管理员鉴权接口
│       └───msg.py              消息记录函数
│       └───permission.py       鉴权接口
│       └───tools.py            工具函数
├───.gitignore                  git 提交忽略文件
├───main.py                     应用执行入口
├───requirements.txt            用于描述应用的依赖关系
├───README.md                   项目说明文件
```

## 依赖

1. [`mirai`](https://github.com/mamoe/mirai): 即 `mirai-core`, 一个高性能, 高可扩展性的 QQ 协议库
2. [`mirai-console-loader`](https://github.com/iTXTech/mirai-console-loader): 模块化、轻量级且支持完全自定义的 `mirai` 加载器。
3. [`mirai-console`](https://github.com/mamoe/mirai-console): 一个基于 `mirai` 开发的插件式可扩展开发平台
4. [`mirai-api-http`](https://github.com/project-mirai/mirai-api-http): 提供与 `mirai` 交互方式的 `mirai-console` 插件
5. [`Graia Application`](https://github.com/GraiaProject/Application): 一个设计精巧, 协议实现完备的, 基于 `mirai-api-http`
   的即时聊天软件自动化框架.