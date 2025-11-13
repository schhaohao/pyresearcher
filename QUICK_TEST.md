# 快速测试指南

## 前置准备

### 1. 安装依赖

```bash
cd researcher_demo
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入至少一个 API key：

```env
# 至少配置一个 API key
OPENAI_API_KEY=your_openai_api_key_here
# 或
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# 或
DEEPSEEK_API_KEY=your_deepseek_api_key_here
# 或
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
```

## 运行测试

### 方式 1: 测试所有提供商（推荐）

```bash
python tests/test_llm_standalone.py
```

这会：
- 检查所有 API key 配置
- 测试所有已配置的提供商
- 显示详细的测试结果和总结

### 方式 2: 测试单个提供商

```bash
# 测试 OpenAI
python tests/test_single_llm.py --provider openai

# 测试 Anthropic
python tests/test_single_llm.py --provider anthropic

# 测试 DeepSeek
python tests/test_single_llm.py --provider deepseek

# 测试 SiliconFlow
python tests/test_single_llm.py --provider siliconflow
```

### 方式 3: 自定义测试

```bash
# 指定模型
python tests/test_single_llm.py --provider openai --model gpt-3.5-turbo

# 自定义提示词
python tests/test_single_llm.py --provider openai --prompt "请用中文解释什么是深度学习"
```

## 预期输出

### 成功示例

```
============================================================
LLM 模型可用性测试
============================================================

检查 API key 配置...
  OPENAI: ✅ 已配置
  ANTHROPIC: ❌ 未配置
  DEEPSEEK: ❌ 未配置
  SILICONFLOW: ❌ 未配置

============================================================
测试 OPENAI...
============================================================
✅ API key 已配置
正在创建 LLM 实例...
✅ LLM 实例创建成功
   模型: gpt-4
   温度: 0.7
正在发送测试消息...
✅ 测试成功！

响应:
你好！我是一个AI助手，由OpenAI开发...

============================================================
测试总结
============================================================

总计: 4 个提供商
✅ 成功: 1
❌ 失败: 0
⏭️  跳过: 3

✅ 至少有一个提供商可用！
```

## 常见问题

### 1. ModuleNotFoundError

如果遇到 `ModuleNotFoundError`，请先安装依赖：

```bash
pip install -r requirements.txt
```

### 2. API key 未配置

确保 `.env` 文件存在且包含正确的 API key：

```bash
# 检查 .env 文件
cat .env

# 如果不存在，从示例复制
cp .env.example .env
```

### 3. API key 无效

- 检查 API key 是否正确
- 确认 API key 有足够的余额/权限
- 某些服务可能需要代理才能访问

## 下一步

测试通过后，你可以：

1. 在代码中使用 LLM：
   ```python
   from researcher.llm import LLMFactory
   llm = LLMFactory.create(provider="openai")
   ```

2. 查看使用示例：
   ```bash
   python examples/llm_usage.py
   ```

3. 开始使用多智能体系统：
   ```bash
   python examples/example_usage.py
   ```

