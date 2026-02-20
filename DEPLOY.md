# 部署到 GitHub Pages

按顺序在**终端**里执行下面步骤即可。

## 第一步：在 GitHub 上新建仓库

1. 打开 **https://github.com/new**
2. **Repository name** 填：`guangdong-university-recruitment`（或你喜欢的英文名）
3. 选择 **Public**
4. **不要**勾选 "Add a README file"、"Add .gitignore" 等
5. 点击 **Create repository**
6. 记下仓库地址，例如：`https://github.com/你的用户名/guangdong-university-recruitment.git`

## 第二步：在本地执行 Git 命令

在终端中依次执行（把 `你的用户名` 和 `guangdong-university-recruitment` 换成你实际的 GitHub 用户名和仓库名）：

```bash
cd /Users/bytedance/.cursor/projects/System-Applications-Notes-app/GuangdongUniversityRecruitment

git init
git add .
git commit -m "Initial commit: 广东省高校教师岗行政岗招聘信息"
git branch -M main
git remote add origin https://github.com/你的用户名/guangdong-university-recruitment.git
git push -u origin main
```

若提示需要登录，按提示在浏览器中完成 GitHub 认证即可。

## 第三步：开启 GitHub Pages

1. 打开该仓库的 GitHub 页面
2. 点击 **Settings** → 左侧 **Pages**
3. 在 **Build and deployment** 里：
   - **Source** 选 **Deploy from a branch**
   - **Branch** 选 `main`，**Folder** 选 **/ (root)**
   - 点击 **Save**
4. 等待 1～2 分钟，刷新 Pages 设置页，会显示：
   **Your site is live at https://你的用户名.github.io/guangdong-university-recruitment/**

把这个链接发给任何人，即可直接打开招聘信息页面。

## 之后更新内容

修改了页面或 `data/` 里的数据后，在项目目录执行：

```bash
git add .
git commit -m "更新招聘数据"
git push
```

GitHub Pages 会自动重新部署，几分钟后刷新网站即可看到更新。
