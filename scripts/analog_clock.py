import math
import tkinter as tk
import time

my_w = tk.Tk()

width,height=620,620 
c_width,c_height=width-5,height-5 
d=str(width)+"x"+str(height)
my_w.geometry(d)
my_w.title("Analog Clock")
c1 = tk.Canvas(my_w, width=c_width, height=c_height,bg='black')
c1.grid(row=0,column=0,padx=5,pady=5,columnspan=3)
dial=c1.create_oval(10, 10, 600, 600,width=15,outline='orange',fill='#FFFFFF')
x,y=305,305 
x1,y1,x2,y2=x,y,x,10 
center=c1.create_oval(x-8,y-8,x+8,y+8,fill='#c0c0c0')
r1=280 
r2=210  
rs=210 
rm=180 
rh=160 
in_degree = 0
in_degree_s=int(time.strftime('%S')) *6 
in_degree_m=int(time.strftime('%M'))*6 
in_degree_h=int(time.strftime('%I')) * 30 
if(in_degree_h==360):
    in_degree_h=0 
h=iter(['12','1','2','3','4','5','6','7','8','9','10','11'])

for i in range(0,60):
    in_radian = math.radians(in_degree)
    if(i%5==0): 
        ratio=0.85 
        t1=x+r2*math.sin(in_radian) 
        t2=x-r2*math.cos(in_radian) 
        c1.create_text(t1,t2,fill='blue',font="Times 30  bold",text=next(h)) 
    else:
        ratio=0.9 
    
    x1=x+ratio*r1*math.sin(in_radian)
    y1=y-ratio*r1*math.cos(in_radian)
    x2=x+r1*math.sin(in_radian)
    y2=y-r1*math.cos(in_radian)
    c1.create_line(x1,y1,x2,y2,width=1) 
    in_degree=in_degree+6 
 
in_radian = math.radians(in_degree_s) 
x2=x+rs*math.sin(in_radian)
y2=y-rs*math.cos(in_radian)
second=c1.create_line(x,y,x2,y2,fill='red',width=2) 
def my_second():
    global in_degree_s,second
    in_radian = math.radians(in_degree_s)
    c1.delete(second) 
    x2=x+rs*math.sin(in_radian) 
    y2=y-rs*math.cos(in_radian) 
    second=c1.create_line(x,y,x2,y2,arrow='last',fill='red',width=2)
    if(in_degree_s>=360): 
        in_degree_s=0 
        my_minute()  
    in_degree_s=in_degree_s+6 
    c1.after(1000,my_second) 
 
in_radian = math.radians(in_degree_m)
x2=x+rm*math.sin(in_radian)
y2=y-rm*math.cos(in_radian) 
minute=c1.create_line(x,y,x2,y2,width=4,fill='green')
def my_minute():
    global in_degree_m,minute
    in_degree_m=in_degree_m+6  
    in_radian = math.radians(in_degree_m) 
    c1.delete(minute) 
    x2=x+rm*math.sin(in_radian) 
    y2=y-rm*math.cos(in_radian) 
    minute=c1.create_line(x,y,x2,y2,width=4,fill='green')
    my_hour() 
    if(in_degree_m>=360): 
        in_degree_m=0
 
in_degree_h=in_degree_h+(in_degree_m*0.0833333)          
in_radian = math.radians(in_degree_h)
x2=x+rh*math.sin(in_radian)
y2=y-rh*math.cos(in_radian)
hour=c1.create_line(x,y,x2,y2,width=6,fill='#a83e32')
def my_hour():
    global in_degree_h,hour
    in_degree_h=in_degree_h+0.5
    in_radian = math.radians(in_degree_h) 
    c1.delete(hour) 
    x2=x+rh*math.sin(in_radian) 
    y2=y-rh*math.cos(in_radian) 
    hour=c1.create_line(x,y,x2,y2,width=6,fill='#a83e32')
    if(in_degree_h>=360):
        in_degree_h=0

my_second() 
my_w.mainloop()
