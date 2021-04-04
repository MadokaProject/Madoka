## QQ-bot（QQ机器人）

### 使用方法

本程序与数据库相关联，使用前需要先创建一个数据库，并补全 `app/core/env.config.py` → `app/core/config.py` 文件

#### 克隆

``` bash
git clone https://e.coding.net/jxsfgz/qq-bot/python.git QQ-bot
```

#### 安装库

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

### 鸣谢&相关项目

- [`mirai`](https://github.com/mamoe/mirai): 即 `mirai-core`, 一个高性能, 高可扩展性的 QQ 协议库
- [`mirai-console-loader`](https://github.com/iTXTech/mirai-console-loader): 模块化、轻量级且支持完全自定义的 `mirai` 加载器。
- [`mirai-console`](https://github.com/mamoe/mirai-console): 一个基于 `mirai` 开发的插件式可扩展开发平台
- [`mirai-api-http`](https://github.com/project-mirai/mirai-api-http): 提供与 `mirai` 交互方式的 `mirai-console` 插件
- [`Graia Application`](https://github.com/GraiaProject/Application): 一个设计精巧, 协议实现完备的, 基于 `mirai-api-http` 的即时聊天软件自动化框架.