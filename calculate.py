# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 16:42:08 2020

@author: 孔令百

Name:calculate.py

Desctiption:该模块中包含拓扑排序,读写文件,将绘图数据转化为邻接表形式的数据结构
"""
from copy import deepcopy
import pickle
"""
函数：topologySort(circle_dict,line_dict)
功能：拓扑排序算法
传入参数：圆图形字典circle_dict(字典),连接线图形字典line_dict(字典)
传出参数：AOE网络合法标志Flag(布尔),拓扑排序表order(列表)
"""
def topologySort(circle_dict,line_dict):
    c=deepcopy(circle_dict)#拷贝圆图形字典
    l=deepcopy(line_dict)#拷贝连接线图形字典
    order=[]#拓扑排序表
    start_count=0#源点计数
    end_count=0#汇点计数
    #计算源点汇点数目
    for v,value in c.items():
        if len(value[2])==0:
            start_count+=1
        if len(value[3])==0:
            end_count+=1
    #源点/汇点数目不唯一说明AOE网络不合法
    if start_count!=1 or end_count!=1:
        return False,order
    while len(c)>0:
        start=''#图中入度为0的点
        for circle,value in c.items():
            if len(value[2])==0:
                start=circle
                break
        #剩下的点入度均不为0,说明图中有环,AOE网络非法
        if start=='':  
            return False,order
        #将入度为0的点加入列表
        order.append(start)
        #在图中删除该点及其所有的弧
        for line in c[start][3]:
            value=l[line]
            tail=value[2]
            c[tail][2].remove(line)
            l.pop(line)
        c.pop(start)
    return True,order
"""
函数：transform(circle_dict,line_dict,order)
功能：将窗口绘图数据转化为邻接表形式的数据结构
传入参数：圆图形字典circle_dict(字典),连接线图形字典line_dict(字典),拓扑排序表order(列表)
传出参数：AOE网络邻接表graph_head(字符串),AOE网络逆邻接表graph_tail(字符串)
"""       
def transform(circle_dict,line_dict,order):
    graph_head={}#AOE网络邻接表graph_head(字符串),格式:key=顶点名(字符串),value=[(后继顶点名(字符串),到后继节点的弧权值(整数))(元组),......](列表)
    graph_tail={}#AOE网络逆邻接表graph_tail(字符串)
    
    #初始化邻接表
    for v in order:
        graph_head[v]=[]
        graph_tail[v]=[]
    #构建邻接表
    for v in order:
        for line in circle_dict[v][3]:
            value=line_dict[line]
            graph_head[v].append((value[2],value[0]))
        for line in circle_dict[v][2]:
            value=line_dict[line]
            graph_tail[v].append((value[1],value[0]))       
    return graph_head,graph_tail
"""
函数：read(filename)
功能：读取文件内容
传入参数：文件路径及文件名filename(字符串)
传出参数：读文件成功标志,AOE文件内容:圆图形字典circle_dict(字典),连接线图形字典line_dict(字典)
""" 
def read(filename):
    try:
        f=open(filename,'rb')
        tup=pickle.load(f)
        circle_dict=tup[0]
        line_dict=tup[1]
        return True,circle_dict,line_dict
    except IOError as e:
        print("error:caculate.read(filename)",e)
        return False,{},{}
"""
函数：write(filename,circle_dict,line_dict)
功能：将AOE网络图形写入文件
传入参数：文件路径及文件名filename(字符串),圆图形字典circle_dict(字典),连接线图形字典line_dict(字典)
传出参数：写文件成功标志
""" 
def write(filename,circle_dict,line_dict):
    try:
        f=open(filename,'wb')
        tup=(circle_dict,line_dict)
        pickle.dump(tup,f)
        f.close()
        return True
    except IOError as e:
        print("error:caculate.write(filename,circle_dict,line_dict)",e)
        return False
"""
该模块的测试代码
"""
if __name__=="__main__":
    c={'c0': ['1', (103, 146), [], ['l0', 'l2']], 'c1': ['2', (218, 62), ['l0'], ['l1']], 'c2': ['3', (223, 244), ['l2'], ['l3', 'l5']], 'c3': ['4', (357, 62), ['l1', 'l3'], ['l4', 'l7', 'l8']], 'c4': ['5', (358, 242), ['l4', 'l5'], ['l6', 'l12']], 'c5': ['6', (545, 67), ['l8'], ['l9']], 'c6': ['7', (478, 146), ['l6', 'l7'], ['l10']], 'c7': ['8', (581, 258), ['l12'], ['l13']], 'c8': ['9', (670, 159), ['l10', 'l13'], ['l11']], 'c9': ['10', (848, 147), ['l9', 'l11'], []]}
    l={'l0': [5, 'c0', 'c1'], 'l1': [3, 'c1', 'c3'], 'l2': [6, 'c0', 'c2'], 'l3': [6, 'c2', 'c3'], 'l4': [3, 'c3', 'c4'], 'l5': [3, 'c2', 'c4'], 'l6': [1, 'c4', 'c6'], 'l7': [4, 'c3', 'c6'], 'l8': [4, 'c3', 'c5'], 'l9': [4, 'c5', 'c9'], 'l10': [5, 'c6', 'c8'], 'l11': [2, 'c8', 'c9'], 'l12': [4, 'c4', 'c7'], 'l13': [2, 'c7', 'c8']}

    ok,order=topologySort(c, l)
    if ok:
        print(order)
        graph_head,graph_tail=transform(c, l, order)
        print(graph_head)
        print('------------------------------')
        print(graph_tail)
        for i,value in graph_head.items():
            print(i,':',value)
        print('------------------------------')
        for i,value in graph_tail.items():
            print(i,':',value)
    else:
        print("error")