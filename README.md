# QDII ETF Dashboard（本地原型）

这是一个不连接 Wind、不调用 WindPy 的本地 Streamlit 原型。它只读取已保存的 Excel 数值；未来可由另一台电脑上的 Wind Excel 刷新并保存，再上传至本网站。

## 运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

浏览器打开终端显示的本地地址。默认使用 `data/mock_qdii_data.xlsx`；在首页侧栏上传 Excel 后，当前会话所有页面自动使用上传文件。点击“切回内置 mock Excel”可恢复示例数据。

## Excel 交换 Schema

工作簿必须有下列三个 Sheet，字段名必须完全一致，首行为字段名。Python 仅读取公式最后保存的结果值，不会计算或调用任何 Wind 公式。

### `ETF_Current`

`date, code, name, category, close, nav, fund_scale, amount, pct_change, purchase_status`

- 每行是一只 ETF 的最新快照。
- `category` 使用 `纳指`、`标普` 或 `特色`。
- `fund_scale`、`amount` 在本原型统一使用“亿元”；真实 Wind Excel 请在导出前完成单位统一。
- `pct_change` 使用小数（如 1.2% 写为 `0.012`）。

### `ETF_History`

`date, code, close, nav, premium`

- 每行是一只 ETF 的一个日频观察值，建议至少保留近 252 个交易日。
- 页面始终优先按 `close / nav - 1` 重算 `premium`；本列保留用于审计和兼容。

### `Global_Index`

`date, code, name, close, pct_change, pe_ttm`

- 每行是一只指数的一个日频观察值；首页仅展示每个代码的最新日期记录。
- 首批代码：`NDX.GI, SPX.GI, N225.GI, SOX.GI, DAX.GI, CAC.GI, KS11.GI`。

## 等真实 Wind Excel 后验证

- ETF 的 `fund_scale`、`amount` 单位与时间点；
- `purchase_status` 对场内 ETF 的准确业务含义；
- 七大指数的 `pe_ttm` 可用性、口径和缺失值处理；
- NAV 与市价在跨时区下的日期对齐。

任何缺 Sheet、缺字段、数据为空、日期无法解析或关键数值列全为空的工作簿，页面会显示明确提示而不会直接崩溃。
