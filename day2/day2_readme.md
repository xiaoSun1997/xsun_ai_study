# Python 虚拟环境与包管理

## 目录
1. [虚拟环境 (venv)](#虚拟环境-venv)
2. [包管理 (pip)](#包管理-pip)
3. [Requirements.txt](#requirementstxt)
4. [这些工具是否必要？](#这些工具是否必要)
5. [实践演示](#实践演示)

---

## 虚拟环境 (venv)

### 什么是虚拟环境？
虚拟环境是一个独立的 Python 环境，允许您：
- 为每个项目独立安装包
- 避免不同项目依赖之间的冲突
- 保持全局 Python 安装的清洁
- 确保在不同机器上的可复现性

### 为什么要使用虚拟环境？
**不使用 venv 时的问题：**

    项目 A 需要 Django 3.2
    项目 B 需要 Django 4.0
    全局 Python 只能安装一个版本！


**使用 venv 的解决方案：**
    
    项目 A → venv_A → Django 3.2
    项目 B → venv_B → Django 4.0
    两个项目独立工作！


### 如何创建和使用 venv

#### 创建虚拟环境
```bash
# 导航到项目目录
cd my_project

# 创建名为 'venv' 的虚拟环境
python -m venv venv

# 或指定自定义名称
python -m venv myenv
```
激活虚拟环境
Windows (PowerShell)：

    .\venv\Scripts\Activate.ps1
Windows (命令提示符)：

    .\venv\Scripts\activate.bat

Linux/Mac：

    source venv/bin/activate

停用虚拟环境

    deactivate

验证激活状态
激活后，您将在终端中看到环境名称：

    (venv) PS E:\code\my_project>

## 包管理 (pip)
### 什么是 pip？
    pip 是 Python 的包安装工具，允许您：
    
    从 PyPI (Python 包索引) 安装包
    
    卸载包
    
    列出已安装的包
    
    升级包

### 常用 pip 命令
#### 安装包

    # 安装单个包
    pip install requests

    # 安装特定版本
    pip install requests==2.28.0

    # 安装最低版本
    pip install requests>=2.28.0

    # 从 requirements.txt 安装
    pip install -r requirements.txt

#### 列出已安装的包
    # 列出所有已安装的包
    pip list

    # 显示特定包的详细信息
    pip show requests
#### 卸载包
    # 卸载包
    pip uninstall requests
    
    # 无确认卸载
    pip uninstall -y requests
#### 升级包
    # 升级特定包
    pip install --upgrade requests
    
    # 升级 pip 自身
    python -m pip install --upgrade pip

## Requirements.txt
### 什么是 requirements.txt？
    requirements.txt 文件是一个文本文件，列出了项目依赖的所有包及其版本。它能够：
    
    方便与团队成员共享依赖
    
    在不同机器上保持环境一致
    
    简化生产服务器的部署

### 创建 requirements.txt
方法 1：手动创建

    # requirements.txt
    requests==2.28.0
    numpy>=1.21.0
    pandas==1.5.3
    flask==2.3.0
方法 2：从当前环境自动生成

    # 生成包含精确版本的 requirements.txt
    pip freeze > requirements.txt

从 requirements.txt 安装

    # 安装 requirements.txt 中列出的所有包
    pip install -r requirements.txt

### 最佳实践
#### 生产环境固定版本：

    django==4.2.0
    requests==2.28.0

#### 开发环境使用版本范围：

    django>=4.2.0,<5.0.0
    requests>=2.28.0

#### 添加注释提高清晰度：

    # Web 框架
    django==4.2.0
    
    # HTTP 库
    requests==2.28.0
    
    # 数据处理
    pandas==1.5.3
    numpy>=1.21.0