# GPTCGPruner
基于GPT的CodeQL误报去除器，主要进行了过程内和过程间的分析。对于过程内分析，利用GPT再次验证污点是否能传播。对于过程间则利用GPT分析这个调用边是否为误报。本项目Idea主要来源于此篇论文：
- [Striking a balance: pruning false-positives from static call graphs](https://dl.acm.org/doi/abs/10.1145/3510003.3510166)

## 功能
- 调用CodeQL分析项目
- 基于GPT对结果去误报，并输出误报分析（主要是两两片段的分析）

## 使用
- 在config.py中配置数据库路径、ql路径、输出文件路径以及GPT key（穷苦党用的是[GPT_API_free](https://github.com/chatanywhere/GPT_API_free)）

## TODO
- 更好的prompt策略（Few-Shot，ICL，COT......）
- 解析更多静态信息，如类型结构系统等