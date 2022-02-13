# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 23:22:43 2022

@author: tonyp
"""

####
## Import libraries
####

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import local_PID as pid
import random as rnd

####
## GLOBAL VAR
####


fig = None
canv = None

pltmaxnum = 25
arrayXPlt = np.arange(0, pltmaxnum, 1, dtype=int)
arraySetpoint = np.zeros(pltmaxnum, dtype=int)
arrayInput = np.zeros(pltmaxnum, dtype=int)
arrayOutput = np.zeros(pltmaxnum, dtype=int)


statusSimul = FALSE
####
## Util function
####


def quit_FORM():
    this_windows.quit()
    this_windows.destroy()
    
####
## Util UI Elements
####


def update_value(staticText, value, lbloutput, tempRankFunc, withDecimals):
    newValue = 0
    if withDecimals == TRUE:
        newValue = f"{staticText}{float(value):.2f}"
        value = f"{float(value):.2f}"
    else:
        newValue = f"{staticText}{float(value):.0f}"
        value = f"{float(value):.0f}"
    lbloutput.config(text=newValue)
    tempRankFunc(value)

def invokeRanger(ParentContainer, staticText, minRange, maxRange, initValue, style, tempRankFunc, withDecimals):
    container = ttk.Frame(ParentContainer)
    
    if(withDecimals == TRUE):
        hdr = ttk.Label(container, text=f"{staticText}{float(initValue):.2f}", anchor="w")
    else:
        hdr = ttk.Label(container, text=f"{staticText}{float(initValue):.0f}", anchor="w")
    hdr.pack(side=TOP, fill=X, pady=10, anchor="w")
    
    scale = ttk.Scale(container, orient = HORIZONTAL, from_ = minRange, 
                  to = maxRange, value = initValue, 
                  command=lambda x=initValue: update_value(staticText, x, hdr, tempRankFunc, withDecimals),
                  bootstyle = style, length= 200)
    #scale.pack(side=LEFT, padx=15)
    scale.pack(fill=BOTH, side=LEFT)
    return container

def invokeButton(ParentContainer, staticText, style, tempBtnFunc):
    btn = ttk.Button(
                master=ParentContainer,
                text=staticText,
                width=10,
                bootstyle=style,
                command=tempBtnFunc,
            )
    return btn

def update_toggle(varValue, tempBtnFunc, parentControl):
    labelValue = ""
    if(varValue.get() == TRUE):
        labelValue = "ON"
    else:
        labelValue = "OFF"
    parentControl.config(text=labelValue)
    tempBtnFunc(varValue.get())

def invokeToggleButton(ParentContainer, staticText, style, tempBtnFunc):
    container = ttk.Frame(ParentContainer)
    
    tmplbl = ttk.Label(container, text=staticText, anchor=CENTER)
    tmplbl.pack(side=TOP, fill=X, pady=10, anchor="w")
    
    toogle_On_OFF = ttk.BooleanVar()
    toogle_On_OFF.set(True)
    toggleBtn = ttk.Checkbutton(master=container,
                                text="ON",
                                bootstyle=style,
                                width=10,
                                variable=toogle_On_OFF,
                                command=lambda x=toogle_On_OFF: update_toggle(x, tempBtnFunc, toggleBtn)
                                )
    toggleBtn.pack(fill=BOTH, side=LEFT, padx=15)
    return container


####
##  GLOBAL INTERFACE
####


def ui_change_Setpoint(value):
    print("Value:", value, type(value))
    objPID.setSetPoint(int(value))

def ui_change_Kp(value):
    objPID.setKp(float(value))
    #print("Value:", value, type(value))

def ui_change_Ki(value):
    objPID.setKi(float(value))
    #print("Value:", value, type(value))

def ui_change_Kd(value):
    objPID.setKd(float(value))
    #print("Value:", value, type(value))

#Buttons
def ui_change_Sampletime(value):
    objPID.SetSampleTime(int(value))
    #print("Value:", value, type(value))

def ui_click_start():
    global statusSimul
    if(not statusSimul):
        this_windows.after(100, plotter)
        statusSimul = TRUE
    print("start")

def ui_click_end():
    global statusSimul
    if(statusSimul):
        statusSimul = FALSE
    print("end")
    
def ui_click_reset():
    fig.clear()
    global arraySetpoint, arrayInput, arrayOutput
    arraySetpoint = np.zeros(pltmaxnum, dtype=int)
    arrayInput = np.zeros(pltmaxnum, dtype=int)
    arrayOutput = np.zeros(pltmaxnum, dtype=int)
    print("reset")
    
#toggle
def ui_click_change(value):
    if(value == TRUE):
        objPID.SetMode(pid.PID_DEFINITIONS_AUTOMATIC)
        print("ON")
    else:
        objPID.SetMode(pid.PID_DEFINITIONS_MANUAL)
        print("OFF")



def legos_RangeButtons(ParentContainer):
    container = ttk.Frame(ParentContainer)

    #SetPoint, Constantes Kp, Ki, Kd, Sample time.
    #SetPoint
    rangeSetPoint = invokeRanger(container, "Setpoint: ", -180, 180, 100, RangeStyle, ui_change_Setpoint, FALSE) 
    rangeSetPoint.pack(side=TOP, fill=X, padx=5)
    
    #Constantes Kp
    rangeKp = invokeRanger(container, "Kp  (proportional gain): ", 0, 5, 2, RangeStyle, ui_change_Kp, TRUE) 
    rangeKp.pack(side=TOP, fill=X, padx=5)
    #Constantes Ki
    rangeKi = invokeRanger(container, "Ki (integral gain): ", 0, 20, 0.5, RangeStyle, ui_change_Ki, TRUE) 
    rangeKi.pack(side=TOP, fill=X, padx=5)
    #Constantes Kd
    rangeKd = invokeRanger(container, "Kd (derivative gain): ", 0, 20, 2, RangeStyle, ui_change_Kd, TRUE) 
    rangeKd.pack(side=TOP, fill=X, padx=5)
    
    #Constantes Sample time.
    rangeSampletime = invokeRanger(container, "Sample time: ", 50, 1000, 100, RangeStyle, ui_change_Sampletime, FALSE) 
    rangeSampletime.pack(side=TOP, fill=X, padx=5, pady=(0, 15))
    
    container.pack(side=TOP, fill=Y, padx=10, pady=15, anchor="w")

def legos_btn(ParentContainer):
    container = ttk.Frame(ParentContainer)
    
    btnStart = invokeButton(container, "Inicio", "primary-outline", ui_click_start)
    btnStart.pack(side=TOP, fill=X, padx=5)
    
    btnEnd = invokeButton(container, "Fin", "secondary-outline", ui_click_end)
    btnEnd.pack(side=TOP, fill=X, padx=5)
    
    btnReset = invokeButton(container, "Reset", "danger-outline", ui_click_reset)
    btnReset.pack(side=TOP, fill=X, padx=5)
    
    container.pack(side=TOP, fill=X, padx=10, pady=15, anchor="w")
    
def legos_toggle(ParentContainer):
    container = ttk.Frame(ParentContainer)

    togglex = invokeToggleButton(container, "Controlador PID", "warning-round-toggle", ui_click_change)
    togglex.pack(side=TOP, fill=X, padx=5)
    
    container.pack(side=TOP, fill=X, padx=10, pady=15, anchor="w")

#def plotter(yvalues, graph, ax): 
#    while drwarPlot:
#        yvalues = np.random.uniform(low=0.5, high=13.3, size=(10,))
#        ax.cla() 
#        ax.grid() 
#        ax.plot(range(10), yvalues, marker='o', color='orange') 
#        graph.draw() 
#        time.sleep(10)
#        plt.pause(0.0001)   


def plotter():
    print("dibukar el nuevo plot :0")
    result = loop()
    print(result)
    #Setpoint, Input y Output.
    global arraySetpoint, arrayInput, arrayOutput, arrayXPlt
    #input, Output, setPoint
    arrayInput = np.delete(arrayInput, 1)
    arrayInput = np.append(arrayInput, result[0])
    
    arrayOutput = np.delete(arrayOutput, 1)
    arrayOutput = np.append(arrayOutput, result[1])
    
    arraySetpoint = np.delete(arraySetpoint, 1)
    arraySetpoint = np.append(arraySetpoint, result[2])
    
    fig.clear()
    plt = fig.add_subplot(111)
    #plt.plot(np.random.randint(1,10,5), np.random.randint(10,20,5), label = "Setpoint")
    #plt.plot(np.random.randint(1,10,5), np.random.randint(10,20,5), label = "Input")
    #plt.plot(np.random.randint(1,10,5), np.random.randint(10,20,5), label = "Output")
    plt.plot(arrayXPlt, arraySetpoint, label = "Setpoint")
    plt.plot(arrayXPlt, arrayInput, label = "Input")
    plt.plot(arrayXPlt, arrayOutput, label = "Output")
    plt.legend()
    canv.draw_idle()
    global statusSimul
    print("status sumul ----------------------------------------------------------:", statusSimul)
    if(statusSimul):
        this_windows.after(500, plotter)



def legos_output(ParentContainer):
    
    global canv
    global fig
        
    fig = plt.figure()
        
    canv = FigureCanvasTkAgg(fig, master = ParentContainer)
    canv.draw()
    get_widz = canv.get_tk_widget()
    get_widz.pack(side=TOP, fill=BOTH, expand=True)
    


#GLOBSL STYLE
RangeStyle = SUCCESS
#WINDOWS CONFIG
this_windows = ttk.Window(themename="superhero") #superhero journal minty
this_windows.protocol("WM_DELETE_WINDOW", quit_FORM)
this_windows.geometry("1250x650+5+5")
this_windows.title("PID Simulator")




########################
## Ajustes PID
########################

def fakeAnalogSignal():
    maxV = 5;
    minV = 0
    return rnd.uniform(minV, maxV)

def setup():
    #inicializar las variables a las que estamos vinculados
    input = fakeAnalogSignal();
    Setpoint = 100;
    objPID.setInput(input)
    objPID.setSetPoint(Setpoint)
    objPID.SetSampleTime(100)
    #encienda el PID
    objPID.SetMode(pid.PID_DEFINITIONS_AUTOMATIC)
    
def loop():
    print("------------------------------------")
    input = fakeAnalogSignal();
    print("señal entrada: ", input)
    objPID.setInput(input)
    flag = objPID.Compute();
    print("compute status: ", flag)
    Output = objPID.getOutPut()
    setPoint = objPID.getSetPoint()
    return (input, Output, setPoint)

def main():
    
   
    #CONFIG
    containerConfig = ttk.Frame(this_windows) #, bootstyle = "light"
    containerConfig.pack(side=LEFT, fill=Y, padx=5)
    
        
    main_title = ttk.Label(containerConfig, text = "Configuación", font = ("Cambria", 12))
    main_title.pack(side=TOP, fill=X)
    
    legos_btn(containerConfig)
    legos_toggle(containerConfig)
    legos_RangeButtons(containerConfig)
    
    
    #OUTPUT
    containerOutput = ttk.Frame(this_windows, bootstyle = "light") #
    containerOutput.pack(side=LEFT, fill=BOTH, expand=True, padx=5) 
    
    main_title = ttk.Label(containerOutput, text = "OutPut", font = ("Cambria", 12))
    main_title.pack(side=TOP, fill=X)

    legos_output(containerOutput)
    
    #PID
    global objPID
    myDirection = pid.PID_DEFINITIONS_DIRECT
    objPID = pid.ObjectPID(100, 2.00, 0.5, 2.00, myDirection)
    setup()
    
    #this_windows.after(2000, plotter)
    this_windows.mainloop()
    
    

# EJECUTAR MAIN
main()
