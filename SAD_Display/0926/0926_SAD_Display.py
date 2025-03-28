import tkinter as tk
import serial

ser = serial.Serial('/dev/ttyTHS1', 115200, timeout=1)

class ToggleSwitch(tk.Frame):
    def __init__(self, parent, var_name, app, on_image, off_image, label, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.app = app
        self.var_name = var_name
        self.is_on = getattr(app, var_name)

        self.on_image = on_image
        self.off_image = off_image

        self.label = label  # Store the label reference

        self.label_widget = tk.Label(self, image=self.off_image)
        self.label_widget.pack()

        self.label.bind("<Button-1>", self.toggle_switch)
        self.update_switch()

    def toggle_switch(self, event=None):
        # 스위치 전환 후 업데이트
        self.app.toggle(self.var_name, self, self.label)
        self.update_switch()

    def update_switch(self):
        self.is_on = getattr(self.app, self.var_name)

        if self.is_on:
            self.label_widget.config(image=self.on_image)
        else:
            self.label_widget.config(image=self.off_image)

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TEST SAD")
        self.root.geometry("1855x1030")
        self.root.resizable(False, False)
        
        self.volt_values = []  # 전압 값을 저장할 리스트
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
        
        # 이미지 로드
        try:
            self.on_image = tk.PhotoImage(file="C:/code_img_folder/toggle_on2.png")
            self.off_image = tk.PhotoImage(file="C:/code_img_folder/toggle_off2.png")
            self.diar_on_image = tk.PhotoImage(file="C:/code_img_folder/diar_sw1.png")
            self.diar_off_image = tk.PhotoImage(file="C:/code_img_folder/diar_sw2.png")
        except tk.TclError:
            # 이미지 로드 실패 시 공백 이미지 출력
            self.on_image = tk.PhotoImage()
            self.off_image = tk.PhotoImage()
            self.diar_on_image = tk.PhotoImage()
            self.diar_off_image = tk.PhotoImage()

        self.init_widgets()
        self.update_loop()

    def toggle(self, variable_name, widget, label):
        # 각 버튼에 대한 의존성을 처리 (다음 버튼이 켜져 있는지 확인)
        if variable_name == "ARM_2" and not self.ARM_1:
            return
        elif variable_name == "ARM_3" and not self.ARM_2:
            return
        elif variable_name == "FIRE" and not self.ARM_3:
            return
        elif variable_name == "DIAR" and not self.FIRE:
            return

        # 현재 상태 확인
        current_state = getattr(self, variable_name)
        new_state = not current_state

        # 버튼을 끌 때 다음 버튼이 켜져 있으면 꺼지지 않도록 함
        if not new_state:
            if variable_name == "ARM_1" and self.ARM_2:
                return
            elif variable_name == "ARM_2" and self.ARM_3:
                return
            elif variable_name == "ARM_3" and self.FIRE:
                return
            elif variable_name == "FIRE" and self.DIAR:
                return

        # 상태 업데이트
        setattr(self, variable_name, new_state)

        # 상태 업데이트
        setattr(self, variable_name, new_state)

        # DIAR 처리
        if variable_name == "DIAR":
            if new_state:
                self.reset_all()
                self.root.after(1000, self.reset_diar)
            self.update_diar_status(self.DIAR_label, new_state)
            return

        # 신호 업데이트 (ARM_1, ARM_2, ARM_3)
        self.update_signal(variable_name, new_state)
        self.update_signals()
        self.update_signal_labels()

        # 상태 표시
        status = "ON" if new_state else "OFF"
        label.config(text=f"{variable_name} = {status}")

    def reset_diar(self):  # DIAR 스위치 리셋
        self.DIAR = False
        self.update_diar_status(self.DIAR_label, self.DIAR)
        self.toggle_diar_widget.update_switch()

    def update_diar_status(self, label, new_state):  # DIAR 스위치 전환
        status = "ON" if new_state else "OFF"
        label.config(text=f"DIAR = {status}")

    def reset_all(self):        # 모든 스위치 리셋
        self.ARM_1, self.ARM_2, self.ARM_3, self.FIRE = False, False, False, False
        for rect, lbl, var in zip(self.small_rects, self.labels, ["ARM_1", "ARM_2", "ARM_3", "FIRE"]):
            rect.update_switch()
            lbl.config(text=f"{var} = OFF")
        
        self.signal_value1 = 0
        self.signal_value2 = 0
        self.signal_value3 = 0
        
        self.update_signals()
        self.update_signal_labels()

    def update_signal(self, variable_name, new_state):      # 디지털 신호 그래프 값 및 상태 업데이트
        if variable_name == "ARM_1":
            self.signal_value1 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data1, self.signal_value1)
        elif variable_name == "ARM_2":
            self.signal_value2 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data2, self.signal_value2)
        elif variable_name == "ARM_3":
            self.signal_value3 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data3, self.signal_value3)

    def update_signal_history(self, signal_list, new_signal_value):     # 신호 값 저장 및 업데이트
        signal_list.append(new_signal_value)
        if len(signal_list) > 10:
            signal_list.pop(0)

    def update_loop(self):  # 신호 값 반복
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
            self.update_signal_arm_3()

        self.update_signals()
        self.update_signal_labels()

        self.draw_Volt()
        # 100ms 마다 갱신
        self.root.after(100, self.update_loop)

    def update_signal_arm_3(self):          # ARM_3 순발, 지연 신호 값 업데이트
        quick_data = [0, 1]
        delay_data = [0, 0, 1, 1]
        if self.ARM_3_toggle_interval == 20:
            for i in quick_data:
                self.update_signal_history(self.signal_Data3, i)
        elif self.ARM_3_toggle_interval == 50:
            for i in delay_data:
                self.update_signal_history(self.signal_Data3, i)

    def init_widgets(self):
        # UI 위젯 초기화
        # ADC 값 그래프
        large_rect = tk.Frame(self.root, width=1140, height=650, bg="white", relief="solid", bd=1)
        large_rect.place(x=60, y=25)

        self.canvas_inside_large = tk.Canvas(large_rect, width=1140, height=650, bg="white")
        self.canvas_inside_large.pack()
        self.canvas_inside_large.create_line(0, 325, 1145, 325, fill="black", width=2)

        Vol_val = ["+15V", "+10V", " +5V", "  0V", " -5V", "-10V", "-15V"]
        Vol_y_pos = [22, 120, 230, 340, 450, 560, 660]
        for name, y in zip(Vol_val, Vol_y_pos):
            Vol_label = tk.Label(self.root, text=name, font=("Helvetica", 12))
            Vol_label.place(x=10, y=y)

        self.voltage_label = tk.Label(self.root, text="ADC Voltage: N/A", font=("Helvetica", 30), bg='white')
        self.voltage_label.place(x=1375, y=600)

        # 디지털 신호 그래프
        medium_rect = tk.Frame(self.root, width=475, height=510, bg="white", relief="solid", bd=1)
        medium_rect.place(x=1300, y=25)

        self.canvas_inside_medium = tk.Canvas(medium_rect, width=475, height=510, bg="white")
        self.canvas_inside_medium.pack()

        ARM_num = ["ARM_1", "ARM_2", "ARM_3"]
        ARM_y_pos = [105, 265, 435]
        for name, y in zip(ARM_num, ARM_y_pos):
            ARM_label = tk.Label(self.root, text=name, font=("Helvetica", 16))
            ARM_label.place(x=1220, y=y)

        self.signal_labels = []
        signal_y_pos = [105, 265]
        for y in signal_y_pos:
            signal_label = tk.Label(self.root, text="LOW", font=("Helvetica", 16))
            signal_label.place(x=1790, y=y)
            self.signal_labels.append(signal_label)

        # 작은 사각형 위치
        self.small_rects = []
        self.labels = []

        x_start = 50  # 버튼 UI 처음 x 좌표
        gap_280 = 280  # ARM_1, ARM_2, ARM_3 사이의 간격
        gap_360 = 360  # ARM_3와 DIAR 사이의 간격

        for i, var_name in enumerate(["ARM_1", "ARM_2", "ARM_3", "FIRE"]): 
            if i < 3:  # ARM_1, ARM_2, ARM_3
                x_position = x_start + i * gap_280
            else:  # DIAR
                x_position = x_start + 2 * gap_280 + gap_360

            label = tk.Label(self.root, text=f"{var_name} = OFF", font=("Arial", 18))
            label.place(x=x_position + 7, y=975)
            self.labels.append(label)

            toggle_switch = ToggleSwitch(self.root, var_name, self, self.on_image, self.off_image, label)
            toggle_switch.place(x=x_position, y=700)
            self.small_rects.append(toggle_switch)

        # ARM_3 순발, 지연 버튼
        self.fuze_var = tk.StringVar(value="50ms")  # 초기 값 설정

        canvas1 = tk.Canvas(self.root, width=150, height=100)
        canvas1.place(x=790, y=735)
        canvas1.create_rectangle(10, 10, 150, 90, outline="black", width=1)

        Fuze_Quick = tk.Radiobutton(self.root, text="Quick", variable=self.fuze_var, value="20ms", command=self.update_fuze_mode, font=("Arial", 18))
        Fuze_Quick.place(x=820, y=765)

        canvas2 = tk.Canvas(self.root, width=150, height=100)
        canvas2.place(x=790, y=855)
        canvas2.create_rectangle(10, 10, 150, 90, outline="black", width=1)

        Delay_Fuze = tk.Radiobutton(self.root, text="Delay", variable=self.fuze_var, value="50ms", command=self.update_fuze_mode, font=("Arial", 18))
        Delay_Fuze.place(x=820, y=885)

        # DIAR 버튼 위치
        self.DIAR_label = tk.Label(self.root, text="DIAR = OFF", font=("Arial", 18))
        self.DIAR_label.place(x=1320, y=975)

        self.toggle_diar_widget = ToggleSwitch(self.root, "DIAR", self, self.diar_on_image, self.diar_off_image, self.DIAR_label)
        self.toggle_diar_widget.place(x=1325, y=700)
        self.small_rects.append(self.toggle_diar_widget)

    def update_fuze_mode(self):                     # ARM_3 순발, 지연 선택
        selected_fuze = self.fuze_var.get()
        if selected_fuze == "20ms":
            self.ARM_3_toggle_interval = 20
        elif selected_fuze == "50ms":
            self.ARM_3_toggle_interval = 50

    def update_signals(self):                       # 디지털 신호 그래프 선그리기
        self.canvas_inside_medium.delete("all")
        self.canvas_inside_medium.create_line(0, 171, 475, 171, fill="black", width=2)
        self.canvas_inside_medium.create_line(0, 341, 475, 341, fill="black", width=2)

        self.draw_signal(self.signal_Data1, y_high=10, y_low=160)
        self.draw_signal(self.signal_Data2, y_high=180, y_low=330)
        self.draw_signal(self.signal_Data3, y_high=350, y_low=503)

    def update_signal_labels(self):                 # 텍스트 라벨 전환
        self.signal_labels[0].config(text="HIGH" if self.signal_value1 == 1 else "LOW")
        self.signal_labels[1].config(text="HIGH" if self.signal_value2 == 1 else "LOW")

    def draw_signal(self, signal_data, y_high, y_low):              # 디지털 신호 선 그리기
        if len(signal_data) == 0:
            return
        
        step = 530 / len(signal_data)       # 각 데이터 포인트를 x축 상에 균등하게 분포시키기 위해 사용, 220 = x축의 총 길이 -> 각 데이터 포인트는 220/10 = 22 만큼의 x축 간격을 가짐
        for i in range(len(signal_data) - 1):
            x1 = i * step
            x2 = (i + 1) * step

            y1 = y_high if signal_data[i] == 1 else y_low
            y2 = y_high if signal_data[i + 1] == 1 else y_low

            self.canvas_inside_medium.create_line(x1, y1, x2, y1, fill="blue", width=2)
            self.canvas_inside_medium.create_line(x2, y1, x2, y2, fill="blue", width=2)

    def draw_Volt(self):
        self.canvas_inside_large.delete("volt_graph")  # 이전 그래프 삭제

        # 시리얼 데이터 읽기
        if ser.in_waiting > 0:
            try:
                data = ser.readline().decode('utf-8').strip()  # 시리얼에서 데이터를 읽음
                voltage = float(data)  # 받은 데이터를 전압 값으로 변환
                self.volt_values.append(voltage)  # 전압 값 리스트에 추가

                # 50개의 값을 유지하며 오래된 값을 삭제
                if len(self.volt_values) > 50:
                    self.volt_values.pop(0)

                # ADC 전압 값을 라벨에 업데이트
                self.voltage_label.config(text=f"ADC Voltage: {voltage:.2f} V")

            except ValueError:
                print("Invalid data received")

        # 전압 값을 그래프로 그림 
        for i in range(len(self.volt_values) - 1):
            x1 = i * 10
            y1 = 325 - self.volt_values[i] * 10
            x2 = (i + 1) * 10
            y2 = 325 - self.volt_values[i + 1] * 10

            self.canvas_inside_large.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="volt_graph")


if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
