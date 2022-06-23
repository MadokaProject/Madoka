# Changelog

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
