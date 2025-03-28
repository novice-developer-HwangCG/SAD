import tkinter as tk
import random

class ToggleSwitch(tk.Frame):
    def __init__(self, parent, var_name, app, on_image, off_image, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.app = app
        self.var_name = var_name
        self.is_on = getattr(app, var_name)

        self.on_image = on_image
        self.off_image = off_image

        self.label = tk.Label(self)
        self.label.pack()

        self.label.bind("<Button-1>", self.toggle_switch)
        self.update_switch()

    def toggle_switch(self, event=None):
        self.app.toggle(self.var_name, self, self.app.labels[self.app.small_rects.index(self)])
        self.update_switch()

    def update_switch(self):
        self.is_on = getattr(self.app, self.var_name)

        if self.is_on:
            self.label.config(image=self.on_image)
        else:
            self.label.config(image=self.off_image)

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEST SAD")
        self.root.geometry("800x440")
        self.root.resizable(False, False)
        
        self.signal_Data1 = []
        self.signal_Data2 = []
        self.signal_Data3 = []

        self.signal_value1 = 0
        self.signal_value2 = 0
        self.signal_value3 = 0
        
        self.ARM_1 = False
        self.ARM_2 = False
        self.ARM_3 = False
        self.DIAR = False
        self.FIRE = False

        self.ARM_3_toggle_interval = 50
        
        self.on_image = tk.PhotoImage(file="C:/code_img_folder/toggle_on.png")
        self.off_image = tk.PhotoImage(file="C:/code_img_folder/toggle_off.png")

        self.init_widgets()
        self.update_loop()

    def toggle(self, variable_name, widget, label, canvas=None, oval_id=None):
        if variable_name == "ARM_2" and not self.ARM_1:
            return
        elif variable_name == "ARM_3" and not self.ARM_2:
            return
        elif variable_name == "DIAR" and not self.ARM_3:
            return
        elif variable_name == "FIRE" and not self.DIAR:
            return

        current_state = getattr(self, variable_name)
        new_state = not current_state
        setattr(self, variable_name, new_state)

        if variable_name == "FIRE":
            if new_state:
                self.reset_all()
                self.root.after(1000, self.reset_fire)
            self.update_fire_status(label, canvas, oval_id, new_state)
            return

        if variable_name == "ARM_1":
            self.signal_value1 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data1, self.signal_value1)
        elif variable_name == "ARM_2":
            self.signal_value2 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data2, self.signal_value2)
        elif variable_name == "ARM_3":
            self.signal_value3 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data3, self.signal_value3)

        self.update_signals()
        self.update_signal_labels()

        status = "ON" if new_state else "OFF"
        label.config(text=f"{variable_name} = {status}")
        color = "green" if new_state else "red"

        if canvas and oval_id is not None:
            canvas.itemconfig(oval_id, fill=color)
        else:
            widget.update_switch()

    def reset_fire(self):       # FIRE 스위치 리셋
        self.FIRE = False
        self.update_fire_status(self.fire_label, self.circle_canvas, self.oval_id, self.FIRE)

    def update_fire_status(self, label, canvas, oval_id, new_state):        # FIRE 스위치 전환
        status = "ON" if new_state else "OFF"
        color = "green" if new_state else "red"
        label.config(text=f"FIRE = {status}")
        canvas.itemconfig(oval_id, fill=color)

    def reset_all(self):        # 모든 스위치 리셋
        self.ARM_1, self.ARM_2, self.ARM_3, self.DIAR = False, False, False, False
        for rect, lbl, var in zip(self.small_rects, self.labels, ["ARM_1", "ARM_2", "ARM_3", "DIAR"]):
            rect.update_switch()
            lbl.config(text=f"{var} = OFF")
        
        self.signal_value1 = 0
        self.signal_value2 = 0
        self.signal_value3 = 0
        
        self.update_signals()
        self.update_signal_labels()

    def update_signal_history(self, signal_list, new_signal_value):     # 신호 값 저장 및 업데이트
        signal_list.append(new_signal_value)
        if len(signal_list) > 10:
            signal_list.pop(0)

    def update_loop(self):                                              # 신호 값 반복
        self.signal_quick_low_high_data=[0,1]
        self.signal_delay_low_high_data=[0,0,1,1]

        if not self.ARM_1:
            self.update_signal_history(self.signal_Data1, 0)
        else:
            self.update_signal_history(self.signal_Data1, 1)
        if not self.ARM_2:
            self.update_signal_history(self.signal_Data2, 0)
        else:
            self.update_signal_history(self.signal_Data2, 1)
        if not self.ARM_3:
            self.update_signal_history(self.signal_Data3, 0)
        else:
            if self.ARM_3_toggle_interval == 20:
                for i in self.signal_quick_low_high_data:
                    self.update_signal_history(self.signal_Data3, i)
            elif self.ARM_3_toggle_interval == 50:
                for i in self.signal_delay_low_high_data:
                    self.update_signal_history(self.signal_Data3, i)
        
        self.update_signals()
        self.update_signal_labels()

        self.draw_Volt()

        self.root.after(100, self.update_loop)

    def init_widgets(self):
        # 큰 사각형 위치
        large_rect = tk.Frame(self.root, width=425, height=250, bg="white", relief="solid", bd=1)
        large_rect.place(x=60, y=25)

        self.canvas_inside_large = tk.Canvas(large_rect, width=400, height=250, bg="white")
        self.canvas_inside_large.pack()
        self.canvas_inside_large.create_line(0, 125, 405, 125, fill="black", width=2)

        Vol_val = ["+15V", "+10V", " +5V", "  0V", " -5V", "-10V", "-15V"]
        Vol_y_pos = [20, 60, 100, 140, 180, 220, 262]
        for name, y in zip(Vol_val, Vol_y_pos):
            Vol_label = tk.Label(self.root, text=name)
            Vol_label.place(x=20, y=y)
        
        # 중간 사각형 위치
        medium_rect = tk.Frame(self.root, width=200, height=210, bg="white", relief="solid", bd=1)
        medium_rect.place(x=530, y=25)

        self.canvas_inside_medium = tk.Canvas(medium_rect, width=200, height=210, bg="white")
        self.canvas_inside_medium.pack()

        ARM_num = ["ARM_1", "ARM_2", "ARM_3"]
        ARM_y_pos = [55, 125, 195]
        for name, y in zip(ARM_num, ARM_y_pos):
            ARM_label = tk.Label(self.root, text=name)
            ARM_label.place(x=480, y=y)

        self.signal_labels = []
        signal_y_pos = [55, 125]
        for y in signal_y_pos:
            signal_label = tk.Label(self.root, text="LOW")
            signal_label.place(x=745, y=y)
            self.signal_labels.append(signal_label)

        # 작은 사각형 위치
        self.small_rects = []
        self.labels = []

        for i, var_name in enumerate(["ARM_1", "ARM_2", "ARM_3", "DIAR"]): 
            toggle_switch = ToggleSwitch(self.root, var_name, self, self.on_image, self.off_image)
            toggle_switch.place(x=40 + i * 125, y=300)
            self.small_rects.append(toggle_switch)

            label = tk.Label(self.root, text=f"{var_name} = OFF")
            label.place(x=35 + i * 125, y=405)
            self.labels.append(label)

        # ARM_3 순발, 지연 버튼
        self.fuze_var = tk.StringVar(value="50ms")  # 초기 값 설정

        Fuze_Quick = tk.Radiobutton(self.root, text="Quick", variable=self.fuze_var, value="20ms", command=self.update_fuze_mode)
        Fuze_Quick.place(x=355, y=315)

        Delay_Fuze = tk.Radiobutton(self.root, text="Delay", variable=self.fuze_var, value="50ms", command=self.update_fuze_mode)
        Delay_Fuze.place(x=355, y=365)

        # FIRE 버튼 위치
        self.circle_canvas = tk.Canvas(self.root, width=100, height=100)
        self.circle_canvas.place(x=550, y=300)

        self.oval_id = self.circle_canvas.create_oval(10, 10, 90, 90, fill="red", outline="black", width=2)

        self.fire_label = tk.Label(self.root, text="FIRE = OFF")
        self.fire_label.place(x=567, y=405)

        self.circle_canvas.bind("<Button-1>", lambda e: self.toggle("FIRE", None, self.fire_label, canvas=self.circle_canvas, oval_id=self.oval_id))

    def update_fuze_mode(self):                     # ARM_3 순발, 지연 선택
        selected_fuze = self.fuze_var.get()
        if selected_fuze == "20ms":
            self.ARM_3_toggle_interval = 20
        elif selected_fuze == "50ms":
            self.ARM_3_toggle_interval = 50

    def update_signals(self):                       # 디지털 신호 그래프 선그리기
        self.canvas_inside_medium.delete("all")
        self.canvas_inside_medium.create_line(0, 71, 205, 71, fill="black", width=2)
        self.canvas_inside_medium.create_line(0, 141, 205, 141, fill="black", width=2)

        self.draw_signal(self.signal_Data1, y_high=10, y_low=60)
        self.draw_signal(self.signal_Data2, y_high=80, y_low=130)
        self.draw_signal(self.signal_Data3, y_high=150, y_low=200)

    def update_signal_labels(self):                 # 텍스트 라벨 전환
        self.signal_labels[0].config(text="HIGH" if self.signal_value1 == 1 else "LOW")
        self.signal_labels[1].config(text="HIGH" if self.signal_value2 == 1 else "LOW")

    def draw_signal(self, signal_data, y_high, y_low):              # 디지털 신호 선 그리기
        if len(signal_data) == 0:
            return
        
        step = 220 / len(signal_data)       # 각 데이터 포인트를 x축 상에 균등하게 분포시키기 위해 사용, 220 = x축의 총 길이 -> 각 데이터 포인트는 220/10 = 22 만큼의 x축 간격을 가짐
        for i in range(len(signal_data) - 1):
            x1 = i * step
            x2 = (i + 1) * step

            y1 = y_high if signal_data[i] == 1 else y_low
            y2 = y_high if signal_data[i + 1] == 1 else y_low

            self.canvas_inside_medium.create_line(x1, y1, x2, y1, fill="blue", width=2)
            self.canvas_inside_medium.create_line(x2, y1, x2, y2, fill="blue", width=2)

    def draw_Volt(self):
        #sbc에 부착된 pico가 sbc가 받는 전압 Volt 값을 adc 값으로 전환, 전환된 adc 값을 다시 젯슨 나노로 전달하여 큰 사각형에 해당 값 그래프 그리기(연속으로 받아 그려야함)
        self.canvas_inside_large.delete("volt_graph")
        volt_values = [random.uniform(-12, 12) for _ in range(50)]

        for i in range(len(volt_values) - 1):
            x1 = i * 8
            y1 = 125 - volt_values[i] * 9
            x2 = (i + 1) * 8
            y2 = 125 - volt_values[i + 1] * 9

            self.canvas_inside_large.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="volt_graph")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
