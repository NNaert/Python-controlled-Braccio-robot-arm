# -*- coding: utf-8 -*-
# """
# Created on Sun Nov 28 12:21:04 2021

# @author: natan
# """


# Importing Libraries
# %%

import serial
import time
import solverNNA
import numpy as np

base =[0,0,180,0]  #default value for base, min value and max value, write location
shoulder=[150,15,165,1]
elbow=[0,0,180,2]
wrist=[0,0,180,3]
wristRot=[90,0,180,4]
gripper=[73,73,0,5]


arm = serial.Serial('COM4', 115200, timeout=5)
print("Initializing arm") 
time.sleep(2)
arm.write(b'H0,90,20,90,90,73,20\n')  #home the arm at low speeds
time.sleep(2)



def write_arduino(angles):
    
    angles[0]=180-angles[0]  #invert degrees for base
    angles[3]=180-angles[3]  #invert degrees for base
    angle_string=','.join([str(elem) for elem in angles])  # join the list values togheter
    angle_string="P"+angle_string+",200\n"    
    arm.write(angle_string.encode())          #.encode encodes the string to bytes
            
    

def rotate_joint(joint):  #rotate a specifi joint to the outer limits of the joint angles

    def calculate_joint(joint,number):
        angle_string_def_angles=[base[0],shoulder[0],elbow[0],wrist[0],wristRot[0],gripper[0]]  #load in default values
        angle_string_def_angles[joint[3]]=joint[number]  #write minimum angle to the string
        write_arduino(angle_string_def_angles)
        
    calculate_joint(joint,1)
    time.sleep(2)
    calculate_joint(joint,2)
    time.sleep(2)
    calculate_joint(joint,1)
    time.sleep(2)
    
    
    
def home(speed=20):
    angle_string_def_angles=[base[0],shoulder[0],elbow[0],wrist[0],wristRot[0],gripper[0]]
    write_arduino(angle_string_def_angles)

def rotate_all_joints():
    print("The base.")
    rotate_joint(base)
    print("The shoulder.")
    rotate_joint(shoulder)
    print("The elbow.")
    rotate_joint(elbow)
    print("The vertical axis of the wrist.")
    rotate_joint(wrist)
    print("The rotational axis of the wrist.")
    rotate_joint(wristRot)
    print("The gripper.")
    rotate_joint(gripper)
  
def write_position(theta_base=base[0],theta_shoulder=shoulder[0],theta_elbow=elbow[0],theta_wrist=wrist[0],theta_wristRot=wristRot[0],grip="closed"):
    
    if grip=="closed":
        theta_gripper=gripper[1]
    if grip=="open":
        theta_gripper=gripper[2]

    theta_base_comp=solverNNA.backlash_compensation_base(theta_base)  #check if compensation is neededbacklash_compensation_base(theta_base)  #check if compensation is needed    
        
    angle_string_def_angles=[theta_base_comp,theta_shoulder,theta_elbow,theta_wrist,theta_wristRot,theta_gripper]
    write_arduino(angle_string_def_angles)
    
    #write angle values in txt file without the compensation
    angles=[theta_base,theta_shoulder,theta_elbow,theta_wrist,theta_wristRot,theta_gripper]
    text_file = open("prev_teta.txt", "w")
    iteration=[0,1,2,3,4,5]
    for elem in iteration:
        text_file.write(str(angles[elem]))
        text_file.write(";")
    text_file.close()
    
    
def go_to_coordinate(x,y,z,grip_position="closed"):
    theta_list=solverNNA.move_to_position_cart(x,y,z)
    write_position(theta_list[0],theta_list[1],theta_list[2],theta_list[3],grip=grip_position)
    
    
def move_vertical(x,y):
    loop_iteration=np.linspace(0, 350, 2)
    for z in loop_iteration:
        print(z)
        go_to_coordinate(x,y,round(z))
        time.sleep(2)
        
def move_horizontal(z):
    loop_iteration=np.linspace(100, 350,2)
    for x in loop_iteration:
        print(x)
        go_to_coordinate(round(x),0,z)
        time.sleep(2)
        
        
def get_previous_teta():
    text_file = open("prev_teta.txt", "r")
    prev_teta_string=text_file.read()
    text_file.close()
    
    prev_teta= list(prev_teta_string.split(";"))
    prev_teta.pop(6)
    prev_teta=[int(i) for i in prev_teta]
    return prev_teta

def open_gripper():
    prev_angles=get_previous_teta()
    write_position(prev_angles[0],prev_angles[1],prev_angles[2],prev_angles[3],prev_angles[4],grip="open")
    
def close_gripper():
    prev_angles=get_previous_teta()
    write_position(prev_angles[0],prev_angles[1],prev_angles[2],prev_angles[3],prev_angles[4],grip="closed")  
    
    
    
def pick_up(x,y):
    glass_pos=[310,95] #x,y pos of glass
    delay=1  #delay between steps
    pick_up_heigth=10  #heigth of the object
    home()
    time.sleep(delay)
    go_to_coordinate(x,y,100,"closed")
    time.sleep(delay)
    open_gripper()
    time.sleep(delay)
    print('pick-up foam')
    go_to_coordinate(x,y,pick_up_heigth-20,"open")
    time.sleep(delay)
    close_gripper()
    time.sleep(delay)
    go_to_coordinate(x,y,200,"closed")
    time.sleep(delay)
    go_to_coordinate(glass_pos[0],glass_pos[1],200,"closed")
    time.sleep(delay)
    go_to_coordinate(glass_pos[0],glass_pos[1],120,"closed")
    time.sleep(delay)
    open_gripper()
    home()
    
def backlash():
    time.sleep(5)
    write_position(90,0,90,90)
    time.sleep(2)
    write_position(45,0,90,90)
    time.sleep(2)
    write_position(90,0,90,90)

# %%
def camera_compensation(x_coordinate,y_coordinate):
    h_foam=80  #fam heigth of 80mm
    camera_position=[480,150,880]  #x,y,z coordinate from origin in mm
    #add 300 to move orgin to under the camera
    offset=300
    x_coordinate=(offset-x_coordinate)+(camera_position[0]-offset)
    
    #perform compensation
    x_compensated=x_coordinate-(h_foam/(camera_position[2]/x_coordinate))
    if y_coordinate<camera_position[1]:
        y_compensated=y_coordinate-(h_foam/(camera_position[2]/y_coordinate))
    else:
        y_compensated=y_coordinate+(h_foam/(camera_position[2]/y_coordinate))
    #substract the offset
    x_compensated=offset-(x_compensated-(camera_position[0]-offset))
    
    return int(x_compensated),int(y_compensated)
    
# %%
