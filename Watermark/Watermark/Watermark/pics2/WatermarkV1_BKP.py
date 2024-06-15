# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 19:46:53 2022

@author: ASUS
"""
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import cv2
import os
from tkinter import *
from PIL import Image,ImageDraw,ImageFont
import shutil
from tkinter.font import Font


root = Tk()
root.title('Watermarking System')
# root.geometry('{}x{}'.format(900, 900))

width= root.winfo_screenwidth()
height= root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))

# create all of the main containers
top_frame = Frame(root, bg='#292250', width=450, height=50, pady=3)
center = Frame(root, bg='gray2', width=100, height=300, padx=3, pady=3)
# btm_frame = Frame(root, bg='white', width=450, height=5, pady=3)
# btm_frame2 = Frae(root, bg='lavender', width=450, height=60, pady=3)

# layout all of the main containers
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame.grid(row=0, sticky="ew")
top_frame.grid_propagate(False)
top_frame.grid_columnconfigure(1, weight=1)
center.grid(row=1, sticky="nsew")
# btm_frame.grid(row=3, sticky="ew")
# btm_frame2.grid(row=4, sticky="ew")

# create the widgets for the top frame
my_font = Font(
    family = 'Times',
    size = 20,
    weight = 'bold',
    slant = 'italic',
    underline = 1,
    overstrike = 0
)
model_label = Label(top_frame, text='Watermarking System - Add logo/text to images', font=my_font)



# layout the widgets in the top frame
#model_label.grid(row=0, columnspan=3)
model_label.grid(row=0, columnspan=10)
#width_label.grid(row=1, column=0)
#length_label.grid(row=1, column=2)
#entry_W.grid(row=1, column=1)
#entry_L.grid(row=1, column=3)

# create the center widgets
# center.grid_rowconfigure(0, weight=1)
# center.grid_columnconfigure(1, weight=1)

ctr_left = Frame(center, bg='#273029', width=400, height=500,highlightbackground="white", highlightthickness=2)
ctr_mid = Frame(center, bg='#273029', width=400, height=190,highlightbackground="white", highlightthickness=2)
ctr_right = Frame(center, bg='#273029', width=800, height=500, padx=3, pady=3,highlightbackground="white", highlightthickness=2)

ctr_left.grid(row=0, column=0, sticky="nsew")
ctr_mid.grid(row=0, column=1, sticky="nsew")
ctr_right.grid(row=0,rowspan=2, column=2, sticky="nsew")


ctr_left.grid_propagate(False)
# ctr_left.grid_columnconfigure(1, weight=1)


f1 = Frame(ctr_left,bg='#a19c57',width=400,height=80,highlightbackground="white", highlightthickness=2)
f1.grid(row=0, column=0,sticky='ew')
f2 = Frame(ctr_mid,bg='#a19c57',width=400,height=80,highlightbackground="white", highlightthickness=2)
f2.grid(row=0, column=0)
f3 = Frame(ctr_right,bg='#a19c57',width=800,height=80,highlightbackground="white", highlightthickness=2)
f3.grid(row=0, column=0)

ftxt = Frame(center,bg='#273029',width=700,height=250,highlightbackground="white", highlightthickness=2)
ftxt.grid(row=1, columnspan=2, sticky='we')


ibtn = PhotoImage(file='C:/Watermark/Watermark/src/upload_img.png')
photoimage2 = ibtn.subsample(4,4)
bt1font = Font(weight="bold",size = 15)

imgbtn = tk.Button(f1, text='Upload Image',compound = RIGHT,image=photoimage2 ,command = lambda:upload_file())
imgbtn['font']=bt1font
imgbtn.place(x=10,y=5)

i = PhotoImage(file='C:/Watermark/Watermark/src/upload_logo.png')
photoimage = i.subsample(4,4)
bt2font = Font(weight="bold",size = 15)
logobtn = tk.Button(f2, text='Upload Logo    ', compound = RIGHT,image=photoimage,command = lambda:upload_logo())
logobtn['font']=bt2font
logobtn.place(x=70,y=5)

outbtn = tk.Button(f3, text='Add Watermark', width=20,font=bt2font,command = lambda:watermark())
outbtn.place(x=80,y=5)

text_head_font=Font(weight="bold",size = 15)
text_head=Label(ftxt,text="Text Watermark", font=text_head_font)
text_head.place(x=250,y=10)

#type area of add text
eText = Entry(ftxt, width=20,relief = 'sunken',)
txtlbl = Label(ftxt,text="Enter the text:")
txtlbl.place(x=15,y=80)
eText.place(x=110,y=80)

#add text checkbutton
ch1=IntVar()
c1 = Checkbutton(ftxt,text="Add the Text",variable = ch1)
c1.place(x=20,y=120)

fimg = Frame(ctr_left,bg='#273029',width=400,height=500)
fimg.grid(row=1, column=0)

flg = Frame(ctr_mid,bg='#273029',width=400,height=300)
flg.grid(row=1, column=0)
# label = Label(flg,text="test")
#label.pack()

# label2 = Label(ctr_left,text="2")
# label2.grid(row=2,column=0)
# Label(ctr_left,text="test32fdssssss222222").grid(row=1,column=1)

# label.grid_rowconfigure((0,1), weight=1)
# label.grid_columnconfigure((0,3), weight=1)
def upload_logo():
#     f_types = [('Jpg Files', '*.jpg'),('PNG Files','*.png')]   # type of files to select 
    f_types = [('Jpg Files', '*.jpg')] 
    filename = tk.filedialog.askopenfilename(multiple=True,filetypes=f_types)
    col=0 # start from column 1
    row=1 # start from row 3 
    path = "C:/Watermark/Watermark/logo/"
    for f in filename:
        img=Image.open(f) # read the image file
        img.save(path+'logo.jpg')
#         print(f.split('/')[-1])

        img=img.resize((100,100)) # new width & height
        img=ImageTk.PhotoImage(img)
        e2 =tk.Label(flg)
#        Label(flg,text='texttest').pack()
#        e2.pack()
        e2.grid(row=row,column=col)
        e2.image = img
        e2['image']=img 
        if(col==2): 
            row=row+1
            col=1    
        else:       
            col=col+1 
def upload_file():
#     f_types = [('Jpg Files', '*.jpg'),('PNG Files','*.png')]   # type of files to select 
    f_types = [('Jpg Files', '*.jpg')] 
    filename = tk.filedialog.askopenfilename(multiple=True,filetypes=f_types)
    col=0 # start from column 1
    row=1 # start from row 3 
    cnt = 1
    path = "C:/Watermark/Watermark/images/"
#    shutil.rmtree(path)
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))
    for f in filename:
        img=Image.open(f) # read the image file
        print(f.split('/')[-1])
        img.save(path+'img'+str(cnt)+'.jpg')
        cnt+=1
        img=img.resize((100,100)) # new width & height
        img=ImageTk.PhotoImage(img)
        e1 =tk.Label(fimg)
#         e1.grid()
        e1.grid(row=row,column=col)
#         e1.place(x=10,y=20)
        e1.image = img
        e1['image']=img 
#         row=row+1
        if(col==4): 
            row=row+1
            col=0
        else:
            col=col+1
           #C:\Watermark\Watermark\images 
def watermark():
    dir_path = r'C:/Watermark/Watermark/images/'
    del_path=r'C:/Watermark/Watermark/output/'
    for d in os.listdir(del_path):
        os.remove(os.path.join(del_path, d))

    files=  []
    c = 1
#     tex = e1.get()
#     print(tex)
    for path in os.listdir(dir_path):
    #         print(os.path.join(dir_path, path))
        files.append(os.path.join(dir_path, path))
        
    if ch1.get()==1:
#         text="hhh"
        text = eText.get()
        #print(text)
        
        for f in files:
            photo = Image.open(f)
            drawing = ImageDraw.Draw(photo)
            pos=(180, 200)
            color = (142, 141, 148)
            font = ImageFont.truetype("arial.ttf", 80)
            drawing.text(pos, text, fill=color, font=font)
            filename = 'C:/Watermark/Watermark/output/Watermakred_Image'+str(c)+'.jpg'
            c+=1
            photo.save(filename)
        

        
    else:
        

        for f in files:
    #         img = cv2.imread('E:/Meera/Watermark/images/img.jpg')
            img = cv2.imread(f)
    #         print(f)
            watermark = cv2.imread("C:/Watermark/Watermark/logo/logo.jpg")
            lo_w=int(watermark.shape[1])
            lo_h=int(watermark.shape[0])
            if lo_w>250 and lo_h>250:
                print("Logo size more than 250x250")
    #         watermark = cv2.imread("E:/Meera/Watermark/workspace/lg.png")
    
            percent_of_scaling = 20
            new_width = int(img.shape[1] * percent_of_scaling/100)
            new_height = int(img.shape[0] * percent_of_scaling/100)

            new_dim = (new_width, new_height)
            new_dim = (img.shape[1], img.shape[0])
            resized_img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)

            wm_scale = 40
            wm_scale = 100
            wm_width = int(watermark.shape[1] * wm_scale/100)
            wm_height = int(watermark.shape[0] * wm_scale/100)
            wm_dim = (wm_width, wm_height)

            resized_wm = cv2.resize(watermark, wm_dim, interpolation=cv2.INTER_AREA)

            h_img, w_img, _ = resized_img.shape
            center_y = int(h_img/2)
            center_x = int(w_img/2)
            h_wm, w_wm, _ = resized_wm.shape
            top_y = center_y - int(h_wm/2)
            left_x = center_x - int(w_wm/2)
            bottom_y = top_y + h_wm
            right_x = left_x + w_wm

            roi = resized_img[top_y:bottom_y, left_x:right_x]
            result = cv2.addWeighted(roi, 1, resized_wm, 0.3, 0)
            resized_img[top_y:bottom_y, left_x:right_x] = result

    #         filename = 'E:/Meera/Watermark/output/Watermakred_Image.jpg'
            filename = 'C:/Watermark/Watermark/output/Watermakred_Image'+str(c)+'.jpg'
            c+=1
            print(filename)
            cv2.imwrite(filename, resized_img)
        
    #Display
    dir_path = r'C:/Watermark/Watermark/output/'
    disp_files=  []
    disp_files.clear()
    cnt = 0
    for path in os.listdir(dir_path):
#         print(os.path.join(dir_path, path))
        disp_files.append(os.path.join(dir_path, path))
    for f in disp_files:
        if cnt==1:
            break
        img=Image.open(f) # read the image file
#        print(f.split('/')[-1])
#        img.save(path+'img'+str(cnt)+'.jpg')
#        cnt+=1
        w,h = img.size
        scale = 50
        nw= int(w*(scale/100))
        nh = int(h*(scale/100))
        print(w,h,nw,nh)
        img=img.resize((nw,nh)) # new width & height
        img=ImageTk.PhotoImage(img)
        e1 =tk.Label(ctr_right)
        e1.grid(row=1,column=0)
        e1.image = img
        e1['image']=img 
        cnt+=1
    #print(disp_files)
    if len(disp_files)>1:
        n=len(disp_files)
        l_fin=tk.Label(ctr_right,text="There are {} more images saved in path C:/Watermark/Watermark/output/".format(n-1))
        l_fin.grid(row=2,column=0)
    else:
        l_fin['text']=""
        
#        if(col==3): 
#            row=row+1
#            col=1   
#        else:       
#            col=col+1
        
root.mainloop()






            
