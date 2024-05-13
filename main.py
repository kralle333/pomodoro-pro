import tkinter
from tkinter import ttk

import random
import sv_ttk
import json
import os.path
from playsound import playsound
from notifypy import Notify

settings_file_name = "settings.json"

root = tkinter.Tk()

frame = ttk.Frame(master=root, width=200, height= 20)
frame.pack(fill=tkinter.BOTH, side=tkinter.LEFT)
sv_ttk.set_theme("dark")

# Constants
pomodoro_length_seconds = 60.0*25.0
break_length_seconds =  60.0*5.0
motivational_stuff = []
breaks_needed_for_long_break = 4
long_break_multiplier = 0.15
motivational_time_seconds = 60
length_of_break = 0

state = "ready_to_start"
motivational_stuff_index = -1
breaks_taken = 0
total_pomodoro_time_used = 0

timer = pomodoro_length_seconds

if not os.path.isfile(settings_file_name):
    save_data = {
            "pomodoro_length_seconds": 60*25,
            "break_length_seconds": 60*5.0,
            "long_break_multiplier":0.15,
            "breaks_needed_for_long_break":4,
            "motivational_stuff": ["You can do it!","Keep going","U bravo","🍅", "Time to focus!"],
            "motivational_time_seconds": 60,
            "time_for_break_sound":"meow.mp3",
            "breaks_over_sound":"ring.mp3",
            "notification_icon":"tomato.png"
            }
    with open(settings_file_name,"w") as outfile:
        json.dump(save_data,outfile, indent=2)

save_data = json.loads(open(settings_file_name,"r").read())
pomodoro_length_seconds = save_data["pomodoro_length_seconds"]
break_length_seconds = save_data["break_length_seconds"]
long_break_multiplier = save_data["long_break_multiplier"]
breaks_needed_for_long_break = save_data["breaks_needed_for_long_break"]
motivational_stuff = save_data["motivational_stuff"]
motivational_time_seconds = save_data["motivational_time_seconds"]
time_for_break_sound  = save_data["time_for_break_sound"]
breaks_over_sound = save_data["breaks_over_sound"]
notification_icon = save_data["notification_icon"]
timer = pomodoro_length_seconds



def pretty_time(seconds):
    if(seconds < 60):
        return f'{int(seconds)}s'
    if(seconds < 60*60):
        seconds_left = seconds % 60
        minutes = seconds // 60  
        return f'{int(minutes)}m {int(seconds_left)}s'
    if (seconds < 60*60*24):
        seconds_left = seconds % 60
        minutes_left = int((seconds % 3600) / 60)
        hours =  int((seconds) / 3600)
        return f'{int(hours)}h {int(minutes_left)}m {int(seconds_left)}s'   
    return ""

def set_motivational():
    global motivational_stuff_index
    new_index = random.randint(0,len(motivational_stuff)-1)
    if new_index == motivational_stuff_index:
        set_motivational()
        return
    new_quote = motivational_stuff[new_index]
    motivational_stuff_index = new_index
    motivationalL.configure(text=new_quote)

def set_ui_state(new_state):
    if new_state == "breaks_over":
        timerL.configure(text="Time's up!")
        # timerL.configure(text="")
        motivationalL.configure(text="")
        button.configure(text="Start 🍅")
    if new_state == "ready_to_start":
        button.configure(text="Start 🍅")
        motivationalL.configure(text="")
        timerL.configure(text=pretty_time(timer))
        break_button.grid_forget()
        reset_button.grid_forget()
    if new_state == "running":
        timerL.configure(fg='white')
        timerL.configure(text=pretty_time(timer))
        break_button.grid(row = 0,column=2, padx=10,pady=10)
        reset_button.grid(row=0,column=1, padx=10,pady=10)
        motivationalL.configure(text =f'')
        button.configure(text="Pause")
        set_motivational()

def toggle_timer(_):
    global state
    global timer
    if(state == "running"):
        button.configure(text="Resume")
        state = "stopped"
    elif (state == "stopped"):
        button.configure(text="Pause")
        state = "running"
    elif (state == "break"):
        resume_from_break_early()
    elif state == "overtime":
        button.configure(text="Resume")
        state = "stopped_overtime"
    elif state == "stopped_overtime":
        button.configure(text="Pause")
        state = "overtime"
    elif(state == "breaks_over"):
        timer = pomodoro_length_seconds
        state = "running"
        set_ui_state(state)
    elif state == "ready_to_start":
        state = "running"
        set_ui_state(state)

