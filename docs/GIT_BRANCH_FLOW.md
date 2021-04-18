开发流程如下：
![](https://7.dusays.com/2021/04/12/61ae478820cc9.png)

- master：master分支不能进行任何的本地merge，必须pull request进行合并，并保持与release同步
- release：release是预发布分支，每次发布后，将会提出pull request到master进行master的更新，而且所有的分支，都是基于release进行创建。
- dev：测试环境分支，进行合并测试的分支，测试分支不会与release进行合并，只有将release合并到dev进行更新，dev是一条不稳定的分支
- feature：每个新的特性都需要建立一条分支，命名规范如feature/迭代/姓名/功能名，feature/1.0/Colsrch/Group_management。
- bugfix：线上紧急bug，应该从master创建一条bugfix分支进行修复，然后合并到dev进行CR，并且通过测试后，pull request到master进行合并发布。

| 分支名 | 稳定性 | 源 | 合并方式 |
| :--- | :---: | :---: | --- |
| master | 稳定 | - |pull request |
| release | 稳定 | master |pull request |
| dev | 不稳定 | release |merge，pull request |
| feature | 不稳定 | release | merge，pull request |
| bugfix | 不稳定 | release | merge，pull request |

开发流程：

1. 开发时，应该按照规定创建feature分支（feature/迭代/姓名/功能名，feature/1.0/Colsrch/Group_management）
2. 本地开发并调试后，通过pull request合并到dev分支
3. 管理员CR通过合并到dev进行测试
4. 测试通过后，将会提交pull request到release分支等待发布
5. 管理员CR后合并提交的新特性到release中
6. 所有版本特性全部合并完成后打tag
7. 发布后将release同步到master中
8. 遇到紧急bug，通过master创建bugfix分支进行开发，完成bugfix后，应该提交到dev进行测试，并通过CR后，pull request到master，由管理员进行合并发布打tag，然后更新代码到release中。

> dev分支会一定时间内会清除重新在release中创建
> feature分支，在版本发布后，应该及时删除

### 注意

- 一切代码开发都应该在其功能对应目录进行开发，例如新插件（指令）的开发核心代码都应该在 app/plugin 目录完成。

### pull request流程

- 无论是pull request到dev还是releases，都需要更新一下releases到feature分支，再进行提交。
- pull request后，需要自己看看pull request后的代码是否存在冲突问题，不要提了就不管了。
- 从feature分支pull request到dev分支时需要注意以下问题:
    - 代码必须保证本地可以运行并通过自测
    - dev分支作为联合调试环境,不会将dev代码同步到releases,所以提交pull request时注意不要勾选合并后删除分支.
    - pull request后留意CR结果,CR不通过, 将会关闭pull request,根据整改意见整改后,再次提交pull request.
    - pull request中必须说清楚修改的内容,例如:
        - bugfix: 修改首页xxx情况下xxx问题
        - feat: 在xxx模块新增xxx特性
        - 如果pull request涉及多处修改,必须在pull request描述清楚每一个修改点的内容,CR也会检查pull request是否描述清楚问题.
- 通过dev进行测试没有问题后, 从feature分支pull request到releases分支.releases要求与dev分支规则一致,pull request与dev理论上应该一致,合并会采用扁平合并,将会合并本次pull
  request中的所有内容进行一次commit
    - 合并releases的pull request，一般情况下都需要在dev有提交记录
    - 如果没有特殊情况，可以选择合并后删除feature分支
    - releases分支将会作为上线前统一测试环境，当releases测试出现问题需要进行bugfix时，理论上需要重新合并dev重新走流程。
