# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 13:32:10 2022

@author: natan
"""

from sympy import *
from math import *
import numpy as np

#from braccio_control_python import get_previous_teta


l0=71.5
l1=125
l2=125
l3=60+132


def move_to_position_cart(x,y,z):
    r_compensation=1.02 #add 2 percent
    z=z+15  #compensation for backlash
    r_hor=sqrt(x**2+y**2)
    r=sqrt(r_hor**2+(z-71.5)**2)*r_compensation
    
    if y==0:
        if x<=0:
            theta_base=180
        else:
            theta_base=0
    else:
        theta_base=90-degrees(atan(x/y))  #add 2 degrees for backlash compensation
    #print(theta_base)
    #theta_base=backlash_compensation_base(theta_base)  #check if compensation is needed
    
    #calulcate angles for level operation
    
    alpha1=acos(((r-l2)/(l1+l3)))
    theta_shoulder=degrees(alpha1)
    alpha3=asin((sin(alpha1)*l3-sin(alpha1)*l1)/l2)  #compensate for the difference in arm length
    theta_elbow=(90-degrees(alpha1))+degrees(alpha3)
    theta_wrist=(90-degrees(alpha1))-degrees(alpha3)
    
    if theta_wrist <=0: #when arm length compensation results in negative values
        alpha1=acos(((r-l2)/(l1+l3)))
        theta_shoulder=degrees(alpha1+asin((l3-l1)/r))
        theta_elbow=(90-degrees(alpha1))
        theta_wrist=(90-degrees(alpha1))
    
    #adjust shoulder angle to increase heigth
    if z!=l0:
        theta_shoulder=theta_shoulder+degrees(atan(((z-l0)/r)))
        #print(degrees(atan(((z-l0)/r))))
    
    #add compensation for bad line-up of servo with mount
    theta_elbow=theta_elbow+5  
    theta_wrist=theta_wrist+5  
    
    
    theta_array=[round(theta_base),round(theta_shoulder),round(theta_elbow),round(theta_wrist)]
    
    return theta_array

def get_previous_teta2():
    text_file = open("prev_teta.txt", "r")
    prev_teta_string=text_file.read()
    text_file.close()
    
    prev_teta= list(prev_teta_string.split(";"))
    prev_teta.pop(6)
    prev_teta=[int(i) for i in prev_teta]
    return prev_teta


def backlash_compensation_base(theta_base):
    theta_base=round(theta_base)
    theta_base_comp=theta_base
    
    compensation_value_CW=8  #degrees (CW roation)
    compensation_value_CCW=np.linspace(0, 14,135)
    prev_angles=get_previous_teta2()  #get previous theta's from txt file
    theta_base_prev=prev_angles[0]
    
    delta_theta_base=theta_base-theta_base_prev
    # print(delta_theta_base)
    if delta_theta_base>1:
        if theta_base<=45:
            theta_base_comp=theta_base
        else:
            index=int(round(theta_base-46))
            theta_base_comp=theta_base+compensation_value_CCW[index]
            theta_base_comp=round(theta_base_comp)
            # print("base theta compensated CCW, val: "+str(round(compensation_value_CCW[theta_base-46])))
    if delta_theta_base<-1:
        theta_base_comp=theta_base-compensation_value_CW
        # print("base theta compensated CW, val: "+str(compensation_value_CW))

        
    return theta_base_comp
    
    
    