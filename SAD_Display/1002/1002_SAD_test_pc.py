import tkinter as tk
import serial
import time

# ser = serial.Serial('/dev/ttyTHS1', 115200, timeout=1)

class ImageToggleButton(tk.Frame):
    # 버튼 상태 공통 관리를 위해 클래스 변수로 선언
    ARM_1 = False
    ARM_2 = False
    ARM_3 = False
    FIRE = False

    def __init__(self, root, on_image_path, off_image_path, variable_name, label, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.variable_name = variable_name
        self.label = label

        self.on_image = tk.PhotoImage(file=on_image_path)
        self.off_image = tk.PhotoImage(file=off_image_path)

        self.button = tk.Button(self, image=self.off_image, command=self.toggle)
        self.button.pack()

    def toggle(self):
        # 버튼 제어 로직 (예시. ARM_1이 OFF이면 ARM_2는 ON 되지 않음)
        if self.variable_name == "ARM_2" and not ImageToggleButton.ARM_1:
            return
        elif self.variable_name == "ARM_3" and not ImageToggleButton.ARM_2:
            return
        elif self.variable_name == "FIRE" and not ImageToggleButton.ARM_3:
            return

        # ARM_1 제어 로직
        if self.variable_name == "ARM_1":
            ImageToggleButton.ARM_1 = not ImageToggleButton.ARM_1
            try:
                if ImageToggleButton.ARM_1:
                    # ser.write(b'1')
                    print("Sent '1' to Pico")
                    self.button.config(image=self.on_image)
                else:
                    # ser.write(b'0')
                    print("Sent '0' to Pico")
                    self.button.config(image=self.off_image)
                # ser.flush()
            except serial.SerialException as e:
                print(f"Failed to send data to Pico: {e}")
            return

        # 버튼들 상태 전환 및 제어 로직
        current_status = not getattr(ImageToggleButton, self.variable_name)
        setattr(ImageToggleButton, self.variable_name, current_status)

        if current_status:
            self.button.config(image=self.on_image)
        else:
            self.button.config(image=self.off_image)

        signal_graph.update_signal(self.variable_name, current_status)

        status = "ON" if current_status else "OFF"
        self.label.config(text=f"{self.variable_name} = {status}")

# 각 버튼에 상태에 대한 신호 그래프 그리기 클래스
class Signal_data(tk.Frame):
    def __init__(self, root, canvas, signal_labels, fuze_var):
        super().__init__(root)
        self.root = root  # root 객체를 받아서 이후 after() 메서드에 사용
        self.canvas = canvas
        self.signal_labels = signal_labels
        self.fuze_var = fuze_var

        self.signal_Data1 = []
        self.signal_Data2 = []
        self.signal_Data3 = []

        self.signal_value1 = 0
        self.signal_value2 = 0
        self.signal_value3 = 0

        self.ARM_3_toggle_interval = 50

    def update_signal(self, variable_name, new_state):
        if variable_name == "ARM_1":
            self.signal_value1 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data1, self.signal_value1)
        elif variable_name == "ARM_2":
            self.signal_value2 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data2, self.signal_value2)
        elif variable_name == "ARM_3":
            self.signal_value3 = 1 if new_state else 0
            self.update_signal_history(self.signal_Data3, self.signal_value3)
        
        # 신호 그래프와 라벨 업데이트
        self.update_graph()
        self.update_signal_labels()

    def update_fuze_mode(self):
        selected_fuze = self.fuze_var.get()
        if selected_fuze == "20ms":
            self.ARM_3_toggle_interval = 20
        elif selected_fuze == "50ms":
            self.ARM_3_toggle_interval = 50
    
    def update_signal_history(self, signal_list, new_signal_value):  # 신호 값 저장 및 업데이트
        signal_list.append(new_signal_value)
        if len(signal_list) > 10:
            signal_list.pop(0)

    def update_loop(self):
        # ARM 버튼 상태 확인 및 신호 업데이트
        if not ImageToggleButton.ARM_1:
            self.update_signal_history(self.signal_Data1, 0)
        else:
            self.update_signal_history(self.signal_Data1, 1)

        if not ImageToggleButton.ARM_2:
            self.update_signal_history(self.signal_Data2, 0)
        else:
            self.update_signal_history(self.signal_Data2, 1)

        if not ImageToggleButton.ARM_3:
            self.update_signal_history(self.signal_Data3, 0)
        else:
            self.update_signal_arm_3()

        # 그래프 및 라벨 갱신
        self.update_graph()
        self.update_signal_labels()

        # 100ms 후에 다시 루프 실행 (비동기적으로)
        self.root.after(100, self.update_loop)

    def update_fuze_mode(self):  # ARM_3 순발, 지연 선택
        selected_fuze = self.fuze_var.get()
        if selected_fuze == "20ms":
            self.ARM_3_toggle_interval = 20
        elif selected_fuze == "50ms":
            self.ARM_3_toggle_interval = 50

    def update_signal_arm_3(self):          # ARM_3 순발, 지연 신호 값 업데이트
        quick_data = [0, 1]
        delay_data = [0, 0, 1, 1]
        if self.ARM_3_toggle_interval == 20:
            for i in quick_data:
                self.update_signal_history(self.signal_Data3, i)
        elif self.ARM_3_toggle_interval == 50:
            for i in delay_data:
                self.update_signal_history(self.signal_Data3, i)

    def update_signal_labels(self):
        # 상태에 따라 텍스트 라벨 업데이트
        self.signal_labels[0].config(text="HIGH" if self.signal_value1 == 1 else "LOW")
        self.signal_labels[1].config(text="HIGH" if self.signal_value2 == 1 else "LOW")
        self.signal_labels[2].config(text="HIGH" if self.signal_value3 == 1 else "LOW")

    def update_graph(self):
        self.canvas.delete("all")
        canvas_inside_medium.create_line(0, 126, 350, 126, fill="black", width=2)
        canvas_inside_medium.create_line(0, 251, 350, 251, fill="black", width=2)

        self.draw_signal(self.signal_Data1, y_high=15, y_low=110)
        self.draw_signal(self.signal_Data2, y_high=140, y_low=235)
        self.draw_signal(self.signal_Data3, y_high=265, y_low=360)

    def draw_signal(self, signal_data, y_high, y_low):
        if len(signal_data) == 0:
            return
        
        step = 390 / len(signal_data)
        for i in range(len(signal_data) - 1):
            x1 = i * step
            x2 = (i + 1) * step

            y1 = y_high if signal_data[i] == 1 else y_low
            y2 = y_high if signal_data[i + 1] == 1 else y_low

            self.canvas.create_line(x1, y1, x2, y1, fill="blue", width=2)
            self.canvas.create_line(x2, y1, x2, y2, fill="blue", width=2)

