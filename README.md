<div align="center">

# Madoka

一个基于 Graia 和 Mirai 的快速、可配置、可自定义插件的 QQ 机器人

> 只要将想要守护的事物一直守护到底就好了。

[![Release](https://img.shields.io/github/v/release/MadokaProject/Application)](https://github.com/MadokaProject/Application/releases/latest)
[![Python](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue)](https://docs.python.org/zh-cn/3.9/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/MadokaProject/Madoka/release.svg)](https://results.pre-commit.ci/latest/github/MadokaProject/Madoka/release)
[![License](https://img.shields.io/badge/license-AGPL--v3-green)](https://www.gnu.org/licenses/agpl-3.0.html)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![docs](https://img.shields.io/badge/docs-readme-28afa0)](https://madoka.colsrch.cn/)

</div>

> Madoka 是一个非盈利的开源项目，仅供交流学习使用。请勿用于商业或非法用途，因使用而与腾讯公司产生的一切纠纷均与原作者无关。

## 部署流程

请查看文档: https://madoka.colsrch.cn/doc/

## 项目版本管理

1. [Git 分支开发工作流](./docs/GIT_BRANCH_FLOW.md)

## 项目目录结构说明

```
madoka
├── app ······················· 程序主体
│   ├── console ··············· 控制台模块
│   ├── core ·················· 核心模块
│   │   ├── app.py ············ 应用主体
│   │   ├── commander.py······· 命令委托管理器
│   │   ├── config.py ········· 系统配置读取器
│   │   ├── env.config.ini ···· 示例系统配置文件
│   │   └── settings.py ······· 在线配置文件
│   ├── entities ·············· 实体模块
│   │   ├── game.py ··········· 游戏实体
│   │   ├── group.py ·········· 群实体
│   │   └── user.py ··········· 用户实体
│   ├── event ················· 事件模块
│   ├── extend ················ 扩展模块
│   ├── plugin ················ 插件模块
│   ├── resource ·············· 资源目录
│   ├── trigger ··············· 预处理模块
│   └── util ·················· 工具模块
│       ├── control.py ········ 管理工具
│       ├── cut_string.py ····· 字符串断行工具
│       ├── dao.py ············ 数据库访问接口
│       ├── decorator.py ······ 装饰器存放处
│       ├── msg.py ············ 消息存储接口
│       ├── network.py ········ 网络工具
│       ├── online_config.py ·· 在线配置工具
│       ├── other.py ·········· 其他工具
│       ├── phrases.py ········ 快捷回复消息
│       ├── send_message.py ··· 发送消息函数
│       ├── text2image.py ····· 文本转图片工具
│       └── tools.py··········· 工具函数
├── CHANGELOG.md ·············· 更新日志
├── k8s ······················· Kubernetes 配置
├── main.py ··················· 应用执行入口
├── requirements.txt ·········· 项目依赖
└── README.md ················· 项目介绍
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
