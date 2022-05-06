<div align="center">

# Madoka

一个基于 Graia 和 Mirai 的快速、可配置、可自定义插件的 QQ 机器人

> 只要将想要守护的事物一直守护到底就好了。

[![License](https://img.shields.io/badge/license-AGPL--v3-green)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python](https://img.shields.io/badge/python-3.8-blue)](https://docs.python.org/zh-cn/3.8/)
[![Release](https://img.shields.io/github/v/release/MadokaProject/Application)](https://github.com/MadokaProject/Application/releases/latest)

</div>

> Madoka 是一个非盈利的开源项目，仅供交流学习使用。请勿用于商业或非法用途，因使用而与腾讯公司产生的一切纠纷均与原作者无关。

## Build Setup

```bash
# install dependencies
$ pip install -r requirements.txt

# Start the mirai service and Configuration profile
# Run on the server
$ screen -S qq-bot
$ python main.py
```

## 部署流程

请查看文档: https://madoka.colsrch.cn/doc/

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

- [Madoka](https://github.com/MadokaProject/Madoka.git): Madoka 主体
- [Plugins](https://github.com/MadokaProject/Plugins.git): Madoka 的官方插件库（你也可以提交 PR 来丰富此插件库）
- [Web](https://github.com/MadokaProject/Web.git): 机器人 Web 控制系统(计划中)
- [Loader](https://github.com/MadokaProject/Loader.git): 懒人工具(或许有？)

## 依赖

1. [`mirai`](https://github.com/mamoe/mirai): 即 `mirai-core`, 一个高性能, 高可扩展性的 QQ 协议库
2. [`mirai-console-loader`](https://github.com/iTXTech/mirai-console-loader): 模块化、轻量级且支持完全自定义的 `mirai` 加载器。
3. [`mirai-console`](https://github.com/mamoe/mirai-console): 一个基于 `mirai` 开发的插件式可扩展开发平台
4. [`mirai-api-http`](https://github.com/project-mirai/mirai-api-http): 提供与 `mirai` 交互方式的 `mirai-console` 插件
5. [`Graia Ariadne`](https://github.com/GraiaProject/Ariadne): 一个设计精巧, 协议实现完备的, 基于 `mirai-api-http v2`
   的即时聊天软件自动化框架.
6. [`Arclet-Alconna`](https://github.com/ArcletProject/Alconna): 一个直观的、高性能、泛用的命令行参数解析器集成库