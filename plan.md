我要做一个文本标注项目，先实现后端的部分。
使用 sqlite 管理数据
- 标注数据管理：text as string(无重复), labels as string (用逗号分隔)
- 标签管理：id as number, label as string

数据来源：
现有旧数据导入：old-data/**/<label>.txt, 每行是该标签的一个记录，会有一些相同记录存在于多个标签文件中，合并它们并获取用逗号分隔的标签
新数据导入：无标注文本，按行分隔