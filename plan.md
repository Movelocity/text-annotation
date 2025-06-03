我要做一个文本标注项目，先实现后端的部分。
使用 sqlite 管理数据
- 标注数据管理：text as string(no duplicate), labels as string (seperated by comma)
- 标签管理：id as number, label as string

数据来源：
现有旧数据导入：old-data/**/<label>.txt, each line is a record for the label, there will be some common records exist in multiple label files, merge them and get labels seperate by comma
新数据导入：无标注文本，按行分隔