def take_break(_):
    global timer
    global state
    global break_button
    global total_pomodoro_time_used
    global breaks_taken
    global length_of_break

    breaks_taken += 1
    if breaks_taken == breaks_needed_for_long_break:
        timer = long_break_multiplier * total_pomodoro_time_used
        breaks_taken = -1
        total_pomodoro_time_used = 0
        motivationalL.configure(text =f'Enjoy long break!')
    else:
        if state == "overtime": # add normal break length + over time
            timer = timer/pomodoro_length_seconds + break_length_seconds
        elif state == "running": # early break
            time_spent = pomodoro_length_seconds-timer
            #print(f'time spent {time_spent}')
            timer = (time_spent/pomodoro_length_seconds)*break_length_seconds
        motivationalL.configure(text =f'Enjoy short break!')
    
    length_of_break=timer
    state = "break"
    timerL.configure(text= pretty_time(timer) ,fg="white")
    break_button.grid_forget()
    reset_button.grid_forget()
    button.configure(text="End break early")

def resume_from_break_early():
    global state
    global timer
    if state != "break":
        return
    
    state = "running"
    timeSpentInBreak = length_of_break-timer
    #print(f'time spent in break: {timeSpentInBreak}')
    fractionsOfBreaks = timeSpentInBreak/break_length_seconds
    #print(f'franctions of breaks {fractionsOfBreaks}')
    toPomoTime = fractionsOfBreaks*pomodoro_length_seconds
    #print(f'to Pomo Time {toPomoTime}')
    timer = pomodoro_length_seconds - toPomoTime
    timerL.configure(text=pretty_time(timer))
    break_button.grid(row = 0,column=2, padx=10,pady=10)
    break_button.configure(text="Take early break", bg ="orange")
    reset_button.grid(row = 0,column=1, padx=10,pady=10)
    button.configure(text="Pause")
    set_motivational()
    motivationalL.configure(text =f'')


def update_timer():
    global timer
    global run
    global state
    global total_pomodoro_time_used
    frame.after(1000, update_timer)
    # longBreakTimeL.configure(text=f'Breaks taken: {breaks_taken} Long break time: {pretty_time((total_pomodoro_time_used)*0.15)}')
    if state == "running":
        timer -= 1
        total_pomodoro_time_used += 1
        timerL.configure(text=pretty_time(timer))
        if timer % motivational_time_seconds == 0:
            set_motivational()
        if timer <=0:
            state = "overtime"
            playsound(time_for_break_sound)

            notification = Notify()
            notification.title = "Time's up!"
            notification.message = "Take your short break" if breaks_taken+1 % breaks_needed_for_long_break != 0 else "Take your long break"
            notification.icon= notification_icon
            notification.send()

            motivationalL.configure(text= "bonus time")
            break_button.configure(text="Take break", bg ="green")
            timerL.configure(fg='green')
            #motivationalL.configure(text=f'Break length: {pretty_time(calculate_break_size())}')
    elif state == "stopped":
        pass
    elif state == "overtime":
        timer += 1
        total_pomodoro_time_used += 1
        timerL.configure(text=f'+{pretty_time(timer)}')
    elif state == "break":
        timer -=1
        if timer <=0:
            timer = 0
            state = "breaks_over"
            playsound(breaks_over_sound)
            
            notification = Notify()
            notification.title = "Break's over!"
            notification.message = "Get ready for next 🍅"
            notification.icon= notification_icon
            notification.send()

            set_ui_state(state)
        else:
            timerL.configure(text=pretty_time(timer))

def reset_timer(_):
    global state
    global timer
    timer = pomodoro_length_seconds
    state = "ready_to_start"
    set_ui_state(state)

 ### SETUP UI

timeFrame = tkinter.Frame(master=frame, width = 200, height = 200)
timeFrame.pack()

timerL = tkinter.Label(timeFrame, text=pretty_time(timer), font=("Abeezee",66),width=8,pady=10)
timerL.grid(row = 1,column=0)

motivationalL = tkinter.Label(timeFrame,text="",font=("Abeezee",18), fg="green",height=0,pady=10)
motivationalL.grid(row = 2,column=0)

buttons_frame =tkinter.Frame(master= frame,width = 200,height=20)
buttons_frame.pack()
button = tkinter.Button(buttons_frame, text="Start 🍅")
button.bind("<Button-1>",toggle_timer)
button.grid(row=0, column=0,padx=10,pady=10)

break_button = tkinter.Button(buttons_frame,text="Take early break", bg="orange")
break_button.bind("<Button-1>",take_break)
# break_button.grid(row=0,column=2, padx=10,pady=10)

reset_button = tkinter.Button(buttons_frame,text="Reset")
reset_button.bind("<Button-1>",reset_timer)
# reset_button.grid(row=0,column=1, padx=10,pady=10)

 ### END SETUP UI


root.after(1000,update_timer)
root.mainloop()
