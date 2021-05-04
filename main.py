# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 17:58:50 2020

@author: 孔令百

Name:main.py

Desctiption:该模块实现了UI界面相关功能,绘图操作的实现和前后端的对接
"""
import sys
import xlwt
from PyQt5.QtWidgets import QApplication,QMainWindow,QAction,QMessageBox,QWidget,QTableWidgetItem,QFileDialog,QInputDialog,QLineEdit,QStatusBar
from PyQt5.QtGui import QPainter,QBrush,QPen,QColor,QIcon,QPixmap
from PyQt5.QtCore import QPoint,QLineF,QRect,Qt
from PyQt5.uic import loadUi
from calculate import topologySort,transform,read,write
from AOE import AOE
"""
函数：distance(A,B,C)
功能：计算点C到直线AB的距离
传入参数：直线端点：A(元组)，B(元组),点C(元组)
传出参数：距离(整数)
""" 
def distance(A,B,C):
    v_AB=(B[0]-A[0],B[1]-A[1])
    v_AC=(C[0]-A[0],C[1]-A[1])
    cos=(v_AB[0]*v_AC[0]+v_AB[1]*v_AC[1])/(((v_AB[0]**2+v_AB[1]**2)**0.5)*((v_AC[0]**2+v_AC[1]**2)**0.5))
    sin=(1-cos**2)**0.5
    return sin*(v_AC[0]**2+v_AC[1]**2)**0.5
"""
函数：dot_products(A,B,C)
功能：计算向量数量积AB*AC
传入参数：点：A(元组)，B(元组),C(元组)
传出参数：数量积结果(整数)
""" 
def dot_products(A,B,C):#AB*AC
    AB=(B[0]-A[0],B[1]-A[1])
    AC=(C[0]-A[0],C[1]-A[1])
    return AB[0]*AC[0]+AB[1]*AC[1]
"""
类:绘图窗口
功能:在控件中实现绘制AOE网络的功能
"""
class PaintWindow(QWidget):
    """
    函数：__init__(self,parent)
    功能：绘图窗口构造函数,初始化相关参数
    传入参数：上级对象parent
    传出参数：无
    """
    def __init__(self,parent):
        super().__init__()#父类Widget初始化
        self.parent=parent#上级对象
        self.status="Move"#绘图行为,初始为移动操作
        self.x=1920#绘图区宽度
        self.y=1080#绘图区高度
        self.setMinimumSize(self.x, self.y)#设定绘图区大小
        self.isget=False#选中图形标志,初始为假
        self.circle_dict={}#圆图形字典circle_dict(字典),格式:key=圆名字(字符串),value=[事件名name(字符串),圆坐标(横坐标,纵坐标)(元组),入弧[弧名(字符串)](列表),出弧[弧名(字符串)](列表)](列表)
        self.circle_count=0#圆图形计数,绘制一次圆计数增1
        self.circle_gotton=""#选取的圆图形
        self.d=50#圆图形直径
        self.line_dict={}#连接线图形字典line_dict,格式:key=连接线名字(字符串),value=[权值(整数),出发圆名字(字符串),终点圆名字(字符串)]
        self.line_count=0#连接线线图形计数,绘制一次连接线计数增1
        self.line_gotton=""#选取的连接线
        self.line_dest_pos=()#当前连接线重点坐标(鼠标指针位置)
        self.line_width=5#连接线可选区域宽度(非连接线宽度)
        
        self.critical_activity=[]#关键活动
        self.critical_affair=[]#关键事件
        self.isnew=True#当前图形是否是新绘制的(如果生成关键路径后更改AOE网络,则将新的AOE网络视为新绘制的)
    """
    函数：paintEvent(self,event)
    功能：绘图事件函数
    传入参数：event
    传出参数：无
    """ 
    def paintEvent(self,event):
        qp=QPainter(self)
        qp.begin(self)
        self.draw(qp)
        qp.end()
    """
    函数：draw(self,qp)
    功能：绘制AOE网络
    传入参数：绘图对象qp(QPainter)
    传出参数：无
    """ 
    def draw(self,qp):
        brush=QBrush()#刷子对象
        pen=QPen()#画笔对象
        lightgray=QColor()#自定义颜色
        lightgray.setRgb(240,240,240)
        #绘制各个连接线
        for line,value in self.line_dict.items():
            if value[2]=='':#连接线终点未指定时,绘制一条虚线,终点跟随鼠标
                pen.setStyle(Qt.DashLine)
                pen.setColor(Qt.black)
                qp.setPen(pen)
                lineF=QLineF(QPoint(self.circle_dict[value[1]][1][0],self.circle_dict[value[1]][1][1]),QPoint(self.line_dest_pos[0],self.line_dest_pos[1]))
                e=lineF.unitVector()
                new_lineF=QLineF(QPoint(self.circle_dict[value[1]][1][0]+int(e.dx()*self.d/2),self.circle_dict[value[1]][1][1]+int(e.dy()*self.d/2)),QPoint(self.line_dest_pos[0],self.line_dest_pos[1]))
                qp.drawLine(new_lineF)
            #连接线两端的圆形是相离状态时,绘制有向箭头
            elif ((self.circle_dict[value[1]][1][0]-self.circle_dict[value[2]][1][0])**2+(self.circle_dict[value[1]][1][1]-self.circle_dict[value[2]][1][1])**2)**0.5>self.d:
                lineF=QLineF(QPoint(self.circle_dict[value[1]][1][0],self.circle_dict[value[1]][1][1]),QPoint(self.circle_dict[value[2]][1][0],self.circle_dict[value[2]][1][1]))
                e=lineF.unitVector()
                new_lineF=QLineF(QPoint(self.circle_dict[value[1]][1][0]+int(e.dx()*self.d/2),self.circle_dict[value[1]][1][1]+int(e.dy()*self.d/2)),QPoint(self.circle_dict[value[2]][1][0]-int(e.dx()*self.d/2),self.circle_dict[value[2]][1][1]-int(e.dy()*self.d/2)))
                #如果已生成关键路径且图形是最新的,设定连接线为红色
                if line in self.critical_activity and self.isnew:
                    pen.setColor(Qt.red)
                else:#否则连接线为黑色
                    pen.setColor(Qt.black)
                pen.setStyle(Qt.SolidLine)
                qp.setPen(pen)
                #绘制连接线
                qp.drawLine(new_lineF)
                
                #运用向量计算箭头三个顶点
                e.translate(new_lineF.dx()+e.dx(), new_lineF.dy()+e.dy())
                n1=e.normalVector()
                n1.setLength(self.line_width)
                n2=n1.normalVector().normalVector()
                #如果已生成关键路径且图形是最新的,设定箭头为红色
                if line in self.critical_activity and self.isnew:
                    brush.setColor(Qt.red)
                else:#否则箭头为黑色
                    brush.setColor(Qt.black)
                brush.setStyle(Qt.SolidPattern)
                qp.setBrush(brush)
                #绘制箭头
                qp.drawPolygon(n1.p2(),n2.p2(),new_lineF.p2())
                
                #计算箭头上文字的长宽
                metrics=qp.fontMetrics()
                width=metrics.width(str(value[0]))
                height=metrics.height()
                head_pos=self.circle_dict[value[1]][1]
                tail_pos=self.circle_dict[value[2]][1]
                x=(head_pos[0]+tail_pos[0])/2-width/2
                y=(head_pos[1]+tail_pos[1])/2+height/2
                
                #绘制箭头上文字的底色
                brush.setColor(lightgray)
                brush.setStyle(Qt.SolidPattern)
                qp.setBrush(brush)            
                pen.setColor(lightgray)
                pen.setStyle(Qt.SolidLine)
                qp.setPen(pen)
                rect=QRect()
                rect.setRect((head_pos[0]+tail_pos[0])/2-width/2, (head_pos[1]+tail_pos[1])/2-height/2, width, height)
                qp.drawRect(rect)
                
                #如果已生成关键路径且图形是最新的,设定箭头上文字为红色
                if line in self.critical_activity and self.isnew:
                    pen.setColor(Qt.red)
                else:#否则设定文字为黑色
                    pen.setColor(Qt.black)
                pen.setStyle(Qt.SolidLine)
                qp.setPen(pen)
                #绘制箭头上文字
                qp.drawText(x, y, str(value[0]))
        #为了圆形的遮盖次序和选中次序统一,逆序绘制圆形
        circles=list(self.circle_dict.keys())
        circles.reverse()
        for circle in circles:
            value=self.circle_dict[circle]
            color=QColor()
            if self.isget and self.circle_gotton==circle:#如果圆形被选中设定颜色为青色
                color.setRgb(100,200,200)
            else:#否则设定颜色为黄色
                color.setRgb(255,255,150)
            brush=QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)
            qp.setBrush(brush)
            pen.setStyle(Qt.SolidLine)
            if circle in self.critical_affair and self.isnew:#如果已生成关键路径且图形是最新的,设定圆形边框为红色
                pen.setColor(Qt.red)
            else:#否则设定颜色为黑色
                pen.setColor(Qt.black)
            qp.setPen(pen)
            #绘制圆形
            qp.drawEllipse(value[1][0]-self.d/2,value[1][1]-self.d/2,self.d,self.d)
            
            #获取圆形上文字的长宽
            metrics=qp.fontMetrics()
            width=metrics.width(value[0])
            height=metrics.height()
            x=value[1][0]-width/2
            y=value[1][1]+height/2
            #绘制圆形上文字
            qp.drawText(x, y, value[0])
        #如果结果窗口已展开但图形不是最新的
        if not self.isnew and self.parent.isdock:
            #设置主窗口状态栏
            status=QStatusBar()
            status.showMessage('运行结果已过期')
            self.parent.mw.setStatusBar(status)
            #禁用主窗口保存结果按钮
            self.parent.mw.action_save_result.setEnabled(False)
            #收起主窗口
            self.parent.mw.dock_result.close()
            self.parent.isdock=False
    """
    函数：mousePressEvent(self, mouse)
    功能：处理鼠标左键单击事件
    传入参数：鼠标对象mouse
    传出参数：无
    """ 
    def mousePressEvent(self, mouse):
        if mouse.button()==Qt.LeftButton:#确认鼠标点击左键
            if self.status=="Move":#绘图行为是移动
                pos=(mouse.pos().x(),mouse.pos().y())
                #寻找鼠标点击的圆
                for circle,value in self.circle_dict.items():
                    if ((value[1][0]-pos[0])**2+(value[1][1]-pos[1])**2)**0.5<self.d/2:
                        #找到后记录该圆并将选中标志置真
                        self.circle_gotton=circle
                        self.isget=True
                        break
            elif self.status=="DrawCircle":#绘图行为是画圆
                #生成一个新的可用的圆形名字
                while 'c'+str(self.circle_count) in self.circle_dict:
                    self.circle_count+=1
                #将新生成的圆形加入到圆图形表
                self.circle_dict['c'+str(self.circle_count)]=['c'+str(self.circle_count),(mouse.pos().x(),mouse.pos().y()),[],[]]
                self.circle_count+=1#圆图形计数增1
                self.isnew=False#新图形标志置假
                self.parent.issave=False#上层对象的保存标志至假
                #将主窗口的名称后加入'*'
                self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
            elif self.status=="DrawLine":#绘图行为是画线
                pos=(mouse.pos().x(),mouse.pos().y())
                #寻找连接线起始圆形
                for circle,value in self.circle_dict.items():
                    if ((value[1][0]-pos[0])**2+(value[1][1]-pos[1])**2)**0.5<self.d/2:
                        #找到起始圆形,生成一个新的可用的连接线名字
                        while 'l'+str(self.line_count) in self.line_dict:
                            self.line_count+=1
                        self.line_dict['l'+str(self.line_count)]=[0,circle,'']#将连接线加入到连接线表
                        self.line_gotton='l'+str(self.line_count)#记录该连接线
                        self.circle_dict[circle][3].append('l'+str(self.line_count))#起始圆的出弧集加入该连接线
                        self.line_count+=1#连接线计数增1
                        self.isget=True#选中标志为真
                        self.line_dest_pos=pos#连接线终点设为鼠标位置
                        break
            elif self.status=="Delete":#绘图行为是删除
                isdelete=False#删除操作标志
                pos=(mouse.pos().x(),mouse.pos().y())
                #寻找鼠标点击的圆形
                for circle,value in self.circle_dict.items():
                    if ((value[1][0]-pos[0])**2+(value[1][1]-pos[1])**2)**0.5<self.d/2:
                        #找到后删除该圆形及其出弧,入弧
                        for in_line in value[2]:
                            head=self.line_dict[in_line][1]
                            self.circle_dict[head][3].remove(in_line)
                            self.line_dict.pop(in_line)
                        for out_line in value[3]:
                            tail=self.line_dict[out_line][2]
                            self.circle_dict[tail][2].remove(out_line)
                            self.line_dict.pop(out_line)
                        self.circle_dict.pop(circle)
                        #设定相关标志位和标题栏
                        isdelete=True
                        self.isnew=False
                        self.parent.issave=False
                        self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
                        break
                #如果没有删除圆,检查鼠标是否点中了连接线
                if not isdelete:
                    for line,value in self.line_dict.items():
                        if distance(self.circle_dict[value[1]][1],self.circle_dict[value[2]][1],pos)<self.line_width and dot_products(self.circle_dict[value[1]][1],self.circle_dict[value[2]][1],pos)>=0 and dot_products(self.circle_dict[value[2]][1],self.circle_dict[value[1]][1],pos)>=0:
                            #找到了点中的连接线,删除该连接线并对其起始圆,终点圆的数据进行更改
                            head=value[1]
                            tail=value[2]
                            self.circle_dict[head][3].remove(line)
                            self.circle_dict[tail][2].remove(line)
                            self.line_dict.pop(line)
                            #设定相关标志位和标题栏
                            self.isnew=False
                            self.parent.issave=False
                            self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
                            break
            self.update()#更新绘图区
        # print(self.circle_dict)
        # print(self.line_dict)
    """
    函数：mouseDoubleClickEvent(self,mouse)
    功能：处理鼠标双击事件
    传入参数：鼠标对象mouse
    传出参数：无
    """ 
    def mouseDoubleClickEvent(self,mouse):
        if self.status=="Move":#如果绘图行为是移动
            pos=pos=(mouse.pos().x(),mouse.pos().y())
            #寻找鼠标点击到的圆形
            for circle,value in self.circle_dict.items():
                if ((value[1][0]-pos[0])**2+(value[1][1]-pos[1])**2)**0.5<self.d/2:
                    #获取事件名称并更新圆图形数据和相关标志位
                    test,ok=QInputDialog.getText(self, "文本输入框", "输入事件名",QLineEdit.Normal,"",Qt.WindowCloseButtonHint)
                    if ok and test:
                        value[0]=test
                        self.isnew=False
                        self.parent.issave=False
                        self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
                    return
            #寻找鼠标点击到的连接线
            for line,value in self.line_dict.items():
                if distance(self.circle_dict[value[1]][1],self.circle_dict[value[2]][1],pos)<self.line_width and dot_products(self.circle_dict[value[1]][1],self.circle_dict[value[2]][1],pos)>=0 and dot_products(self.circle_dict[value[2]][1],self.circle_dict[value[1]][1],pos)>=0:
                    #获取弧权值并更新连接线数据和相关标志位
                    num,ok=QInputDialog.getInt(self, "整数输入框", "输入活动持续时间",0,0,65535,1,Qt.WindowCloseButtonHint)
                    if ok and num:
                        value[0]=num
                        self.isnew=False
                        self.parent.issave=False
                        self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
    """
    函数：mouseMoveEvent(self, mouse)
    功能：处理鼠标移动事件
    传入参数：鼠标对象mouse
    传出参数：无
    """ 
    def mouseMoveEvent(self, mouse):
        if self.status=="Move" and self.isget:#绘图行为是移动且已有选中的圆形
            #让该圆形的坐标跟随鼠标指针
            self.circle_dict[self.circle_gotton][1]=(mouse.pos().x(),mouse.pos().y())
            #更新相关标志位和标题
            self.parent.issave=False
            self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
            self.update()#更新绘图区
        elif self.status=="DrawLine" and self.isget:#绘图行为是画线且已有选中连接线
            #更新连接线终点坐标到鼠标指针
            self.line_dest_pos=(mouse.pos().x(),mouse.pos().y())
            self.update()#更新绘图区
    """
    函数：mouseReleaseEvent(self, mouse)
    功能：处理鼠标释放事件
    传入参数：鼠标对象mouse
    传出参数：无
    """                                    
    def mouseReleaseEvent(self, mouse):
        if mouse.button()==Qt.LeftButton:#确认左键释放
            if self.status=="Move" and self.isget:#绘图行为是移动且已选中圆形
                self.isget=False#选中标志复位
            if self.status=="DrawLine" and self.isget:#绘图行为是画线且已选中图形
                self.isget=False#选中标志复位
                find=False#找到标志为假
                pos=(mouse.pos().x(),mouse.pos().y())
                #寻找连接线终点所在的圆形
                for circle,value in self.circle_dict.items():
                    if ((value[1][0]-pos[0])**2+(value[1][1]-pos[1])**2)**0.5<self.d/2:
                        #确认这个圆形不是连接线起始圆形
                        if self.line_dict[self.line_gotton][1]!=circle:
                            isrepeat=False#重复标志为假
                            #寻找有没有与该连接线恰好反向的连接线
                            for line,value in self.line_dict.items():
                                if line!=self.line_gotton and (value[1]==self.line_dict[self.line_gotton][1] and value[2]==circle or value[2]==self.line_dict[self.line_gotton][1] and value[1]==circle):
                                    isrepeat=True
                                    break
                            #如果没有与该连接线恰好反向的连接线
                            if not isrepeat:
                                self.line_dict[self.line_gotton][2]=circle#设定连接线终点圆
                                self.circle_dict[circle][2].append(self.line_gotton)#设定终点圆入弧
                                #设定连接线权值
                                num,ok=QInputDialog.getInt(self, "整数输入框", "输入弧权值",0,0,65535,1,Qt.WindowCloseButtonHint)
                                if ok and num:
                                    self.line_dict[self.line_gotton][0]=num
                                #设定相关标志位和标题框
                                self.isnew=False
                                self.parent.issave=False
                                self.parent.mw.setWindowTitle("AOE网络-"+self.parent.curfilename+'*')
                                find=True
                        break
                if not find:#如果连接线终点不再任何圆形内
                    #删除该连接线并对更新其起始圆的出弧集
                    head=self.line_dict[self.line_gotton][1]
                    self.circle_dict[head][3].remove(self.line_gotton)
                    self.line_dict.pop(self.line_gotton)
                    self.line_count-=1
        
            self.update()#更新绘图区
            self.circle_gotton=''#清除选中的圆形
            self.line_gotton=''#清除选中的连接线
"""
类:主窗口
功能:完成UI界面的设定
"""
class MainWindow(QMainWindow):
    """
    函数：__init__(self,parent=None)
    功能：设定UI界面
    传入参数：上层对象parent
    传出参数：无
    """ 
    def __init__(self,parent=None):
        super(MainWindow,self).__init__()#父类MainWindow初始化
        self.parent=parent#上层对象
        loadUi("mainUI.ui",self)#加载UI文件
        self.setWindowTitle("AOE网络")#设定窗口标题
        self.setWindowIcon(QIcon("static/logo.ico"))#设定程序图标
        self.dock_result.close()#初始关闭结果窗口
        self.action_save_result.setEnabled(False)#初始禁用保存结果按钮
        img=QPixmap("static/doable.gif").scaled(self.label_doable_img.height(),self.label_doable_img.height())
        self.label_doable_img.setPixmap(img)#设定图标
        
        #设定工具栏操作
        self.editAction=QAction(QIcon('static/move.gif'),'编辑(Ctrl+E)',self)
        self.editAction.setShortcut('Ctrl+E')        
        self.affairAction=QAction(QIcon('static/drawcircle.gif'),'新增事件(Ctrl+R)',self)
        self.affairAction.setShortcut('Ctrl+R')
        self.activityAction=QAction(QIcon('static/drawline.gif'),'新增活动(Ctrl+T)',self)
        self.activityAction.setShortcut('Ctrl+T')
        self.deleteAction=QAction(QIcon('static/delete.gif'),'删除(Ctrl+D)',self)
        self.deleteAction.setShortcut('Ctrl+D')
        self.previewAction=QAction(QIcon('static/preview'),'速览(Ctrl+F)',self)
        
        self.toolbar=self.addToolBar("toolbar")
        self.toolbar.addAction(self.editAction)
        self.toolbar.addAction(self.affairAction)
        self.toolbar.addAction(self.activityAction)
        self.toolbar.addAction(self.deleteAction)
        self.toolbar.addAction(self.previewAction)
        #设定窗口主题
        self.setStyleSheet("#MainWindow{background-color: white;}")
        
        self.action_quit.triggered.connect(self.close)#将菜单栏退出按钮挂载到窗口退出函数
    """
    函数：closeEvent(self,event)
    功能：退出函数
    传入参数：event
    传出参数：无
    """
    def closeEvent(self,event):
        #上级对象的保存标志为假时询问是否保存当前文件
        if not self.parent.issave:
            reply=QMessageBox.question(self, '消息', '当前文件未保存，是否要保存当前文件？',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply==QMessageBox.Yes:
                self.parent.save()
        event.accept()
        
"""
类:程序主类
功能:实现UI窗口的行为和的对接前后端
"""        
class Main():
    """
    函数：__init__(self)
    功能：构造函数,对接前后端
    传入参数：无
    传出参数：无
    """
    def __init__(self):
        
        self.mw=MainWindow(self)#主窗口
        self.pw=PaintWindow(self)#绘图窗口
        self.mw.scrollArea.setWidget(self.pw)#将绘图窗口放入主窗口的scrollArea中
        
        #将窗口信号挂载到函数
        self.mw.action_open.triggered.connect(self.open_aoe)
        self.mw.action_save.triggered.connect(self.save)
        self.mw.action_save_as.triggered.connect(self.save_as)
        self.mw.action_save_image_as.triggered.connect(self.save_image_as)
        self.mw.action_save_result.triggered.connect(self.save_result)
        self.mw.action_fast_run.triggered.connect(self.preview)
        self.mw.action_run.triggered.connect(self.run)
        self.mw.action_help.triggered.connect(self.instruction)
        self.mw.editAction.triggered.connect(self.setDrawStatus) 
        self.mw.affairAction.triggered.connect(self.setDrawStatus)
        self.mw.activityAction.triggered.connect(self.setDrawStatus)
        self.mw.deleteAction.triggered.connect(self.setDrawStatus)
        self.mw.previewAction.triggered.connect(self.preview)
        
        self.isdock=False#dock栏打开标志,初始为假
        self.curfilename=""#当前文件名
        self.issave=True#当前文件保存标志,初始为假
        self.routes=[]#关键路径列表
        self.activities=[]#关键活动列表
        self.time=0#工程最短完成时间
        self.Ve={}#事件Vi的最早可能开始时间
        self.Vl={}#事件Vi的最迟允许开始时间
        self.e={}#活动ai的最早可能开始时间
        self.l={}#活动ai的最迟允许开始时间
    """
    函数：setDrawStatus(self)
    功能：设定绘图行为
    传入参数：无
    传出参数：无
    """
    def setDrawStatus(self):
        status=''
        if self.mw.sender().text()=='编辑(Ctrl+E)':
            status="Move"
        elif self.mw.sender().text()=='新增事件(Ctrl+R)':
            status="DrawCircle"
        elif self.mw.sender().text()=='新增活动(Ctrl+T)':
            status="DrawLine"
        elif self.mw.sender().text()=='删除(Ctrl+D)':
            status="Delete"
        self.pw.status=status
    """
    函数：preview(self)
    功能：预览AOE网络关键路径(试运行)
    传入参数：无
    传出参数：无
    """
    def preview(self):
        #当绘图窗口的圆图形字典为空时输出错误信息
        if len(self.pw.circle_dict)==0:
            msg=QMessageBox(QMessageBox.Critical,"错误","未绘制AOE网")
            msg.exec()
        else:
            ok,order=topologySort(self.pw.circle_dict,self.pw.line_dict)#拓扑排序
            if ok:#AOE网络合法
                #执行相关算法
                graph_head,graph_tail=transform(self.pw.circle_dict,self.pw.line_dict, order)
                aoe=AOE(graph_head,graph_tail,self.pw.circle_dict,self.pw.line_dict)
                self.pw.critical_activity,self.pw.critical_affair=aoe.function()#直线
                self.pw.update()#更新绘图区
                self.pw.isnew=True
                self.mw.dock_result.close()#关闭结果dock栏
                self.isdock=False
            else:#AOE网络不合法,输出错误信息
                msg=QMessageBox(QMessageBox.Critical,"错误","该工程不可行，AOE网络必须是单源点单汇点的有向无环图")
                msg.addButton("确定",QMessageBox.YesRole)
                msg.exec()
    """
    函数：run(self)
    功能：求解AOE网络关键路径，展示结果信息(正式运行)
    传入参数：无
    传出参数：无
    """
    def run(self):
        #当绘图窗口的圆图形字典为空时输出错误信息
        if len(self.pw.circle_dict)==0:
            msg=QMessageBox(QMessageBox.Critical,"错误","未绘制AOE网")
            msg.exec()
        else:
            ok,order=topologySort(self.pw.circle_dict,self.pw.line_dict)
            if ok:#AOE网络合法
                #执行相关算法
                graph_head,graph_tail=transform(self.pw.circle_dict,self.pw.line_dict, order)
                aoe=AOE(graph_head,graph_tail,self.pw.circle_dict,self.pw.line_dict)
                self.pw.critical_activity,self.pw.critical_affair=aoe.function()
                self.routes,self.activities=aoe.critical()
                self.time=aoe.time
                self.Ve=aoe.Ve
                self.Vl=aoe.Vl
                self.e=aoe.e
                self.l=aoe.l
                
                
                self.pw.update()#更新绘图区 
                self.pw.isnew=True
                status=QStatusBar()#更新状态栏
                status.showMessage('运行结果已更新')
                self.mw.setStatusBar(status)
                self.mw.action_save_result.setEnabled(True)#启用保存结果按钮
                               
                self.mw.label_time.setText(str(self.time))#显示工程最短运行时间
                
                #显示关键路径和关键活动
                self.mw.tableWidget_critical.setRowCount(len(self.routes))
                for i in range(len(self.routes)):
                    route=self.routes[i]
                    activity=self.activities[i]
                    item=QTableWidgetItem()
                    item.setText(route)
                    self.mw.tableWidget_critical.setItem(i,0,item)
                    item=QTableWidgetItem()
                    item.setText(activity)
                    self.mw.tableWidget_critical.setItem(i,1,item)
                    
                #显示Ve,Vl
                self.mw.tableWidget_v.setRowCount(len(self.Ve))
                row=0
                for v,ve in self.Ve.items():
                    vl=self.Vl[v]
                    name=self.pw.circle_dict[v][0]
                    item=QTableWidgetItem()
                    item.setText(name)
                    self.mw.tableWidget_v.setItem(row,0,item)
                    item=QTableWidgetItem()
                    item.setText(str(ve))
                    self.mw.tableWidget_v.setItem(row,1,item)
                    item=QTableWidgetItem()
                    item.setText(str(vl))
                    self.mw.tableWidget_v.setItem(row,2,item)
                    row+=1
                    
                #显示e,l
                self.mw.tableWidget_a.setRowCount(len(self.e))
                row=0
                for a,ae in self.e.items():
                    al=self.l[a]
                    name='<'+self.pw.circle_dict[self.pw.line_dict[a][1]][0]+','+self.pw.circle_dict[self.pw.line_dict[a][2]][0]+'>'
                    item=QTableWidgetItem()
                    item.setText(name)
                    self.mw.tableWidget_a.setItem(row,0,item)
                    item=QTableWidgetItem()
                    item.setText(str(ae))
                    self.mw.tableWidget_a.setItem(row,1,item)
                    item=QTableWidgetItem()
                    item.setText(str(al))
                    self.mw.tableWidget_a.setItem(row,2,item)
                    row+=1
                
                #显示结果dock栏
                self.mw.dock_result.show()
                self.mw.dock_result.setMinimumSize(540,500)
                self.isdock=True
            else:#工程不可行输出错误信息
                msg=QMessageBox(QMessageBox.Critical,"错误","该工程不可行，AOE网络必须是单源点单汇点的有向无环图")
                msg.addButton("确定",QMessageBox.YesRole)
                msg.exec()
    """
    函数：open_aoe(self)
    功能：打开aoe文件
    传入参数：无
    传出参数：无
    """
    def open_aoe(self):
        if not self.issave:#若当前文件未保存先保存当前文件
            reply=QMessageBox.question(self.mw, '消息', '当前文件未保存，是否要保存当前文件？',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply==QMessageBox.Yes:
                self.save()
        #打开aoe文件
        filename=QFileDialog.getOpenFileName(None,'打开AOE文件','./',".AOE(*.aoe)")
        if filename[0]!="":#判断是否选定了文件
            ok,circle_dict,line_dict=read(filename[0])
            if ok:
                self.pw.circle_dict=circle_dict
                self.pw.line_dict=line_dict
                self.curfilename=filename[0]
                self.issave=True
                self.mw.setWindowTitle("AOE网络-"+self.curfilename)
            else:
                msg=QMessageBox(QMessageBox.Critical,"错误","AOE文件打开失败")
                msg.addButton("确定",QMessageBox.YesRole)
                msg.exec()
    """
    函数：save(self)
    功能：保存aoe文件
    传入参数：无
    传出参数：无
    """
    def save(self):
        if self.curfilename!="":#如果当前aoe网络有对应的文件
            #重新写入aoe网络到文件
            ok=write(self.curfilename,self.pw.circle_dict,self.pw.line_dict)
            if not ok:
                msg=QMessageBox(QMessageBox.Critical,"错误","AOE网络保存失败")
                msg.addButton("确定",QMessageBox.YesRole)
                msg.exec()
            else:
                #更新保存标志,标题
                self.issave=True
                self.mw.setWindowTitle("AOE网络-"+self.curfilename)
        else:#否则需要新建文件
            self.save_as()
    """
    函数：save_as(self)
    功能：另存为aow网络
    传入参数：无
    传出参数：无
    """
    def save_as(self):
        #选择文件路径及文件名
        filename=QFileDialog.getSaveFileName(None,'保存AOE网络','./',".AOE(*.aoe)")
        if filename[0]!="":#判断是否选定了文件
            ok=write(filename[0],self.pw.circle_dict,self.pw.line_dict)
            if not ok:
                msg=QMessageBox(QMessageBox.Critical,"错误","AOE网络保存失败")
                msg.addButton("确定",QMessageBox.YesRole)
                msg.exec()
            else:
                #更新当前文件名,保存标志,标题
                self.curfilename=filename[0]
                self.issave=True
                self.mw.setWindowTitle("AOE网络-"+self.curfilename)
    """
    函数：save_image_as(self)
    功能：另存aow网络为图片
    传入参数：无
    传出参数：无
    """
    def save_image_as(self):
        filename=QFileDialog.getSaveFileName(None,'保存AOE网络为图片','./',".JPG(*.jpg);;.PNG(*.png);;.TIFF(*.tiff);;.BMP(*.bmp)")
        if filename[0]!="":
             #导出绘图窗口图片
            pixmap=QPixmap(self.pw.size())
            self.pw.render(pixmap)
            #根据选中的图片格式保存图片
            if filename[1]==".JPG(*.jpg)":
                pixmap.save(filename[0],"jpg",100)
            elif filename[1]==".PNG(*.png)":
                pixmap.save(filename[0],"png",100)
            elif filename[1]==".TIFF(*.tiff)":
                pixmap.save(filename[0],"tiff",100)
            elif filename[1]==".BMP(*.bmp)":
                pixmap.save(filename[0],"bmp",100)
    """
    函数：save_result(self)
    功能：保存运行结果
    传入参数：无
    传出参数：无
    """
    def save_result(self):
        filename=QFileDialog.getSaveFileName(None,'保存结果','./',".XLS(*.xls)")
        if filename[0]!="":#判断是否选定了文件
            #结果表格写入到excel表格中
            workbook=xlwt.Workbook(encoding="utf-8")
            worksheet1=workbook.add_sheet("概览")
            worksheet2=workbook.add_sheet("事件时间表")
            worksheet3=workbook.add_sheet("活动时间表")
            
            worksheet1.write(0,0,"工程最早完成时间")
            worksheet1.write(0,1,self.time)
            worksheet1.write(1,0,"关键路径")
            worksheet1.write(1,1,"关键活动")
            
            for row in range(2,len(self.routes)+2):
                worksheet1.write(row,0,self.routes[row-2])
                worksheet1.write(row,1,self.activities[row-2])
                
            worksheet2.write(0,0,"事件i")
            worksheet2.write(0,1,"Ve[i]")
            worksheet2.write(0,2,"Vl[i]")
            
            row=1
            for v,ve in self.Ve.items():
                vl=self.Vl[v]
                name=self.pw.circle_dict[v][0]
                worksheet2.write(row,0,name)
                worksheet2.write(row,1,ve)
                worksheet2.write(row,2,vl)
                row+=1
            
            worksheet3.write(0,0,"活动i")
            worksheet3.write(0,1,"e[i]")
            worksheet3.write(0,2,"l[i]")
            
            row=1
            for a,ae in self.e.items():
                al=self.l[a]
                name='<'+self.pw.circle_dict[self.pw.line_dict[a][1]][0]+','+self.pw.circle_dict[self.pw.line_dict[a][2]][0]+'>'
                worksheet3.write(row,0,name)
                worksheet3.write(row,1,ae)
                worksheet3.write(row,2,al)
                row+=1
            #保存该excel表格    
            workbook.save(filename[0])
    """
    函数：instruction(self)
    功能：显示程序指南
    传入参数：无
    传出参数：无
    """
    def instruction(self):
        msg=QMessageBox(QMessageBox.Information,"使用说明","\
【功能概述】\n\
本软件可以通过图形画操作绘制AOE网络，基本绘图操作与主流绘图软件相似，可以对AOE网络执行保存、另存为、打开等文件操作,\
文件格式为.aoe文件，还可以将绘制的AOE网络保存为图片。对于某个正确的AOE工程可以运用算法求出工程的最早完成时间关键路径和关键活\
动，并在绘图区以红色标注出关键路径。同时给出工程中每个活动的最早开始时间e(i)，最迟开始时间l(i)，每个事件的最早开始时间e(i),\
最晚开始时间l(i),并可以将结果保存为.xls文件\n\
【工具栏工具说明】\n\
1)编辑工具：使用该工具拖动现有顶点位置，在顶点(弧)上双击可以修改顶点名称(弧权值)\n\
2)新增事件工具：使用该工具在空白位置点击可以在鼠标点击位置新增一个AOE网络顶点\n\
3)新增活动位置：使用该工具按住鼠标左键从一个顶点向另一个顶点画线，生成AOE网络的一条弧\n\
4)删除工具：使用该工具在顶点(弧)上单机以删除\n\
5)预览工具：快速检测AOE网络的可运行性，快速查看关键路径，该工具也能在“运行”菜单中找到")
        msg.addButton("确定",QMessageBox.YesRole)
        msg.exec()

if __name__=="__main__":
    app=QApplication(sys.argv)#初始化应用程序
    m=Main()#构建主对象
    m.mw.show()#显示主窗口
    app.exec_()#退出应用程序