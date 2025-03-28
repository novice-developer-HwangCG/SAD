import tkinter as tk
import serial
import threading
import time
from datetime import datetime

# ser = serial.Serial('/dev/ttyTHS1', 115200, timeout=1)

toggle_buttons = []     # 전역 리스트로 각 버튼 인스턴스를 관리

class ImageToggleButton(tk.Frame):
    def __init__(self, root, on_image_path, off_image_path, variable_name, label, action_handler, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.variable_name = variable_name
        self.label = label
        self.is_on = False  # OFF 상태
        self.action_handler = action_handler  # 기능 실행 핸들러 추가

        self.on_image = tk.PhotoImage(file=on_image_path)
        self.off_image = tk.PhotoImage(file=off_image_path)

        self.button = tk.Button(self, image=self.off_image, command=self.toggle)
        self.button.pack()

        toggle_buttons.append(self)  # 버튼을 전역 리스트에 추가

    def toggle(self):
        """버튼 제어 로직"""
        if self.variable_name == "ARM_2" and not toggle_buttons[0].is_on:
            return
        elif self.variable_name == "ARM_3" and not toggle_buttons[1].is_on:
            return
        elif self.variable_name == "FIRE" and not toggle_buttons[2].is_on:
            return
        elif self.variable_name == "DIAR" and not toggle_buttons[3].is_on:
            return

        # 상태 변경
        self.is_on = not self.is_on

        # 기능 핸들러를 호출해 버튼에 따른 동작 실행
        self.action_handler.perform_action(self.variable_name, self.is_on)

        # 버튼 UI 업데이트
        self.update_button_display()

    def update_button_display(self):
        """버튼 이미지 및 라벨 업데이트"""
        if self.is_on:
            self.button.config(image=self.on_image)
            self.label.config(text=f"{self.variable_name} = HIGH")
        else:
            self.button.config(image=self.off_image)
            self.label.config(text=f"{self.variable_name} = LOW")

        # 신호 그래프 및 라벨 업데이트
        signal_graph.update_signal(self.variable_name, self.is_on)

class ButtonActionHandler:
    def __init__(self):
        # 각 버튼 상태를 관리하는 속성 추가
        self.ARM_1 = False
        self.ARM_2 = False
        self.ARM_3 = False
        self.FIRE = False

    def perform_action(self, button_name, state):
        """버튼에 따른 동작을 실행하고 상태 업데이트"""
        if button_name == "ARM_1":
            self.ARM_1 = state
            self.arm_1_action(state)
        elif button_name == "ARM_2":
            self.ARM_2 = state
            self.arm_2_action(state)
        elif button_name == "ARM_3":
            self.ARM_3 = state
            self.arm_3_action(state)
        elif button_name == "FIRE":
            self.FIRE = state
            self.fire_action(state)

    def arm_1_action(self, is_on):
        """ARM_1 버튼 동작"""
        if is_on:
            self.send_signal_to_pico("ARM_1", True)
        else:
            self.send_signal_to_pico("ARM_1", False)

    def arm_2_action(self, is_on):
        """ARM_2 버튼 동작"""
        print("ARM_2 활성화" if is_on else "ARM_2 비활성화")

    def arm_3_action(self, is_on):
        """ARM_3 버튼 동작"""
        print("ARM_3 활성화" if is_on else "ARM_3 비활성화")

    def fire_action(self, is_on):
        """FIRE 버튼 동작"""
        print("FIRE 버튼 활성화" if is_on else "FIRE 버튼 비활성화")

    def send_signal_to_pico(self, variable_name, state):
        """Pico에 신호 전송"""
        try:
            if state:
                # ser.write(b'1')
                print(f"Sent '1' to Pico for {variable_name}")
            else:
                # ser.write(b'0')
                print(f"Sent '0' to Pico for {variable_name}")
            # ser.flush()
        except serial.SerialException as e:
            print(f"Failed to send data to Pico: {e}")

class DiarToggleButton(tk.Frame):
    """DIAR 버튼 클래스"""
    def __init__(self, root, action_handler, diar_on_image_path, diar_off_image_path, label, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.DIAR = False
        self.label = label
        self.action_handler = action_handler

        self.diar_on_image = tk.PhotoImage(file=diar_on_image_path)
        self.diar_off_image = tk.PhotoImage(file=diar_off_image_path)

        self.button = tk.Button(self, image=self.diar_off_image, command=self.toggle)
        self.button.pack()

    def toggle(self):
        # FIRE 버튼의 상태를 참조
        fire_button = next((button for button in toggle_buttons if button.variable_name == "FIRE"), None)
        if fire_button is None or not fire_button.is_on:
            return  # FIRE 버튼이 OFF일 때는 동작하지 않음

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
        """모든 버튼과 신호 그래프 상태를 초기화하는 메서드."""
        for button in toggle_buttons:
            if isinstance(button, ImageToggleButton):   # toggle_buttons 리스트에 ImageToggleButton 인스턴스가 없을 경우
                button.is_on = False
                button.update_button_display()
            else:
                print(f"Warning: {button} is not an ImageToggleButton instance.")

        print("Sent '0' to Pico")

        # ButtonActionHandler 상태 초기화
        self.action_handler.ARM_1 = False
        self.action_handler.ARM_2 = False
        self.action_handler.ARM_3 = False
        self.action_handler.FIRE = False

        # 신호 데이터를 0으로 설정
        for signal_list in [signal_graph.signal_Data1, signal_graph.signal_Data2, signal_graph.signal_Data3]:
            signal_graph.update_signal_history(signal_list, 0)

        # Pico로 OFF 신호 전송
        # try:
        #     ser.write(b'0')
        #     ser.flush()
        # except serial.SerialException as e:
        #     print(f"Failed to send reset signal to Pico: {e}")

class SignalData(tk.Frame):
    """각 버튼에 상태에 대한 신호 그래프 그리기 클래스"""
    def __init__(self, root, canvas, action_handler, signal_labels, fuze_var):
        super().__init__(root)
        self.root = root  # root 객체를 받아서 이후 after() 메서드에 사용 실시간 신호 그래프를 위함
        self.canvas = canvas
        self.action_handler = action_handler
        self.signal_labels = signal_labels
        self.fuze_var = fuze_var

        self.signal_Data1 = []
        self.signal_Data2 = []
        self.signal_Data3 = []

        self.ARM_3_toggle_interval = 50

    def update_signal(self, variable_name, new_state):
        if variable_name == "ARM_1":
            self.update_signal_history(self.signal_Data1, new_state)
        elif variable_name == "ARM_2":
            self.update_signal_history(self.signal_Data2, new_state)
        elif variable_name == "ARM_3":
            self.update_signal_history(self.signal_Data3, new_state)
        
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
        signal_list.append(new_signal_value)  # 새로운 신호 값 저장
        if len(signal_list) > 10:  # 최대 10개 신호만 유지
            signal_list.pop(0)

    def update_loop(self):
        # ARM 버튼 상태 확인 및 신호 업데이트
        self.update_signal_history(self.signal_Data1, 1 if self.action_handler.ARM_1 else 0)
        self.update_signal_history(self.signal_Data2, 1 if self.action_handler.ARM_2 else 0)

        if self.action_handler.ARM_3:
            self.update_signal_arm_3()
        else:
            self.update_signal_history(self.signal_Data3, 0)

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
        """ARM 버튼 상태에 따라 텍스트 라벨을 업데이트"""
        self.signal_labels[0].config(text="HIGH" if self.action_handler.ARM_1 else "LOW")
        self.signal_labels[1].config(text="HIGH" if self.action_handler.ARM_2 else "LOW")
        self.signal_labels[2].config(text="HIGH" if self.action_handler.ARM_3 else "LOW")

    def update_graph(self):
        self.canvas.delete("all")
        canvas_inside_medium.create_line(0, 126, 350, 126, fill="black", width=2)
        canvas_inside_medium.create_line(0, 251, 350, 251, fill="black", width=2)

        self.draw_signal(self.signal_Data1, 15, 110)
        self.draw_signal(self.signal_Data2, 140, 235)
        self.draw_signal(self.signal_Data3, 265, 360)

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

class ADCGraph:
    """ADC 그래프"""
    def __init__(self, canvas, label):
        self.volt_values = []
        self.canvas = canvas
        self.label = label

    def update_adc_value(self, voltage):
        """시리얼 데이터를 받아서 그래프와 텍스트 라벨을 업데이트"""
        self.volt_values.append(voltage)

        if len(self.volt_values) > 60:  # 60개를 초과하면 가장 오래된 값 삭제
            self.volt_values.pop(0)

        # 소수점 두 자리까지 표시
        self.label.config(text=f"ADC Value: {voltage:.2f}", font=("Helvetica", 20), bg='white')

        # 그래프 업데이트
        self.update_graph()

    def update_graph(self):
        """volt_values에 저장된 값으로 그래프 그리기"""
        self.canvas.delete("adc_volt_graph")
        try:
            for i in range(len(self.volt_values) - 1):
                x1 = i * 10
                y1 = 225 - self.volt_values[i] * 15
                x2 = (i + 1) * 10
                y2 = 225 - self.volt_values[i + 1] * 15
                self.canvas.create_line(x1, y1, x2, y1, fill="blue", width=2, tags="adc_volt_graph")
        except ValueError:
            pass

# def serial_read_loop():
#     """시리얼 데이터를 읽고 메인 스레드에서 업데이트 요청"""
#     while True:
#         try:
#             if ser.in_waiting > 0:
#                 adc_value = ser.readline().decode('utf-8').strip()
#                 voltage = float(adc_value)
#                 root.after(0, adc_graph.update_adc_value, voltage)  # 메인 스레드에서 GUI 업데이트
#         except serial.SerialException as e:
#             print(f"Failed to read from Pico: {e}")
#             break

class TimeUpdate:
    @staticmethod
    def timestamp_update():
        while True:
            current_time = time.time()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            root.after(0, lambda ts=timestamp: timestamp_update_label(ts))
            time.sleep(0.1)  # Update every second

def timestamp_update_label(timestamp):
    timestamp_label.config(text=f"Timestamp: {timestamp}")

"""메인 GUI"""
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

timestamp_label = tk.Label(root, text="-", font=("Helvetica", 10))
timestamp_label.place(x=820, y=430)

adc_label = tk.Label(root, text="ADC Value: - ")
adc_label.place(x=820, y=450)

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

action_handler = ButtonActionHandler()

for i, variable_name in enumerate(["ARM_1", "ARM_2", "ARM_3", "FIRE"]):
    x_position = x_start + (i % 3) * gap_180 if i < 3 else x_start + 2 * gap_180 + gap_260

    label = tk.Label(root, text=f"{variable_name} = OFF", font=("Arial", 16))
    label.place(x=x_position-5, y=700)

    toggle_button = ImageToggleButton(
        root,
        on_image_path="C:/code_img_folder/toggle_on.png",
        off_image_path="C:/code_img_folder/toggle_off.png",
        variable_name=variable_name,
        label=label,
        action_handler=action_handler
    )
    toggle_button.place(x=x_position, y=525)
    toggle_buttons.append(toggle_button)

diar_label = tk.Label(root, text="DIAR = OFF", font=("Arial", 16))
diar_label.place(x=920, y=700)

toggle_diar = DiarToggleButton(
    root,
    diar_on_image_path="C:/code_img_folder/diar_sw1_1.png",
    diar_off_image_path="C:/code_img_folder/diar_sw2_2.png",
    label=diar_label,
    action_handler=action_handler
)
toggle_diar.place(x=925, y=525)

# ARM_3 순발, 지연
fuze_var = tk.StringVar(value="50ms")  # 초기 값을 Delay로 설정

# 신호 그래프 인스턴스 생성
signal_graph = SignalData(root, canvas_inside_medium, action_handler, signal_labels, fuze_var)

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

timestamp_thread = threading.Thread(target=TimeUpdate.timestamp_update, daemon=True)
timestamp_thread.start()

# serial_thread = threading.Thread(target=serial_read_loop, daemon=True)      # pico 시리얼 쓰레드 시작
# serial_thread.start()

# adc_graph = ADCGraph(canvas_inside_large, adc_label)
signal_graph.update_loop()  # 신호 그래프 주기적 업데이트 시작

root.mainloop()