# DIAR 버튼 클래스
class DiarToggleButton(tk.Frame):
    def __init__(self, root, diar_on_image_path, diar_off_image_path, label, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.DIAR = False
        self.label = label

        self.diar_on_image = tk.PhotoImage(file=diar_on_image_path)
        self.diar_off_image = tk.PhotoImage(file=diar_off_image_path)

        self.button = tk.Button(self, image=self.diar_off_image, command=self.toggle)
        self.button.pack()

    def toggle(self):
        # FIRE 버튼이 ON일 시에만 DIAR 버튼 제어 가능
        if not ImageToggleButton.FIRE:
            return  # FIRE 버튼이 OFF면 아무 작업도 하지 않음

        # DIAR 버튼 상태 전환
        self.DIAR = not self.DIAR
        self.button.config(image=self.diar_on_image if self.DIAR else self.diar_off_image)

        status = "ON" if self.DIAR else "OFF"
        self.label.config(text=f"DIAR = {status}")

        # DIAR가 ON일 경우 2초 후 상태 초기화
        if self.DIAR:
            self.reset_all()
            self.after(2000, self.reset_diar)

    def reset_diar(self):
        self.DIAR = False
        self.button.config(image=self.diar_off_image)
        self.label.config(text="DIAR = OFF")

    def reset_all(self):
        for button in toggle_buttons:
            # ser.write(b'0')
            # ser.flush()
            print("Sent '0' to Pico")
            setattr(button, button.variable_name, False)
            button.button.config(image=button.off_image)
            button.label.config(text=f"{button.variable_name} = OFF")
    
        # 신호 그래프를 0으로 초기화
        signal_graph.update_signal("ARM_1", 0)
        signal_graph.update_signal("ARM_2", 0)
        signal_graph.update_signal("ARM_3", 0)

        # 상태 동기화 DISR 버튼을 누르면 모든 버튼이 리셋이 정상적으로 작동 되지만 
        # 여기서 ARM_1 버튼을 누르면 동작이 없다가 다시 한번 누르게 되면 정상적으로 on이 된다 이를 방지 하기 위해 상태 동기화 추가
        ImageToggleButton.ARM_1 = False
        ImageToggleButton.ARM_2 = False
        ImageToggleButton.ARM_3 = False
        ImageToggleButton.FIRE = False

# # ADC 그래프
# class ADCGraph:
#     def __init__(self, canvas, label):
#         self.volt_values = []
#         self.canvas = canvas
#         self.label = label
#         self.update_adc_value()

#     def update_adc_value(self):
#         try:
#             if ser.in_waiting > 0:
#                 adc_value = ser.readline().decode('utf-8').strip()
#                 voltage = float(adc_value)
#                 self.volt_values.append(voltage)

#                 if len(self.volt_values) > 60:
#                     self.volt_values.pop(0)

#                 self.label.config(text=f"ADC Value: {adc_value:}", font=("Helvetica", 20), bg='white')

#                 self.update_graph()
#         except serial.SerialException as e:
#             print(f"Failed to read data from Pico: {e}")

#         self.label.after(1000, self.update_adc_value)

#     def update_graph(self):
#         self.canvas.delete("adc_volt_graph")
#         try:
#             for i in range(len(self.volt_values) - 1):
#                 x1 = i * 10
#                 y1 = 225 - self.volt_values[i] * 15
#                 x2 = (i + 1) * 10
#                 y2 = 225 - self.volt_values[i + 1] * 15
#                 self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="adc_volt_graph")
#         except ValueError:
#             pass

# 메인 GUI
root = tk.Tk()
root.title("SAD_display")
root.geometry("1220x740")

large_rect = tk.Frame(width=625, height=450, bg="white", relief="solid", bd=1)
large_rect.place(x=60, y=25)

canvas_inside_large = tk.Canvas(large_rect, width=625, height=450, bg="white")
canvas_inside_large.pack()
canvas_inside_large.create_line(0, 225, 630, 225, fill="black", width=2)

Vol_val = ["+15V", "+10V", "+5V", "0V", "-5V", "-10V", "-15V"]
Vol_y_pos = [22, 94, 167, 240, 314, 387, 460]
for name, y in zip(Vol_val, Vol_y_pos):
    Vol_label = tk.Label(root, text=name, font=("Helvetica", 10))
    Vol_label.place(x=10, y=y)

adc_label = tk.Label(root, text="ADC Value: ")
adc_label.place(x=830, y=440)

medium_rect = tk.Frame(width=350, height=375, bg="white", relief="solid", bd=1)
medium_rect.place(x=790, y=25)

canvas_inside_medium = tk.Canvas(medium_rect, width=350, height=375, bg="white")
canvas_inside_medium.pack()

canvas_inside_medium.create_line(0, 126, 350, 126, fill="black", width=2)
canvas_inside_medium.create_line(0, 251, 350, 251, fill="black", width=2)

signal_labels = [tk.Label(text="LOW", font=("Helvetica", 12)) for _ in range(3)]
for i, y in enumerate([70, 195, 325]):
    signal_labels[i].place(x=1160, y=y)

ARM_num = ["ARM_1", "ARM_2", "ARM_3"]
ARM_y_pos = [70, 195, 325]
for name, y in zip(ARM_num, ARM_y_pos):
    ARM_label = tk.Label(text=name, font=("Helvetica", 12))
    ARM_label.place(x=715, y=y)

x_start = 50
gap_180 = 180
gap_260 = 260
toggle_buttons = []

for i, variable_name in enumerate(["ARM_1", "ARM_2", "ARM_3", "FIRE"]):
    x_position = x_start + (i % 3) * gap_180 if i < 3 else x_start + 2 * gap_180 + gap_260

    label = tk.Label(root, text=f"{variable_name} = OFF", font=("Arial", 16))
    label.place(x=x_position-5, y=700)

    toggle_button = ImageToggleButton(
        root,
        on_image_path="C:/code_img_folder/toggle_on.png",
        off_image_path="C:/code_img_folder/toggle_off.png",
        variable_name=variable_name,
        label=label
    )
    toggle_button.place(x=x_position, y=525)
    toggle_buttons.append(toggle_button)

diar_label = tk.Label(root, text="DIAR = OFF", font=("Arial", 16))
diar_label.place(x=920, y=700)

toggle_diar = DiarToggleButton(
    root,
    diar_on_image_path="C:/code_img_folder/diar_sw1_1.png",
    diar_off_image_path="C:/code_img_folder/diar_sw2_2.png",
    label=diar_label
)
toggle_diar.place(x=925, y=525)

# ARM_3 순발, 지연
fuze_var = tk.StringVar(value="50ms")  # 초기 값을 Delay로 설정

# 신호 그래프 인스턴스 생성
signal_graph = Signal_data(root, canvas_inside_medium, signal_labels, fuze_var)

Fuze_canvas = tk.Canvas(root, width=125, height=75)
Fuze_canvas.place(x=525, y=525)
Fuze_canvas.create_rectangle(10, 10, 125, 70, outline="black", width=1)

Fuze_Quick = tk.Radiobutton(root, text="Quick", variable=fuze_var, value="20ms", command=signal_graph.update_fuze_mode, font=("Arial", 12))
Fuze_Quick.place(x=550, y=550)

Delay_canvas = tk.Canvas(root, width=125, height=75)
Delay_canvas.place(x=525, y=605)
Delay_canvas.create_rectangle(10, 10, 125, 70, outline="black", width=1)

Delay_Fuze = tk.Radiobutton(root, text="Delay", variable=fuze_var, value="50ms", command=signal_graph.update_fuze_mode, font=("Arial", 12))
Delay_Fuze.place(x=550, y=630)

# adc_graph = ADCGraph(canvas_inside_large, adc_label)
signal_graph.update_loop()  # 신호 그래프 주기적 업데이트 시작

root.mainloop()
