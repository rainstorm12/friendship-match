import pandas as pd
import numpy as np
import re
import jieba

class Person:
    def __init__(self,student):
        #这里对应的是我们问卷中的一些数据
        self.index = student["编号"]
        self.name = student["1.姓名"]
        self.gender = student["2.性别"]
        self.birthday = student["出生年"]
        self.college = student["5.所在学院"]
        self.height = student["10.身高"]
        self.weight = student["11.体重"]
        self.mbti = student["12.mbti"].upper()
        self.character = student["14.用2-3个词语形容自己性格"]
        self.req_height = student["17.对对方的身高要求"]
        self.req_mbti = student["18.对对方的mbti要求"].upper()
        self.req_character = student["19.对对方的性格要求"]

class Girl(Person):
    def __init__(self, student):
        super().__init__(student)
        pass

class Boy(Person):
    def __init__(self, student):
        super().__init__(student)
        pass

class Friendship:
    def __init__(self, boy, girl):
        self.boy = boy
        self.girl = girl
    
    def age_score(self):
        dif_age = abs(self.girl.birthday-self.boy.birthday)
        if dif_age<=3:
            return 1
        else:
            return 1/dif_age

    def mbti_score(self,mbti,target_mbti):
        if "/" in target_mbti:
            req_mbti_list = target_mbti.split('/')
            if mbti in req_mbti_list:
                return 1
            else:
                return 0
        else:
            score = 0
            for i in range(0,4):
                c1 = target_mbti[i]
                c2 = mbti[i]
                if c1==c2 or c1 == 'X':
                    score+=1
            if score==4:
                return 1
            else:
                return 0
    def height_score(self,height,target_height):
        if type(target_height)==int:
            if target_height==0:
                low_height = 0
                high_height = 300
            else:
                low_height = target_height
                high_height = 300
        else:
            if '-' in target_height:
                req_height_list = target_height.split('-')
                low_height = int(req_height_list[0])
                high_height = int(req_height_list[1])
            elif target_height=='0':
                low_height = 0
                high_height = 300
            else:
                low_height = int(target_height)
                high_height = 300

        if height>=low_height and height<=high_height:
            return 1
        else:
            return 0
    def character_score(self,character,target_character):
        if target_character=='无':
            return 0.1
        pattern = '[\s,、，；。|]+'
        target_character = "|".join(jieba.cut(target_character, cut_all=False))
        character = "|".join(jieba.cut(character, cut_all=False))
        target_character_words = re.split(pattern, target_character)
        character_words = re.split(pattern, character)
        score = 0
        for tc in target_character_words:
            for c in character_words:
                if c in tc:
                    score+=0.1
        if score>=1:
            score = 1
        return score
    
    def get_character_score(self):
        self.boy_character_score = self.character_score(self.girl.character,self.boy.req_character)
        self.girl_character_score = self.character_score(self.boy.character,self.girl.req_character)
        return self.boy_character_score+self.girl_character_score
    
    def get_mbti_score(self):
        self.boy_mbti_score = self.mbti_score(self.girl.mbti,self.boy.req_mbti)
        self.girl_mbti_score = self.mbti_score(self.boy.mbti,self.girl.req_mbti)
        return self.boy_mbti_score+self.girl_mbti_score

    def get_height_score(self):
        self.boy_height_score = self.height_score(self.girl.height,self.boy.req_height)
        self.girl_height_score = self.height_score(self.boy.height,self.girl.req_height)
        return self.boy_height_score+self.girl_height_score
    
    def get_score(self):
        return self.get_height_score()*1000+self.age_score()*100+self.get_mbti_score()*10+self.get_character_score()

if __name__=='__main__':
    #数据路径
    file_path = './data/data_process.xlsx'#处理后的数据
    save_excel_path = './data/match.xlsx'#匹配结果数据
    
    #信息录入
    df = pd.read_excel(file_path)
    boy_map = {}
    girl_map = {}
    for _,item in df.iterrows():
        if item["2.性别"]=='A.男':
            b = Boy(item)
            boy_map[b.name] = b
        if item["2.性别"]=='B.女':
            g = Girl(item)
            girl_map[g.name] = g

    #匹配得分计算
    friend_map = {}
    for boy in boy_map.values():
        for girl in girl_map.values():
            f = Friendship(boy,girl)
            friend_map[(f.boy.name,f.girl.name)] = f.get_score()


    #得分排序
    threshold = 0#调整阈值过滤掉分数低的匹配结果
    sorted_friend_map = sorted(friend_map.items(), key=lambda item: item[1], reverse=True)
    sorted_friend_map = [item for item in sorted_friend_map if item[1]>=threshold]
    sorted_friend_map = sorted(sorted_friend_map, key=lambda x: x[0][0])

    #Kuhn-Munkras算法完成匹配
    import networkx as nx
    G = nx.Graph()
    edges_with_weights = []
    for friendship in sorted_friend_map:
        tuple_friend_score = (friendship[0][0],friendship[0][1],friendship[1])
        edges_with_weights.append(tuple_friend_score)

    for u, v, weight in edges_with_weights:
        G.add_edge(u, v, weight=weight)

    # 使用最大权重匹配算法
    matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True)

    #匹配结果导出
    concatenated_data = []
    is_match_list = []
    for friend in sorted_friend_map:
        boy_name = friend[0][0]
        girl_name = friend[0][1]
        boy = boy_map[boy_name]
        girl = girl_map[girl_name]
        score = friend[1]
        is_match=0
        if (boy_name,girl_name) in matching or (girl_name,boy_name) in matching:
            is_match = 1
            is_match_list.append(boy_name)
            is_match_list.append(girl_name)
        if is_match:
            concatenated_data.append([boy.name,boy.birthday,boy.height,boy.mbti,boy.character,boy.req_height,boy.req_mbti,boy.req_character,girl.name,girl.birthday,girl.height,girl.mbti,girl.character,girl.req_height,girl.req_mbti,girl.req_character,score])

    for girl in girl_map.values():
        girl_name =  girl.name
        if girl_name not in is_match_list:
            concatenated_data.append(['','','','','','','','',girl.name,girl.birthday,girl.height,girl.mbti,girl.character,girl.req_height,girl.req_mbti,girl.req_character,0])
    # triples_df = pd.DataFrame(concatenated_data, columns=['boy name','boy brithday','boy height','boy mbti','boy character','boy height req','boy mbti req','boy character req','girl name','girl brithday','girl height','girl mbti','girl character','girl height req','girl mbti req','gril character req','score'])
    triples_df = pd.DataFrame(concatenated_data, columns=['男生名字','男生生日','男生身高','男生mbti','男生性格','男生身高要求','男生mbti要求','男生性格要求','女生名字','女生生日','女生身高','女生mbti','女生性格','女生身高要求','女生mbti要求','女生性格要求','匹配分数'])
    triples_df.to_excel(save_excel_path, index=False, engine='openpyxl')