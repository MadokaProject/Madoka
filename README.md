# PyIBot

一个基于 Graia 和 Mirai 的快速、可配置、可自定义插件的 QQ 机器人

> PyIBot 是一个非盈利的开源项目，仅供交流学习使用。请勿用于商业或非法用途，因使用而与腾讯公司产生的一切纠纷均与原作者无关。

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

推荐使用官方启动器 [mirai-console-loader](https://github.com/iTXTech/mirai-console-loader) (mcl)
自行启动 [mirai](https://github.com/mamoe/mirai) 与 [mirai-api-http](https://github.com/mamoe/mirai-api-http) 插件。

### 运行前配置

本应用与数据库相关联，使用前请创建一个数据库如 `qqbot` ，并补全 `app/core/env.config.ini` → `app/core/config.ini` 文件

> 请注意你需要拥有 MySQL 数据库服务，否则无法正常使用本应用

### 克隆项目

``` bash
git clone https://github.com/PyIBot/Application.git PyIBot
```

### 安装依赖

建议使用 Virtualenv 或 Conda 等虚拟环境工具

``` bash
pip install -r requirements.txt
```

### 安装插件

推荐使用 [Web](https://github.com/PyIBot/Web.git) 端一键安装，手动安装如下：

前往 [Plugins](https://github.com/PyIBot/Plugins.git) 仓库下载所需插件至 `app/plugin` 目录，并在该目录的 `__init__.py` 文件中添加对应插件文件名。

> 你可自行在该目录编写其他插件，同时欢迎你将你的插件 PR 到此插件库

### 升级插件

推荐使用 [Web](https://github.com/PyIBot/Web.git) 端一键升级，手动升级请重新下载覆盖原文件。

### 运行

#### Linux

``` bash
sh run.sh
```

#### Windows

``` cmd
python main.py
```

## 升级

- 推荐使用 [Web](https://github.com/PyIBot/Web.git) 端一键升级。
- 手动升级：git pull 拉取。

## 项目版本管理

1. [Git 分支开发工作流](./docs/GIT_BRANCH_FLOW.md)

## 项目目录结构说明

```
├───app                         程序主体
│   ├───api                     api 存放目录
│   │   └───doHttp.py             通用Http异步请求函数
│   ├───core                    核心目录
│   │   └───config.ini           项目配置文件
│   │   └───controller.py       核心控制器
│   ├───entities                实体控制
│   ├───event                   其他监听事件存放目录
│   ├───extend                  定时、循环执行事件存放目录
│   ├───plugin                  插件（指令）存放目录
│   ├───resource                资源文件存放目录
│   ├───tirgger                 预处理函数存放目录
│   └───util                    工具函数存放目录
│       ├───CutString.py        字符串自动断行工具
│       ├───dao.py              数据库访问接口
│       ├───decorator.py        管理员鉴权接口
│       ├───msg.py              消息存储函数
│       ├───permission.py       鉴权接口
│       ├───text2image.py       图片生成工具
│       └───tools.py            工具函数
├───.gitignore                  git 提交忽略文件
├───initDB.py                   初始化数据库函数
├───main.py                     应用执行入口
├───requirements.txt            项目运行环境依赖包
├───README.md                   项目说明文件
```

## 说明

请勿将其用于商业或非法用途。

## 相关项目

- [Application](https://github.com/PyIBot/Application.git): PyIBot 主体
- [Plugins](https://github.com/PyIBot/Plugins.git): PyIBot 的官方插件库（你也可以提交 PR 来丰富此插件库）
- [Web](https://github.com/PyIBot/Web.git): 机器人 Web 控制系统(计划中)
- [Loader](https://github.com/PyIBot/Loader.git): 懒人工具(或许有？)

## 依赖

1. [`mirai`](https://github.com/mamoe/mirai): 即 `mirai-core`, 一个高性能, 高可扩展性的 QQ 协议库
2. [`mirai-console-loader`](https://github.com/iTXTech/mirai-console-loader): 模块化、轻量级且支持完全自定义的 `mirai` 加载器。
3. [`mirai-console`](https://github.com/mamoe/mirai-console): 一个基于 `mirai` 开发的插件式可扩展开发平台
4. [`mirai-api-http`](https://github.com/project-mirai/mirai-api-http): 提供与 `mirai` 交互方式的 `mirai-console` 插件
5. [`Graia Application`](https://github.com/GraiaProject/Application): 一个设计精巧, 协议实现完备的, 基于 `mirai-api-http`
   的即时聊天软件自动化框架.