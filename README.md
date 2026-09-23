# 财富自由之路

面向约 10 人猎头团队的轻量 ATS/CRM V1。系统默认使用 PostgreSQL 保存业务数据，简历与附件通过独立存储接口保存到本地卷，后续可在不改业务代码的前提下接入 S3、MinIO 或云对象存储。

## 已包含

- 登录、管理员/经理/顾问角色与联系人字段脱敏
- 公司人才库、个人人才库、组合搜索、新增与编辑
- 手机号/邮箱自动查重
- PDF、DOCX 简历文本提取、字段初步识别与原件保留
- 客户与职位管理
- 独立于人才档案的职位 Pipeline：搜寻 → 联系 → 推荐 → 面试 → Offer → 入职 → 保证期 → 回款
- 候选人跟进备注与附件
- Docker Compose、PostgreSQL、持久化数据卷、健康检查
- 演示账号与演示业务数据
- 团队成员管理、密码重置、账号停用和审计日志
- 工作台统计、客户/职位页面与八阶段看板操作界面
- 数据库与附件成套备份、恢复脚本
- 简历流程：求职申请表、性格测试、面试邀请及候选人免登录填写
- 按客户配置发送主体、申请表表头、短信签名和面试要求
- 表单回收、后台查看、打印或另存为 PDF

## 短信链接

“简历流程”会自动生成候选人专属链接。未配置短信平台时为演示模式，可点击“复制短信链接”后自行发送。

接入腾讯云短信或其他短信服务时配置：

```env
PUBLIC_WEB_URL=https://你的系统域名
SMS_WEBHOOK_URL=https://你的短信发送网关地址
```

短信网关会收到 `phone`、`signature` 和 `content` 三个字段。正式发送前应配置 HTTPS 域名，并在短信服务商完成签名和模板审核。

## 本地启动（Mac / Windows）

1. 安装并启动 Docker Desktop。
2. 复制 `.env.example` 为 `.env`，建议修改其中两个密码。
3. 在本项目目录运行：

   ```bash
   docker compose up --build
   ```

4. 浏览器访问 `http://localhost:3000`。API 文档位于 `http://localhost:8000/docs`。

局域网其他电脑可访问 `http://本机局域网IP:3000`。首次启动会自动建表并生成演示数据。

## 账号与权限

首次升级后的管理员登录手机号为 `13800000000`，初始密码为 `123456`。请登录后立即在“个人资料”中修改手机号和6位数字密码。管理员可在“系统设置”中查看现有员工的登录手机号，并为每位员工创建独立账号。

管理员可以查看全部联系方式；普通顾问只可查看自己负责人才的完整联系方式，其他人的联系方式会脱敏。

## 常用管理操作

```bash
# 后台运行
docker compose up -d --build

# 查看运行状态
docker compose ps

# 停止（保留数据）
docker compose down

# 备份数据库
docker compose exec -T db pg_dump -U lingyao lingyao > lingyao-backup.sql
```

完整备份数据库与全部附件：

```bash
./scripts/backup.sh
```

备份文件保存在 `backups/`。恢复时传入同一时间生成的数据库和附件备份：

```bash
./scripts/restore.sh backups/lingyao-时间.dump backups/attachments-时间.tar.gz
```

不要使用 `docker compose down -v`，除非确定要删除数据库和全部简历附件。

## 正式使用前

1. 使用管理员账号登录，在系统设置中为每位员工创建独立账号。
2. 为管理员和员工账号设置各自的6位数字密码；不再使用的账号应停用。
3. 执行一次 `./scripts/backup.sh` 并将 `backups/` 复制到另一块磁盘或 NAS。
4. 局域网使用时，仅在可信内网开放 3000 和 8000 端口；公网访问必须配置 HTTPS 和防火墙。

## 云迁移

云上仍可直接使用本 Compose；生产环境建议将 PostgreSQL 切换到托管数据库，将 `LocalBlobStorage` 替换为实现同一接口的 S3/MinIO 存储，并在反向代理启用 HTTPS。业务 API 与数据模型无需重写。

## 数据接口

后端提供 `/api/auth`、`/api/candidates`、`/api/resumes`、`/api/clients`、`/api/jobs`、`/api/pipeline`、`/api/candidates/{id}/notes` 与附件下载接口。完整可交互说明可在服务启动后打开 `/docs` 查看。

## 测试

后端自动测试覆盖登录、搜索、查重、职位创建以及 Pipeline 阶段流转：

```bash
docker compose run --rm api pytest -q
```
