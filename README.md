# 广东省高校教师岗·行政岗招聘信息

收集并展示广东省内本科、专科院校的**教师岗**与**行政岗**招聘信息，支持按岗位类型、城市、院校类型筛选，并可持续更新。

## 项目结构

```
GuangdongUniversityRecruitment/
├── index.html          # 展示页（招聘列表 + 各校入口）
├── update_jobs.py      # 更新脚本：抓取各校人事处页面并提取招聘链接
├── requirements.txt   # Python 依赖
├── data/
│   ├── universities_guangdong.json  # 院校名单与招聘页 URL
│   └── jobs.json                    # 抓取到的招聘信息（由脚本更新）
└── README.md
```

## 使用方式

### 1. 查看页面

- 用**本地 HTTP 服务**打开（推荐），否则浏览器可能禁止加载本地 `data/*.json`：
  ```bash
  cd GuangdongUniversityRecruitment
  python3 -m http.server 8080
  ```
  本机浏览器访问：<http://localhost:8080>

**让其他人或手机能打开（同一 WiFi 下）：**

- `localhost` 只表示「本机」，别人访问 `localhost:8080` 会连到他们自己的电脑/手机，所以会显示「无法访问」。
- 需要让服务器监听所有网卡，并**把地址改成你电脑的局域网 IP**：
  ```bash
  cd GuangdongUniversityRecruitment
  python3 -m http.server 8080 --bind 0.0.0.0
  ```
  终端里会显示本机 IP（如 `192.168.1.105`），**把下面这个地址发给别人**（同一 WiFi 下）：  
  **http://你的电脑IP:8080**  
  例如：`http://192.168.1.105:8080`
- 或直接双击运行项目里的 **`start_server.command`**（Mac）；首次若无法运行，在终端执行：`chmod +x start_server.command`。

**想让任何人通过网址打开（不限于同一 WiFi）：**  
见下方 [部署到 GitHub Pages](#部署到-github-pages)。

- 页面功能：
  - **招聘信息列表**：展示 `data/jobs.json` 中抓取到的每条招聘/公告链接，可筛选「教师岗 / 行政岗 / 全部」、城市、本科/专科。
  - **按学校入口**：列出所有院校的人事处/招聘页链接，方便直接点进学校官网查看最新公告。

### 2. 更新招聘信息（随时更新）

安装依赖后运行更新脚本，会遍历 `universities_guangdong.json` 中的招聘页，抓取页面中的链接并识别与教师、行政招聘相关条目，写回 `data/jobs.json`。

```bash
cd GuangdongUniversityRecruitment
pip install -r requirements.txt
python3 update_jobs.py
```

- 脚本会按院校逐个请求人事处 URL，并做简单间隔，避免请求过快。
- 若某校网站结构特殊或改版，抓取结果可能不全，可结合「按学校入口」手动打开该校官网查看。

### 3. 定期自动更新（可选）

- **macOS / Linux**：用 crontab 每天跑一次，例如每天 8:00：
  ```bash
  0 8 * * * cd /path/to/GuangdongUniversityRecruitment && python3 update_jobs.py
  ```
- **Windows**：可用任务计划程序，每日执行 `python update_jobs.py`（工作目录设为项目目录）。

## 维护院校名单与链接

- 编辑 `data/universities_guangdong.json`：
  - `name`：学校名称  
  - `city`：城市  
  - `type`：本科 / 专科  
  - `recruitment_url`：该校人事处或招聘公告列表页的 URL（必填才会被脚本抓取）  
  - `recruitment_name`：链接显示名称（如「人事处」「人才招聘」）

新增学校或修正链接后，重新运行 `python3 update_jobs.py` 即可更新数据。

## 部署到 GitHub Pages

按下面步骤即可把页面部署到 GitHub，获得一个公网地址（如 `https://你的用户名.github.io/guangdong-university-recruitment`），任何人打开该链接即可查看。

1. **在 GitHub 上新建仓库**
   - 打开 [https://github.com/new](https://github.com/new)
   - Repository name 填：`guangdong-university-recruitment`（或任意英文名）
   - 选择 **Public**，**不要**勾选 "Add a README file"
   - 点 **Create repository**

2. **在本地项目目录执行（已初始化过可跳过前两行）**
   ```bash
   cd /Users/bytedance/.cursor/projects/System-Applications-Notes-app/GuangdongUniversityRecruitment
   git init
   git add .
   git commit -m "Initial commit: 广东省高校教师岗行政岗招聘信息"
   git branch -M main
   git remote add origin https://github.com/你的用户名/guangdong-university-recruitment.git
   git push -u origin main
   ```
   把 `你的用户名` 和 `guangdong-university-recruitment` 换成你的 GitHub 用户名和仓库名。若提示登录，按提示在浏览器完成认证。

3. **开启 GitHub Pages**
   - 打开该仓库页面 → **Settings** → 左侧 **Pages**
   - 在 **Source** 里选 **Deploy from a branch**
   - **Branch** 选 `main`，文件夹选 **/ (root)**，点 **Save**
   - 等一两分钟，页面上方会显示：`Your site is live at https://你的用户名.github.io/guangdong-university-recruitment/`

之后若修改了代码或数据，执行 `git add .` → `git commit -m "更新"` → `git push`，Pages 会自动更新。

## 说明

- 各校官网结构不一，脚本仅做通用链接提取与关键词匹配（教师/行政/招聘等），**不保证 100% 覆盖**，重要岗位建议以各校官网为准。
- 页面为纯前端 + 本地 JSON，无需后端服务器；部署到任意静态空间时，需保证 `data/jobs.json` 与 `data/universities_guangdong.json` 可被同一域名下的页面访问（或自行改为 API 拉取）。

## 许可证

仅供个人学习与信息汇总使用，请遵守各校官网使用条款与 robots 协议。
