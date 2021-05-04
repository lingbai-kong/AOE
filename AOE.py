# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 21:58:03 2020

@author: 孔令百

Name:AOE.py

Desctiption:该模块中主要是AOE网络计算的底层算法
"""

"""
类:AOE类
功能:求解AOE网络
"""
class AOE:
    """
    函数：__init__(self,graph_head,graph_tail,circle_dict,line_dict)
    功能：AOE类的构造函数
    传入参数：AOE网络正向邻接表graph_head(字典),AOE网络逆邻接表graph_tail(字典),圆图形字典circle_dict(字典),连接线图形字典line_dict(字典)
    传出参数：无
    """
    def __init__(self,graph_head,graph_tail,circle_dict,line_dict):
        self.gh=graph_head#AOE网络邻接表
        self.gt=graph_tail#AOE网络逆邻接表
        self.circle_dict=circle_dict#圆图形字典
        self.line_dict=line_dict#连接线图形字典
        self.order=list(self.gh.keys())#顶点的拓扑排序序列
        self.critical_activity=[]#关键活动列表
        self.critical_affair=[]#关键事件列表
        self.Ve={}#事件Vi的最早可能开始时间,格式key=圆图形名称(字符串),value=时间(整数)
        self.Vl={}#事件Vi的最迟允许开始时间,格式key=圆图形名称(字符串),value=时间(整数)
        self.e={}#活动ai的最早可能开始时间,格式key=连接线图形名称(字符串),value=时间(整数)
        self.l={}#活动ai的最迟允许开始时间,格式key=连接线图形名称(字符串),value=时间(整数)
        self.route_list=[]#多种关键路径列表
        self.activity_group=[]#多种关键活动列表
        self.time=0
    """
    函数：function(self)
    功能：运行算法,求解Ve,Vl,e,l,critical_activity,critical_affair
    传入参数：无
    传出参数：关键活动self.critical_activity(列表),关键事件self.critical_affair(列表)
    """
    def function(self):
        #从Ve[0]=0开始
        self.Ve[self.order[0]]=0
        #以公式Ve[i]=max{Ve[j]+dur(<Vj,Vi>)}向前递推
        for i in range(1,len(self.order)):
            v=self.order[i]
            m=max(self.gt[v],key=lambda x:self.Ve[x[0]]+x[1])
            self.Ve[v]=self.Ve[m[0]]+m[1]
        #从Vl[n-1]=Ve[n-1]开始
        self.Vl[self.order[-1]]=self.Ve[self.order[-1]]
        #全工程可以完成的最早时间就是Vl[n-1]
        self.time=self.Ve[self.order[-1]]
        #以公式Vl[i]=min{Vl[j]-dur(<Vi,Vj>)}反向递推
        for i in range(len(self.order)-2,-1,-1):
            v=self.order[i]
            m=min(self.gh[v],key=lambda x:self.Vl[x[0]]-x[1])
            self.Vl[v]=self.Vl[m[0]]-m[1]
        
        #以Ve[k]=Vl[k]为判断条件寻找关键事件
        for v in self.order:
            if self.Ve[v]==self.Vl[v]:
                self.critical_affair.append(v)
        #计算e[k]和l[k]        
        #e[k]=Ve[i]
        #l[k]=Vl[j]-dur(<Vi,Vj>)
        for line,value in self.line_dict.items():
            self.e[line]=self.Ve[value[1]]
            self.l[line]=self.Vl[value[2]]-value[0]
        #以e[k]=l[k]为判断条件寻找关键活动
        for line in self.line_dict:
            if self.e[line]==self.l[line]:
                self.critical_activity.append(line)        
        return self.critical_activity,self.critical_affair
    """
    函数：_route(self,cur,route)
    功能：寻找全部的关键路径
    传入参数：当前事件顶点cur(字符串),当前路径route(字符串)
    传出参数：无
    """
    def _route(self,cur,route):
        #拷贝当前路径
        new_route=route
        #将当前事件加入到当前路径中
        if new_route=="":
            new_route=self.circle_dict[cur][0]
        else:
            new_route+='→'+self.circle_dict[cur][0]
        #如果当前事件是AOE网络的汇点
        if cur==self.order[-1]:
            #加入当前路径到关键路径
            self.route_list.append(new_route)
        #检查当前事件的下一个关键事件
        for out in self.circle_dict[cur][3]:
            if out in self.critical_activity:
                #递归地调用此函数
                new=self.line_dict[out][2]
                self._route(new,new_route)
    """
    函数：critical(self)
    功能：计算每一条关键路径和每一组关键活动
    传入参数：无
    传出参数：全部关键路径self.route_list(列表),各组关键事件self.activity_group(列表)
    """
    def critical(self):
        #从源点开始递归计算关键路径
        self._route(self.order[0],"")
        #将每一条关键路径中的关键事件分离出来,组成一组加入到关键事件列表中
        for route in self.route_list:
            step=route.split('→')
            activity=""
            if len(step)>=2:
                activity='<'+step[0]+','+step[1]+'>'
                for i in range(1,len(step)-1):
                    activity+=',<'+step[i]+','+step[i+1]+'>'
            self.activity_group.append(activity)
        return self.route_list,self.activity_group
"""
该模块的测试代码
"""
if __name__=="__main__":
    gh={'c0': [('c1', 5), ('c2', 6)], 'c1': [('c3', 3)], 'c2': [('c3', 6), ('c4', 3)], 'c3': [('c4', 3), ('c6', 4), ('c5', 4)], 'c4': [('c6', 1), ('c7', 4)], 'c5': [('c9', 4)], 'c6': [('c8', 5)], 'c7': [('c8', 2)], 'c8': [('c9', 2)], 'c9': []}
    gt={'c0': [], 'c1': [('c0', 5)], 'c2': [('c0', 6)], 'c3': [('c1', 3), ('c2', 6)], 'c4': [('c3', 3), ('c2', 3)], 'c5': [('c3', 4)], 'c6': [('c4', 1), ('c3', 4)], 'c7': [('c4', 4)], 'c8': [('c6', 5), ('c7', 2)], 'c9': [('c5', 4), ('c8', 2)]}
    c={'c0': ['1', (103, 146), [], ['l0', 'l2']], 'c1': ['2', (218, 62), ['l0'], ['l1']], 'c2': ['3', (223, 244), ['l2'], ['l3', 'l5']], 'c3': ['4', (357, 62), ['l1', 'l3'], ['l4', 'l7', 'l8']], 'c4': ['5', (358, 242), ['l4', 'l5'], ['l6', 'l12']], 'c5': ['6', (545, 67), ['l8'], ['l9']], 'c6': ['7', (478, 146), ['l6', 'l7'], ['l10']], 'c7': ['8', (581, 258), ['l12'], ['l13']], 'c8': ['9', (670, 159), ['l10', 'l13'], ['l11']], 'c9': ['10', (848, 147), ['l9', 'l11'], []]}
    l={'l0': [5, 'c0', 'c1'], 'l1': [3, 'c1', 'c3'], 'l2': [6, 'c0', 'c2'], 'l3': [6, 'c2', 'c3'], 'l4': [3, 'c3', 'c4'], 'l5': [3, 'c2', 'c4'], 'l6': [1, 'c4', 'c6'], 'l7': [4, 'c3', 'c6'], 'l8': [4, 'c3', 'c5'], 'l9': [4, 'c5', 'c9'], 'l10': [5, 'c6', 'c8'], 'l11': [2, 'c8', 'c9'], 'l12': [4, 'c4', 'c7'], 'l13': [2, 'c7', 'c8']}
    aoe=AOE(gh,gt,c,l)
    critical_activity,critical_affair=aoe.function()
    routes,activity=aoe.critical()
    print(critical_activity)
    print(critical_affair)
    print(routes)
    print(activity)