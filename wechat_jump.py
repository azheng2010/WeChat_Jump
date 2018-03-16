# -*- coding: utf-8 -*-
"""
Created on 2018-02-06 17:31:25
@author: wangzheng
Sys_Env : Windows_AMD64 Python3.5.2
Email:yaoyao12348@126.com
filename: wechat_jump_py3.py
fun : 微信跳一跳手动实现
"""
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import random
import cv2
    
def get_score():
    '''图像识别获取分数，[x,y]切割成4个方块
    2.从左至右识别分数
    3.转化成数字  pwd当前目录
    '''
    #pp='C:/Users/wangzheng/'
    global pwd
    pp=pwd
    img=cv2.imread(pp+'autojump.png',cv2.IMREAD_GRAYSCALE)#灰度模式读取图片，720*1280
    tpls=['1.png','2.png','3.png','4.png','5.png',
          '6.png','7.png','8.png','9.png','0.png']
    x=[(83,127),(136,180),(189,233),(243,287)]
    y=[(136,191),]
    score_str=''#得分
    for i in range(len(x)):
        img0=img[y[0][0]:y[0][1],x[i][0]:x[i][1]]
        #ret, thresh = cv2.threshold(img0, 100, 255,cv2.THRESH_BINARY)#二值化图片
        #pic=thresh#位置
        pic=img0
        cv2.imwrite('pos%s.png'%i,pic)
        for tpl in tpls:
            img_tpl=cv2.imread(pp+'templete/'+tpl,cv2.IMREAD_GRAYSCALE)
            #归一化平方差匹配法，越小越好（min_val<0.1）
            #res = cv2.matchTemplate(pic,img_tpl,cv2.TM_SQDIFF_NORMED)
            #归一化相关匹配法，越大越好（max_val>0.9）
            #res = cv2.matchTemplate(pic,img_tpl,cv2.TM_CCORR_NORMED)
            #归一化相关系数匹配法，越大越好（max_val>0.9）
            res = cv2.matchTemplate(pic,img_tpl,cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)
            #print('位置%s与%s相关度：%s'%(i+1,tpl,max_val))
            if max_val>0.9:
                #print('位置%s与%s相关度：%s'%(i+1,tpl,max_val))
                score_str=score_str+tpl[0]
                break
    #print("得分",score_str)
    if score_str is not '':
        return int(score_str)
    else:return 0

def pull_screenshot():
    os.system('adb shell screencap -p /sdcard/autojump.png')
    os.system('adb pull /sdcard/autojump.png .')
    
#    global score
    score=get_score()
    if jump_count>0:
        score_avg=round(score/jump_count,2)
        print('平均分%s'%score_avg)

def jump(distance):
    '''跳跃动作'''
    #press_time = distance * 1.35#原版
    #press_time = distance * 1.85#调试
    press_time = distance * 2.05#分辨率720X1280
    press_time = int(press_time)
    #cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    x=360+random_span(spanX)
    y=960+random_span(spanY)
    cmd = 'adb shell input swipe {X} {Y} {X} {Y} '.format(X=x,Y=y) + str(press_time)#360,960
    #print(cmd)
    os.system(cmd)

def update_data():
    return np.array(Image.open('autojump.png'))

def updatefig(*args):
    global update
    global cir_point
    global pwd
    if update:
        #time.sleep(1.5)
        time.sleep(0.8)
        pull_screenshot()
        #
        print('-'*40)
        cir_point=match_pic(pwd+'templete/chessman.png',pwd+'autojump.png')
        #print('棋子当前位置',cir_point)#标记质心
        im.set_array(update_data())
        update = False
    return im,

def on_click2(event):
    global jump_count#跳跃次数
    global t0,t1,t2
    global update
    global ix, iy
    global click_count
    global cor
    global cir_point
    global score

    ix, iy = event.xdata, event.ydata
    coords = (ix, iy)
    #print('点击位置= ', coords)
    distance = (cir_point[0] - coords[0])**2 + (cir_point[1] - coords[1])**2
    distance = distance ** 0.5
    #print('distance = ', distance)
    jump(distance)
    if t1<=0 :t1=t0
    t2=time.time()#本次计时
    jump_count+=1
    #print('='*30)
    #print("已经跳了",jump_count,"跳")
    t3=t2-t1#本跳费时
    t4=t2-t0#总费时
    t5=t4/jump_count#平均费时
    print("第%s跳\t单跳耗时%.1fs,平均%.1fs"%(jump_count,t3,t5))
    #print('='*30)
    t1=t2
    update = True
    
def random_span(span):
    '''在[-d/2,+d/2]范围随机取值'''
    d=int(span)
    return random.choice(range(int(-d/2),int(d/2)))        
    
def match_pic(tempath,targetpath,methond=cv2.TM_SQDIFF_NORMED):
    '''tempath模板图路径,targetpath目标图路径'''
    #模板图片  
    tpl=cv2.imread(tempath)
    #目标图片  
    target=cv2.imread(targetpath) 
    tarh,tarw=target.shape[:2]
    target_o=target[int(tarh/3):int(tarh*2/3),0:tarw]#截取目标图片的中间1/3用来匹配模板  [h,w]
    #cv2.imshow('template',tpl)  
    #cv2.imshow('target',target)  
    #匹配模式
    #methods=[cv2.TM_SQDIFF_NORMED,cv2.TM_CCORR_NORMED,cv2.TM_CCOEFF_NORMED]  
  
    #获得模板的高宽  
    th,tw=tpl.shape[:2]  
    md=methond
  
    #执行模板匹配  
    #target：目标图片  tpl：模板图片 md：匹配模式
    #result=cv2.matchTemplate(target,tpl,md)
    result=cv2.matchTemplate(target_o,tpl,md)
    #寻找矩阵(一维数组当作向量,用Mat定义) 中最小值和最大值的位置  
    min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)  
    if md==cv2.TM_SQDIFF_NORMED:  
        tl=min_loc  
    else:  
        tl=max_loc
    tl=( tl[0] , tl[1]+int(tarh/3) ) #tl重新赋值，恢复截取前高度
    br=(tl[0]+tw,tl[1]+th)  
    #绘制矩形边框，将匹配区域标注出来  
    #target：目标图像  
    #tl：矩形顶点(左上)
    #br：矩形的宽高  
    #(0,0,255)：矩形边框颜色  
    #2：矩形边框大小  
    cv2.rectangle(target,tl,br,(0,0,255),2)  #画矩形框
    
    pos=(tl[0]+int(tw/2),tl[1]+th-int(tw/4))#棋子底座中心坐标
    #radius=int(tw/2)#半径
    #cv2.circle(target, pos, radius, (0,255,0), 1)#画圆圈
    cv2.circle(target, pos, 2, (0,0,255), 2)#画圆点
    #cv2.imshow('match-'+np.str(md),target)  
    cv2.imwrite('autojump.png',target)
    return pos
    

#全局变量
pwd= 'C:/Users/wangzheng/'
update = True
click_count = 0
cor = []
spanX=70;spanY=90#按键区域XY方向上的波动范围
cir_point=(0,0)
jump_count=0#跳跃次数
t0=time.time()#计时
t1=0.0
t2=0.0
score=-1#本跳分
score_last=-1#上一跳分数
fig = plt.figure()
pull_screenshot()
img = np.array(Image.open(pwd+'autojump.png'))
im = plt.imshow(img, animated=True)


#-------------执行---------------------       
#fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('button_press_event', on_click2)#改进版
ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=True)
plt.show()
