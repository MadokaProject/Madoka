# Changelog

## [4.0.2](https://github.com/MadokaProject/Madoka/compare/v4.0.1...v4.0.2) (2022-10-16)


### Bug Fixes

* 调整获取远程版本的url, 导出requirements.txt ([61eefe2](https://github.com/MadokaProject/Madoka/commit/61eefe25c2147bf0a245f013fae541b226648471))

## [4.0.1](https://github.com/MadokaProject/Madoka/compare/v4.0.0...v4.0.1) (2022-10-16)


### Bug Fixes

* 添加yaml依赖, 修复已知问题 ([e98ba46](https://github.com/MadokaProject/Madoka/commit/e98ba46bb78ce45beb069d4aaf508d9958c67214))

## [4.0.0](https://github.com/MadokaProject/Madoka/compare/v3.3.0...v4.0.0) (2022-10-16)


### ⚠ BREAKING CHANGES

* **config:** 调整配置文件位置至 app/data 目录, 需要手动修改配置文件格式
* use Python features not available in python 3.8.

### Features

* **commander:** 可以指定无子命令匹配时运行的方法了，可以在子命令匹配时添加权限验证 ([a85a082](https://github.com/MadokaProject/Madoka/commit/a85a082523e90daa071daff3c6516a10eba5d41b))
* **commander:** 对Alconna的部分封装 ([6ecab37](https://github.com/MadokaProject/Madoka/commit/6ecab37b55127c629077feab44e04126ecffbf5b))
* **commander:** 新增事件过滤 ([19090b2](https://github.com/MadokaProject/Madoka/commit/19090b2711df2fa821a85423839b2df3e26fd508))
* **commander:** 新增插件限频，支持全局配置、插件配置、插件命令配置 ([97cd0e5](https://github.com/MadokaProject/Madoka/commit/97cd0e54496b25dfe4e06ae5b568b553ebf18fce))
* **command:** 不允许单文件初始化多个命令 ([7f76463](https://github.com/MadokaProject/Madoka/commit/7f76463e391fc943b3683ed3494b256362e04136))
* **command:** 命令不用指定命令头了 ([7f76463](https://github.com/MadokaProject/Madoka/commit/7f76463e391fc943b3683ed3494b256362e04136))
* **command:** 命令半自动补全 ([7f76463](https://github.com/MadokaProject/Madoka/commit/7f76463e391fc943b3683ed3494b256362e04136))
* **core:** 优化重启 ([7f76463](https://github.com/MadokaProject/Madoka/commit/7f76463e391fc943b3683ed3494b256362e04136))
* drop support for Python 3.8 ([0d03fd2](https://github.com/MadokaProject/Madoka/commit/0d03fd217699f732b73e1ad9d8964e3f72a3f118))
* **graia:** 封装了部分 graia 方法，通过消息队列发送消息 ([8549e51](https://github.com/MadokaProject/Madoka/commit/8549e512553f708098e9ee1cbb888d724281b5b5))
* **mq:** 一个简易的消息队列，控制消息发送速度 ([8549e51](https://github.com/MadokaProject/Madoka/commit/8549e512553f708098e9ee1cbb888d724281b5b5))
* **mq:** 优化消息队列，使用 queue ([f794434](https://github.com/MadokaProject/Madoka/commit/f794434be17c1ecd99d4ab49aa1e6ab248adfb28))
* **sqlite:** 调整Sqlite数据库文件存储位置为 app/tmp/db 目录 ([b6fe1bc](https://github.com/MadokaProject/Madoka/commit/b6fe1bc011a516a9443b42896861ac16b853ea38))
* **util.online_config:** 读取配置时优先获取本地缓存 ([0ec433e](https://github.com/MadokaProject/Madoka/commit/0ec433e86bffd96c0923b1367249b5ce2073e717))


### Bug Fixes

* **graia:** 将检测有无指定消息发送对象提前 ([a85a082](https://github.com/MadokaProject/Madoka/commit/a85a082523e90daa071daff3c6516a10eba5d41b))
* **graia:** 消息存储异常的问题 ([b39c936](https://github.com/MadokaProject/Madoka/commit/b39c936c17187f8106cb661d96fb8c2c6224ef9d))
* **mq:** 结束时可能多发送一条消息的问题 ([b39c936](https://github.com/MadokaProject/Madoka/commit/b39c936c17187f8106cb661d96fb8c2c6224ef9d))
* **singletion:** 线程安全 ([8549e51](https://github.com/MadokaProject/Madoka/commit/8549e512553f708098e9ee1cbb888d724281b5b5))
* **util.online_config:** 获取配置为空时返回空字典 ([2cfa027](https://github.com/MadokaProject/Madoka/commit/2cfa027949f839a2fcf9130348a06e072db9b7f4))
* 切换DEBUG模式跟随用户配置命令头 ([35b325d](https://github.com/MadokaProject/Madoka/commit/35b325de312655b501b031f586c7d15ace59a466))


### Code Refactoring

* **config:** 重构配置文件，采用 yaml 格式 ([42a3d05](https://github.com/MadokaProject/Madoka/commit/42a3d059aee6ac591c6347dcb8902c7a012ee325))

## [3.3.0](https://github.com/MadokaProject/Madoka/compare/v3.2.2...v3.3.0) (2022-09-15)


### Features

* **csm:** 指令也加入群管检测 ([06c61e6](https://github.com/MadokaProject/Madoka/commit/06c61e689f1d8af97b889e419e821392d0bb9742))


### Bug Fixes

* **text2image:** 其它目录无法启动的问题 ([071b768](https://github.com/MadokaProject/Madoka/commit/071b7687d6f04636940e03ce53af245358625bae))

## [3.2.2](https://github.com/MadokaProject/Madoka/compare/v3.2.1...v3.2.2) (2022-09-08)


### Bug Fixes

* **mc_info:** 修复无法关闭监听的问题，现在listen操作无需重启了 ([925f1d5](https://github.com/MadokaProject/Madoka/commit/925f1d5fb8ff7963a641ec0585645b902fb52ffe))

## [3.2.1](https://github.com/MadokaProject/Madoka/compare/v3.2.0...v3.2.1) (2022-09-05)


### Bug Fixes

* **plugins:** 部分命令无法使用 ([#47](https://github.com/MadokaProject/Madoka/issues/47)) ([d003f92](https://github.com/MadokaProject/Madoka/commit/d003f92ae2a32cbc09838471ab78ce89d07b3869))

## [3.2.0](https://github.com/MadokaProject/Madoka/compare/v3.1.0...v3.2.0) (2022-09-05)


### Features

* **config:** 自动检查依赖包是否安装, Docker 镜像自动安装 mysql、sqlite 依赖 ([db92c63](https://github.com/MadokaProject/Madoka/commit/db92c635df856ed641187045be83e5a1daf3d1cc))
* **database:** 兼容 sqlite ([#46](https://github.com/MadokaProject/Madoka/issues/46)) ([fdc9149](https://github.com/MadokaProject/Madoka/commit/fdc914978a28886cad118b57646d40829167300e))
* **entities.game:** 好感度等级现在没有上限了。优化了一些 api ([3577a7e](https://github.com/MadokaProject/Madoka/commit/3577a7ea280149ebf0d0305949e2c4b0ff9c1912))
* **entities.user:** 优化了一些 api ([3577a7e](https://github.com/MadokaProject/Madoka/commit/3577a7ea280149ebf0d0305949e2c4b0ff9c1912))
* **exception:** 丰富异常信息 ([9c59aa4](https://github.com/MadokaProject/Madoka/commit/9c59aa4ad84fa2c89d7fe0e78ee253f3c9762067))
* **game:** 移除旧版金币迁移 ([fe391fc](https://github.com/MadokaProject/Madoka/commit/fe391fce9a08a99a0509bac7800f61cc134b1671))
* **mc_server:** 重构 mc_server 插件 ([db92c63](https://github.com/MadokaProject/Madoka/commit/db92c635df856ed641187045be83e5a1daf3d1cc))
* **orm:** 支持 sqlite 和 mysql 数据库, 优化代码实现 ([fe391fc](https://github.com/MadokaProject/Madoka/commit/fe391fce9a08a99a0509bac7800f61cc134b1671))


### Bug Fixes

* **controller:** 权限判断异常 ([fe391fc](https://github.com/MadokaProject/Madoka/commit/fe391fce9a08a99a0509bac7800f61cc134b1671))
* **database:** 修复无法初始化扩展插件数据表的问题 ([d157011](https://github.com/MadokaProject/Madoka/commit/d1570110c63802d358e2ba56c6617d535282634c))
* **database:** 默认值 ([7ae9616](https://github.com/MadokaProject/Madoka/commit/7ae9616040b8fe91d09fb0e46a50eec43bb7e245))
* **event.bot:** 戳一戳事件处理异常 ([84ddf79](https://github.com/MadokaProject/Madoka/commit/84ddf79064a9f304017d5a32180c7f5117cff5d9))
* **event.bot:** 被邀请入群处理异常 ([df2db21](https://github.com/MadokaProject/Madoka/commit/df2db21af57a40fd733f8e78b9fbff9b7986d239))
* **game:** 收租失败 ([e5d926f](https://github.com/MadokaProject/Madoka/commit/e5d926f3210898a82ee37e9f8bff91cbfedbdac4))
* **game:** 无法转账 ([975f340](https://github.com/MadokaProject/Madoka/commit/975f340b71f7f775622319711db8023ee17616ca))
* **log:** 日志持久化的问题 ([3577a7e](https://github.com/MadokaProject/Madoka/commit/3577a7ea280149ebf0d0305949e2c4b0ff9c1912))
* **mc_info:** 监听问题 ([dff0f98](https://github.com/MadokaProject/Madoka/commit/dff0f98e184330b6795776d300f32e396d6affb4))
* **online_config:** ensure_ascii False ([044802e](https://github.com/MadokaProject/Madoka/commit/044802e1c8c1e80bbbb60919b8c990c7157a50a3))
* **plugin.github:** 修改子命令结构，避免误触发 ([43adc11](https://github.com/MadokaProject/Madoka/commit/43adc11d2d52cd67c6b3f2497ede69b9a518d4b5))
* **plugin.plugin_mgr:** 群管理员权限无法使用插件开关功能 ([f425052](https://github.com/MadokaProject/Madoka/commit/f4250524df2e054b4071d323759e819b390be251))
* **plugins:** 修改插件下载链接 ([3579510](https://github.com/MadokaProject/Madoka/commit/3579510df9dabbe3d9b577b2aa0af4c7f06bd521))
* **reply:** 只能获取到第一行的内容 ([f6003b9](https://github.com/MadokaProject/Madoka/commit/f6003b9d62927d473d0d7e72a15d9d67e878f00a))
* **requirements:** 添加richuru依赖 ([eb88534](https://github.com/MadokaProject/Madoka/commit/eb885344fe1c0b176443e2629b80d0fee5951860))
* **requirements:** 锁定依赖版本 ([333ef8e](https://github.com/MadokaProject/Madoka/commit/333ef8e53ff2b6db3f73f89ee2e707599c155106))
* **send_message:** 发送消息异常捕获 ([a737711](https://github.com/MadokaProject/Madoka/commit/a73771194bac41748dc3170f105935fe363ccfc9))
* **settings:** 配置读取错误的问题 ([e810686](https://github.com/MadokaProject/Madoka/commit/e810686520c9156938ae8f39a13bf2897096a831))
* **trigger.chat:** 判断错误 ([8608fa5](https://github.com/MadokaProject/Madoka/commit/8608fa522a0dd4304136e8a456c62d200be98ee6))
* **trigger.chat:** 群聊无法触发 ([3577a7e](https://github.com/MadokaProject/Madoka/commit/3577a7ea280149ebf0d0305949e2c4b0ff9c1912))
* **trigger.mode:** 某些特殊消息触发的错误 ([3577a7e](https://github.com/MadokaProject/Madoka/commit/3577a7ea280149ebf0d0305949e2c4b0ff9c1912))

## [3.1.0](https://github.com/MadokaProject/Madoka/compare/v3.0.0...v3.1.0) (2022-07-20)


### Features

* **github:** 调整github监听命令 ([2ce9da4](https://github.com/MadokaProject/Madoka/commit/2ce9da4f8cf298af2b7a6b9919c2e4f6bc042c82))


### Bug Fixes

* **event:** 使用FunctionWaiter ([6015a52](https://github.com/MadokaProject/Madoka/commit/6015a52dd312f6e28f5286ec891458155130ca41))
* **plugin:** 更新插件的问题 ([8f9852e](https://github.com/MadokaProject/Madoka/commit/8f9852e9597e839f820123e5247fade0a087ded8))

## [3.0.0](https://github.com/MadokaProject/Madoka/compare/v2.4.1...v3.0.0) (2022-07-16)


### ⚠ BREAKING CHANGES

* **database:** 重构数据表初始化，支持自动更新数据表 #37
* **singleton:** 调整类单例模式实现
* **plugin:** 调整插件参数赋值的方式，改为按需获取
* **console:** 调整控制台处理
* **event:** 调整其它事件处理
* **plugin:** 全新插件管理器 #34

### Features

* **console:** 调整控制台处理 ([32d3635](https://github.com/MadokaProject/Madoka/commit/32d36358199160804bbcf0cae0fc014c19902fc8))
* **database:** 重构数据表初始化，支持自动更新数据表 [#37](https://github.com/MadokaProject/Madoka/issues/37) ([90ac51b](https://github.com/MadokaProject/Madoka/commit/90ac51b651d9de774a506b211b9fa45de90d58eb))
* **event:** 调整其它事件处理 ([dfb41ab](https://github.com/MadokaProject/Madoka/commit/dfb41aba98cc9a92d13b66dcc98ccd8c99cfdaf5))
* **plugin:** 全新插件管理器 [#34](https://github.com/MadokaProject/Madoka/issues/34) ([23c0a84](https://github.com/MadokaProject/Madoka/commit/23c0a849738e23ffdfb98b7537e7b8e7d9eae206))
* **plugin:** 新增插件更新检测功能 ([68bb584](https://github.com/MadokaProject/Madoka/commit/68bb584dce5afe0ce6560f34f8f9df8eb76407c5))
* **plugin:** 调整插件参数赋值的方式，改为按需获取 ([461603c](https://github.com/MadokaProject/Madoka/commit/461603c5077d68f7880f992cbc0e50d589c1b2be))
* **singleton:** 调整类单例模式实现 ([a7b9a7f](https://github.com/MadokaProject/Madoka/commit/a7b9a7f07c08e73ba7256cbb3bedbe932cf7fa38))


### Bug Fixes

* **alconna:** bug ([b6fd10e](https://github.com/MadokaProject/Madoka/commit/b6fd10e191a8935dcf7e4997fdbb2488dc143b9c))
* **controller:** 修复插件开关判断 ([0d47b9a](https://github.com/MadokaProject/Madoka/commit/0d47b9ad915fc36cc54b3723c26db4c0af1d6747))
* **game:** 优化金币排行输出 ([7e0280f](https://github.com/MadokaProject/Madoka/commit/7e0280fed54245643da87fa3379ad275a7231465))
* **plugin_mgr:** 更新插件未删除旧插件的问题 ([bcfcba6](https://github.com/MadokaProject/Madoka/commit/bcfcba6f1db728e645b42d8705c8788a0250695c))
* **plugin:** 修复加载、卸载插件的 bug ([68bb584](https://github.com/MadokaProject/Madoka/commit/68bb584dce5afe0ce6560f34f8f9df8eb76407c5))
* **plugin:** 修复本地插件信息文件可能的编码问题、修复部分插件未进行鉴权的 bug ([461603c](https://github.com/MadokaProject/Madoka/commit/461603c5077d68f7880f992cbc0e50d589c1b2be))
* **plugin:** 修改开关插件的命令 ([1f8def7](https://github.com/MadokaProject/Madoka/commit/1f8def79a33a88bb2237671729ad4b259f5f7d9e))
* **plugin:** 在3.9以上无法正常使用的问题 ([8b9fd8d](https://github.com/MadokaProject/Madoka/commit/8b9fd8d71b6833c5f6efeb4092c916e9f1464802))
* **plugin:** 控制请求频率 ([23c0a84](https://github.com/MadokaProject/Madoka/commit/23c0a849738e23ffdfb98b7537e7b8e7d9eae206))
* **plugin:** 插件加载无序的问题 ([1f8def7](https://github.com/MadokaProject/Madoka/commit/1f8def79a33a88bb2237671729ad4b259f5f7d9e))
* **plugin:** 调整插件管理器api ([dfb41ab](https://github.com/MadokaProject/Madoka/commit/dfb41aba98cc9a92d13b66dcc98ccd8c99cfdaf5))
* **schedule:** 调整一下 ([833d92f](https://github.com/MadokaProject/Madoka/commit/833d92f1d4c9a037e06d84f6a77791a1d41f861d))
* **trigger:** 无法发送消息 ([077944c](https://github.com/MadokaProject/Madoka/commit/077944c108907336f460961716033b94375604fa))

## [2.4.1](https://github.com/MadokaProject/Madoka/compare/v2.4.0...v2.4.1) (2022-06-23)


### Bug Fixes

* **controller:** 修复非超级管理员也能进入隐藏插件的bug ([bfb36ee](https://github.com/MadokaProject/Madoka/commit/bfb36ee4bad97862adce1997c3edcb6d7f1bc5ea))

## [2.4.0](https://github.com/MadokaProject/Madoka/compare/v2.3.0...v2.4.0) (2022-06-21)


### Features

* **game:** 新增每日收租 ([3932349](https://github.com/MadokaProject/Madoka/commit/3932349724b9658c22c84ba3c316272e067af9d1))
* **graia:** 升级ariadne->0.7.12, alconna->0.9.4 ([aa89ea5](https://github.com/MadokaProject/Madoka/commit/aa89ea54a99f706a4ab46717bff2d9aae683ab2f))


### Bug Fixes

* **check_version:** 调整版本更新检查执行时间 ([2ea41a5](https://github.com/MadokaProject/Madoka/commit/2ea41a5364934bc8288785beb29abf1cba813022))
* **plugins:** 修复重载、卸载插件后, 计划任务仍存在的bug ([3932349](https://github.com/MadokaProject/Madoka/commit/3932349724b9658c22c84ba3c316272e067af9d1))
* **sche:** 修改初始化方式 ([ccc38d5](https://github.com/MadokaProject/Madoka/commit/ccc38d5db83630e233e9e7c78881436dded891b6))
* **util.network:** 移除general_request旧接口 ([2ea41a5](https://github.com/MadokaProject/Madoka/commit/2ea41a5364934bc8288785beb29abf1cba813022))

## [2.3.0](https://github.com/MadokaProject/Madoka/compare/v2.2.0...v2.3.0) (2022-06-17)


### Features

* **app.plugins:** 支持不同版本下载对应版本的插件 ([9d282ae](https://github.com/MadokaProject/Madoka/commit/9d282ae6d2475a709437df42d6d74c1086b48cd6))
* **game:** 新增自动签到功能 ([0fa3c86](https://github.com/MadokaProject/Madoka/commit/0fa3c860125e28a050f8323fc25d420b42194ab7))


### Bug Fixes

* **app.plugins:** 重载插件提示错误 ([9d282ae](https://github.com/MadokaProject/Madoka/commit/9d282ae6d2475a709437df42d6d74c1086b48cd6))
* **game:** 调整自动签到收费 ([49166b6](https://github.com/MadokaProject/Madoka/commit/49166b606c0b60b846292fa71e5b50d145691688))

## [2.2.0](https://github.com/MadokaProject/Madoka/compare/2.1.0...v2.2.0) (2022-06-14)


### Features

* **plugins:** 重构插件定义方式，独立插件管理器，规范命名 ([400632e](https://github.com/MadokaProject/Madoka/commit/400632e83da07bfb3154c595c1d2016a1c2c6907))


### Bug Fixes

* **Config:** 保证为同一个对象 ([e79cd31](https://github.com/MadokaProject/Madoka/commit/e79cd31966cb60c146abe8723e9a2bbcb167167f))
* **controller:** dictionary changed size during iteration [#33](https://github.com/MadokaProject/Madoka/issues/33) ([c606f8d](https://github.com/MadokaProject/Madoka/commit/c606f8dc78d850eafb5eeb745dbdf7268812fa02))
* **core.app:** bug ([9b03aa6](https://github.com/MadokaProject/Madoka/commit/9b03aa68e7b925750d6f6aea76307670f3291dda))
* **madoka_manager:** list ([8a3046b](https://github.com/MadokaProject/Madoka/commit/8a3046b8e052f0b8ba2b444143f49d5c2bcd458f))
* **plugins:** loads extension plugin ([da2b097](https://github.com/MadokaProject/Madoka/commit/da2b09726e8cbf634bf737dc13182737783b0256))
* **plugins:** NotFoundPlugin [#32](https://github.com/MadokaProject/Madoka/issues/32) ([c6ded9c](https://github.com/MadokaProject/Madoka/commit/c6ded9cbcc845d1fb58f0a7e597cbbc44f46f93f))
