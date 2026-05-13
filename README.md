# QtAutomationFramework

> 一个基于长链推理（Chain-of-Thought）与多智能体（Multi-Agent）协作的 Qt 桌面应用自动化测试框架，旨在解决传统 QTest 脚本在复杂 UI 及异步通信中的稳定性难题。

## 📌 核心痛点
传统 QTest 脚本在面对 Qt 复杂的信号槽（Signal/Slot）异步通信机制以及跨平台（Windows / Linux / macOS）UI 控件差异时，极易出现定位失效、脚本崩溃等问题，导致 CI 流水线的稳定性极差，维护成本高昂。

## ⚙️ 智能 Agent 核心逻辑
本框架通过四个独立的 AI 智能体协作，实现了从 UI 分析到回归验证的全链路自动化：

1. **规划 Agent**：自动解析 `.ui` / `.qml` 文件，深度构建 Qt 控件的依赖关系树与信号槽连接图（支持超 10 万+ Token 的上下文处理）。
2. **执行 Agent**：利用 Qt 元对象反射机制，动态生成基于 QTest 的 UI 操作脚本，兼容不同屏幕缩放与分辨率。
3. **长链推理（Chain-of-Thought）**：针对 Qt 的异步事件（如 QTimer、QEventLoop），通过一步步的逻辑推演，生成精确的等待与重试策略，避免竞态条件。
4. **审查 Agent**：自动运行生成的回归测试，并独立检查 `QObject` 父子关系，防止内存泄漏，同时校验跨平台的运行结果。

## 📊 落地效果
- **日均消耗 Token**：500万 - 1000万
- **自动化测试覆盖率**：从 30% 提升至 90%
- **CI 构建失败率**：降低 80%
- **跨平台兼容性**：单套脚本可无缝运行于 Windows/Linux/macOS

## 📂 目录结构
```text
QtAutomationFramework/
├── planner/           # 规划 Agent 核心逻辑
├── executor/          # 执行 Agent 源码
├── reviewer/          # 审查 Agent 源码  
