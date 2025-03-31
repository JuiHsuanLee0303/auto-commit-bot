# Auto Commit Bot 🤖

一个使用大型語言模型（LLM）自動生成 Git Commit 內容的 Python 工具包。它能分析你的 git diff 內容，並按照 Conventional Commits 格式生成結構化、有意義的提交內容。

## 功能特點 ✨

- 🔄 自動生成提交內容
- 🎯 支持多種 LLM 提供商（Hugging Face API 和本地模型）
- 📝 遵循 Conventional Commits 格式
- 🔍 支持預覽模式（dry-run）
- ⚙️ 可配置的设置

## 安装步驟 📦

### 1. 安装 PyTorch

首先，根據你的 CUDA 版本安装 PyTorch：

1. 訪問 https://pytorch.org
2. 選擇你的配置：
   - PyTorch Build：Stable（稳定版）
   - 你的操作系统
   - Package Manager：Pip
   - CUDA Version：（檢查你的 CUDA 版本或選擇僅 CPU）
3. 运行提供的命令，例如：

```bash
# Windows 系统，CUDA 11.8
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 僅 CPU 版本
pip3 install torch torchvision torchaudio
```

### 2. 安装 Auto Commit Bot

```bash
pip install auto-commit-bot
```

## 快速開始 🚀

1. 配置你的 LLM 提供商：

```bash
# 使用 Hugging Face API
auto-commit configure --provider api --api-key your-api-key --model gpt2

# 使用本地模型
auto-commit configure --provider local --model path/to/your/model
```

2. 暫存你的更改：

```bash
git add .  # 或暫存特定文件
```

3. 生成提交訊息並提交：

```bash
auto-commit commit
```

## 使用說明 📖

### 基本命令

```bash
# 生成提交訊息並提交已暫存的更改
auto-commit commit

# 預覽提交訊息而不實際提交（dry-run）
auto-commit commit --dry-run

# 暫存所有更改並提交
auto-commit commit --stage-all

# 為單次提交指定 LLM 提供商
auto-commit commit --provider api
```

### 配置設置

可以使用 `configure` 命令或創建 `.acbconfig` 文件來配置工具：

```bash
# 設置 LLM 提供商
auto-commit configure --provider api

# 設置 API 密鑰
auto-commit configure --api-key your-api-key

# 設置模型
auto-commit configure --model gpt2
```

`.acbconfig` 文件示例：

```yaml
provider_type: api
huggingface_api_key: your-api-key
model_name: gpt2
commit_format: conventional
```

## 自定義提示模板 📝

你可以通過創建文件並在配置中设置其路徑來自定義提示模板：

```bash
auto-commit configure --prompt-template path/to/template.txt
```

## 代碼示例 📝

### 1. 基本用法

```python
from auto_commit_bot.llm_utils import LLMProvider
from auto_commit_bot.git_utils import get_git_diff

# 初始化 LLM 提供商
llm = LLMProvider()

# 獲取 git diff
diff = get_git_diff(staged=True)

# 生成提交信息
message = llm.generate_commit_message(diff)
print(f"生成的提交信息: {message}")
```

### 2. 自定義配置

```python
from auto_commit_bot.config import Config

# 初始化配置
config = Config()

# 設置 Hugging Face API
config.set("provider_type", "api")
config.set("model_name", "gpt2")
config.set("huggingface_api_key", "your-api-key")
config.save()

# 使用本地模型
config.set("provider_type", "local")
config.set("model_name", "path/to/your/model")
config.save()
```

### 3. 自定義提示模板

```python
# 創建自定義提示模板
template = """
分析以下 git diff 並生成提交訊息。
重點關注主要更改，保持簡潔。

Git diff:
{diff}

按照以下格式生成提交訊息：
type(scope): description
"""

# 保存模板
with open("custom_template.txt", "w") as f:
    f.write(template)

# 配置使用自定義模板
config.set("prompt_template", "custom_template.txt")
config.save()
```

### 4. 命令行使用

```bash
# 暫存並使用默認設置提交
git add .
auto-commit commit

# 預覽提交訊息
auto-commit commit --dry-run

# 使用特定提供商
auto-commit commit --provider api

# 配置設置
auto-commit configure --provider api --model gpt2 --api-key your-api-key
```

## 開發指南 🛠

1. 克隆倉庫
2. 安装依賴：

```bash
poetry install
```

3. 運行測試：

```bash
poetry run pytest
```

## 貢獻指南 🤝

歡迎貢獻！請隨時提交 Pull Request。

## 許可證 📄

MIT 許可證
