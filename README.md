# friendship-match
一个大学生联谊活动的男女生匹配demo

![match](match.jpg)

## 匹配流程

### 1.数据读取

需要对原始数据进行清洗

### 2.计算男生-女生两两匹配得分

权重=1000×身高是否相互满足+100×年龄是否接近+10×mbti是否相互满足+性格是否相互满足

这里的性格是用jieba对语料进行分词然后实现粗略计算的

### 3.对得分进行排序：

调整阈值过滤掉分数低的匹配结果，以减少计算量

### 4.匹配：

根据匹配得分，保障整体的匹配情况尽可能更好，即让大家都满意的匹配结果，而不是顾此失彼

即比如一个人能和5个人匹配，而另一个人只能和2个人匹配，还有一个人只能和一个人匹配

那么需要让他们都满足匹配，或者说要保证整体的匹配结果更优

查了一下百度啊，这可能是种**多对多的关系匹配问题**

这里采用了networkx.algorithms.matching.max_weight_matching这个库实现的匹配（Kuhn-Munkras算法）

### 5.匹配结果导出：

导出到一个excel里，后续还可以根据情况具体调整



## 最后：

爱情不是公式的精确计算，参数一样的人也未必合适
