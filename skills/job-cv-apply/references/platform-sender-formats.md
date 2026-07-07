# 各平台发件人格式（2026-06-22验证）

> 此文件记录Gmail中各求职平台的发件人格式，用于子Agent脚本匹配。

| 平台 | 发件人名称 (name) | 发件人地址 (addr) | 邮件类型 |
|------|-------------------|-------------------|---------|
| LinkedIn | 领英, 领英职位订阅 | jobalerts-noreply@linkedin.com | 职位订阅/申请确认 |
| JobsDB | jobsdb | noreply@email.jobsdb.com | 岗位推荐 |
| JobsDB | jobsdb recommendations | noreply@e.jobsdb.com | 每日推荐 |
| Glassdoor | glassdoor jobs | noreply@glassdoor.com | 岗位推荐 |
| CTgoodjobs | ctgoodjobs.hk | no-reply@mail3.ctgoodjobsnews.hk | 资讯/岗位推荐 |
| CTgoodjobs | ctgoodjobs.hk | no-reply@ctgoodjobscs.hk | 资讯/岗位推荐 |
| Indeed | indeed | donotreply@match.indeed.com | 岗位推荐 |
| HSBC | HSBC Talent Acquisition Team | noreply@mail.apply.careers.hsbc.com | 申请反馈 |

## himalaya from 字段注意事项

`from` 字段是 dict 类型，不是 string：
```python
if isinstance(frm, dict):
    addr = (frm.get("addr", "") or "").lower()  # 注意 None 兜底
    name = (frm.get("name", "") or "").lower()
else:
    addr = str(frm).lower()
    name = ""
```

## CTgoodjobs 需过滤的非岗位内容

- 消委会、失业自白、政府工职位、父亲节、枕头、定存
- 政府工请人、政府部门请文书、面试攻略、个人档案
- 外賣、免費體驗、rtx、pandasale、yuu points

## 验证流程

修改脚本后必须手动验证：
```bash
rm ~/.hermes/job-search/gmail_state.json
python3 ~/.hermes/scripts/gmail_job_agent.py --days 7
# 对比各平台邮件数：LinkedIn ~22, JobsDB ~25, Glassdoor ~40, CTgoodjobs ~10, Indeed ~6
```
