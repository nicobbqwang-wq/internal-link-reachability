# 内链可达性检查器

不仅找“没有入链”的页面，也找“彼此有链接、但从指定入口走不到”的孤立页面组。离线 Python 工具读取页面全集、边清单和入口，输出可达性、最少跳数及入链来源，不抓站、不改站。

维护：**BBQ / BBQ Growth Lab** · [English](README.md) · [MIT](LICENSE)

## 谁能使用？怎样开始？

适合技术 SEO 和内容团队排查发现路径。需要 Python 3.9+，无第三方依赖。下载或克隆后，在仓库目录运行：

```sh
python3 reachability.py examples/graph.json
python3 -m unittest discover -s tests -v
```

六个 example.com 地址全部虚构。首页→Hub→指南形成三页可达路径；孤岛 A、B 互链但从首页不可达；最后一页没有入链。指南最短两跳，不可达页面跳数为 `null`，完整结果见 [示例报告](examples/report.json)。

复制 [输入模板](templates/graph.json)，替换示例 URL 并添加自己的清单：

```sh
python3 reachability.py my-graph.json > report.json
```

退出码 0 表示分析完成，不代表站点无问题；2 表示输入无效。程序仅本地读取 JSON 并输出报告。

## 输入字段

| 字段 | 约定 |
| --- | --- |
| `pages` | 非空数组，每项含绝对 `url` 和布尔值 `discoverable` |
| `entrypoints` | 非空入口 URL 数组，地址必须在 pages 中 |
| `links` | 边数组，每项含 source、target、kind、布尔值 crawlable |
| `kind` | navigation / breadcrumb / context / related / footer |

用 CMS、站点地图等建立页面全集，再接入链接导出；仅用可抓到的页面会漏掉真正需要检查的对象。所有边端点必须存在于清单；外链应先过滤，或明确扩充范围。URL 按原字符串匹配，不自动合并查询参数、大小写和尾斜杠。拒绝片段、凭据、空白和非 HTTP(S) 地址。

`discoverable` **仅控制报告分母**，不代表可索引、robots 状态或能否通行。false 页面仍可作为中间节点；不能通行的边应标记 `crawlable: false`。工具相信输入标签，但不自行验证它们。

## 如何读结果和处理？

每个选定页面包含：入口标记、是否可达、最少跳数、去重后的入链来源、正文来源、无入链候选。自链接不算有效入链；重复边不会夸大路径计数；入口因是人为指定起点而免于无入链标记。

有入链不代表从入口可达；不可达也不证明线上没有其他路径。先核对页面是否应独立存在，再检查采集范围及移动端最终链接，人工选择相关、稳定的入口。修改后使用同一范围重导出，并保留旧分母与报告。见 [复核工作单](templates/review.md)。

## 边界与来源

不检查 HTTP、重定向、canonical、动态渲染、nofollow、语义相关性或索引。跳数不是排名分数，也没有固定达标层数。正文来源标签不证明相关性和稳定性。可达不代表收录，SEO/GEO 效果未测。

来源：[BBQ Growth Lab 内链架构原文](https://bbqgrowthlab.com/zh-cn/articles/internal-linking-architecture-link-equity-guide/)，重点为页面全集、边类型与路径复核；2026-10-08 阅读。代码是其中一个窄范围检查实现，不复用原文业绩数值。[Google 链接指南](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) 用于核对可抓取链接定义，程序不检查网页标记。

由 Codex 辅助制作，仅使用合成数据测试，见 [验证](VALIDATION.md) 和 [贡献说明](CONTRIBUTING.md)。敏感 URL 与客户资料应保留在私有环境。MIT 覆盖原创文件，不覆盖外部资料。
