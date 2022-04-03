# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 20:42:49 2022

@author: natan
"""
# %%

import cv2
#import cv2.aruco as aruco
import numpy as np
import time

# def findArucoMarkers(img, markerSize = 4, totalMarkers=50, draw=True):    
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     key = getattr(cv2.aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
#     arucoDict = cv2.aruco.Dictionary_get(key)
#     arucoParam = cv2.aruco.DetectorParameters_create()
#     bboxs, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
#     #print(bboxs)
#     if draw:
#         cv2.aruco.drawDetectedMarkers(img, bboxs) 
#     if ids is not None:
#         ids_sorted=[]
#         for id_number in ids:
#             ids_sorted.append(id_number[0])
#     else:
#         ids_sorted=ids
#     return bboxs,ids_sorted
        
def getMarkerCoordinates(markers,ids,point=0): #take first corner of th emarker, if point equal to 5, get center
    #nr_of_markers=len(markers)
    marker_array=[]
    #make a list with the desired corners
    for marker in markers:
        marker_array.append([int(marker[0][point][0]),int(marker[0][point][1])])
    #put the list in order of the marker ID's.

    return marker_array,ids

def getMarkerCenter_foam(marker):
    left_top,ids =getMarkerCoordinates(marker,1,point=0) #first corner
    right_top,ids =getMarkerCoordinates(marker,1,point=1) #2 corner    
    left_bot,ids =getMarkerCoordinates(marker,1,point=2) #3 corner
    right_bot,ids =getMarkerCoordinates(marker,1,point=3) #4 corner
    #print(left_top)
    if bool(left_top):
        center_X=(left_top[0][0]+right_top[0][0]+left_bot[0][0]+right_bot[0][0])*0.25
        center_Y=(left_top[0][1]+right_top[0][1]+left_bot[0][1]+right_bot[0][1])*0.25
        markerCenter=[[int(center_X),int(center_Y)]]
    else:
        markerCenter=[[0,0]]
    #print(markerCenter)
    return markerCenter

        
def draw_corners(img,corners):
    for corner in corners:    
        cv2.circle(img,(corner[0],corner[1]),10,(0,255,0),thickness=-1)       

def draw_numbers(img,corners,ids):
    number=0
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 4
    for corner in corners:    
        cv2.putText(img,str(ids[number]),(corner[0]+10,corner[1]+10), font, 2,(0,0,0),thickness)
        number=number+1
        
def show_spec(img,corners):
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1
    amountOfCorners=len(corners)
    spec_string=str(amountOfCorners)+" markers found."
    cv2.putText(img,spec_string,(15,15), font, 0.5,(0,0,250),thickness)
        
def draw_field(img,corners,ids):   #only when 4 ID's are available
    if len(corners)==4:
        markers_sorted=[0,0,0,0] #sort markers in order to 
        for sorted_corner_id in [1,2,3,4]:
            index=ids.index(sorted_corner_id)
            markers_sorted[sorted_corner_id-1]=corners[index]
        contours = np.array(markers_sorted)      
        overlay = img.copy()
        cv2.fillPoly(overlay, pts =[contours], color=(255,215,0))
        alpha = 0.4  # Transparency factor.
        # Following line overlays transparent rectangle over the image
        img_new=cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        squarefound=True
    else:
        img_new=img
        squarefound=False
    return img_new,squarefound


def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect



def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

# # %%
# url = 'http://192.168.0.12:8080/videofeed'
# cap = cv2.VideoCapture(0)
# #cap = videothreading.VideoGet(1)
# square_points=[[10,10], [10,cv2.CAP_PROP_FRAME_WIDTH-10], [cv2.CAP_PROP_FRAME_HEIGHT-10, 10], [cv2.CAP_PROP_FRAME_HEIGHT-10,cv2.CAP_PROP_FRAME_WIDTH-10]] #initial square


