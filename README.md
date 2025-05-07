# IDX

#### 使用前提条件，nodejs项目hello world,打开项目脚本要能自动运行

#### 使用方法

1、先本地使用有头模式手动登录获得cookie文件，再使用cookie运行无头模式

2、变量设置

GOOGLE_PW：google账号格式： 账号 密码

APP_URL：app项目地址

3.建议至少配置:0.5cpu ，1G内存以上

建议使用GitHub的action，gitlab的ci或者vps运行脚本

# GitLab CI/CD 定时任务配置指南

在 GitLab 中，您需要在项目的 CI/CD 设置中手动创建两个定时任务，而不是像 GitHub Actions 那样直接在 YAML 文件中配置 cron 表达式。

## 步骤 1: 设置 CI/CD 变量

1. 进入您的 GitLab 项目
2. 转到 `设置` > `CI/CD` > `变量`
3. 添加以下变量:
   - `WEB_URL`: 您的网站 URL
   - `COOK_URL`: Cookie 下载链接
   - `GOOGLE_PW`: Google 密码
   - `APP_URL`: 应用 URL

## 步骤 2: 配置定时管道

1. 进入项目的 `CI/CD` > `定时任务`
2. 创建两个定时任务:

### 白天时段（对应 `*/5 0-16 * * *`）:
- **描述**: IDX-Keepalive 白天时段
- **间隔模式**: 自定义
- **Cron**: `*/5 0-16 * * *`
- **时区**: 选择您的时区
- **目标分支**: 您的主分支（例如 `main` 或 `master`）
- **变量**:
  - 键: `SCHEDULE_TYPE`
  - 值: `five_min_morning`

### 晚上时段（对应 `*/5 21-23 * * *`）:
- **描述**: IDX-Keepalive 晚上时段
- **间隔模式**: 自定义
- **Cron**: `*/5 21-23 * * *`
- **时区**: 选择您的时区
- **目标分支**: 您的主分支（例如 `main` 或 `master`）
- **变量**:
  - 键: `SCHEDULE_TYPE`
  - 值: `five_min_night`

## 注意事项

1. GitLab 的定时任务执行可能会有几分钟的延迟
2. 确保您已将 `main.py` 文件上传到您的 GitLab 仓库
3. 如果您的脚本需要其他依赖项，请创建 `requirements.txt` 文件
4. 检查 CI/CD 作业日志以确保一切正常运行
