import tkinter as tk
import os
import serial
import threading
import time
from datetime import datetime
from queue import Queue

"""전체적인 GUI를 담당하는 클래스"""
class SAPPED:
    def __init__(self, main_window):
        self.root=main_window
        self.root.title("SAD Display")
        self.serial_queue=Queue()  # Thread 로 부터 안전한 통신을 위해 queue 추가
        self.canvas_inside_large = None
        self.adc_label = None
        self.timestamp_label = None

        # 모든 이미지 속성을 __init__에서 None으로 초기화
        self.on_image = None
        self.off_image = None
        self.diar_on = None
        self.diar_off = None

        self.toggle_buttons=[]  # 모든 토글 버튼을 관리 하는 리스트

        # Serial 통신
        self.serial_reader=SerialRead(self.serial_queue)

        self.create_ui()

        # button 기능에 serial_readfer 전달
        self.action_handler = ButtonActionHandler(self, self.serial_reader)

        # ADC 그래프
        self.adc_graph = ADCGraph(self.canvas_inside_large, self.adc_label)

        # 주기적 으로 Serial data 를 확인, graph 에 반영
        self.update_adc_graph()

        # Timestamp update 를 위한 호출
        self.time_updater = TimeUpdate(self.timestamp_label)

    def create_ui(self):
        base_dir=os.path.dirname(os.path.abspath(__file__))
        # 이미지 로드 시 에러 처리 추가
        try:
            self.on_image = tk.PhotoImage(file=os.path.join(base_dir, "images/toggle_on.png"))
        except tk.TclError:
            self.on_image = None
        try:
            self.off_image = tk.PhotoImage(file=os.path.join(base_dir, "images/toggle_off.png"))
        except tk.TclError:
            self.off_image = None
        try:
            self.diar_on = tk.PhotoImage(file=os.path.join(base_dir, "images/diar_sw1_1.png"))
        except tk.TclError:
            self.diar_on = None
        try:
            self.diar_off = tk.PhotoImage(file=os.path.join(base_dir, "images/diar_sw2_2.png"))
        except tk.TclError:
            self.diar_off = None

        action_handler = ButtonActionHandler(self, self.serial_reader)

        if not self.diar_on:
            self.diar_on = tk.PhotoImage()
            diar_on_label = tk.Label(self.root, text="None-Image", font=("Arial", 10))
            diar_on_label.place(x=150, y=100)
        if not self.diar_off:
            self.diar_off = tk.PhotoImage()
            diar_off_label = tk.Label(self.root, text="None-Image", font=("Arial", 10))
            diar_off_label.place(x=200, y=100)

        large_rect = tk.Frame(width=625, height=450, bg="white", relief="solid", bd=1)
        large_rect.place(x=60, y=25)

        self.canvas_inside_large = tk.Canvas(large_rect, width=625, height=450, bg="white")
        self.canvas_inside_large.pack()
        self.canvas_inside_large.create_line(0, 225, 630, 225, fill="black", width=1)
        self.canvas_inside_large.create_line(0, 79, 630, 79, fill="black", width=1)
        self.canvas_inside_large.create_line(0, 152, 630, 152, fill="black", width=1)
        self.canvas_inside_large.create_line(0, 299, 630, 299, fill="black", width=1)
        self.canvas_inside_large.create_line(0, 372, 630, 372, fill="black", width=1)

        vol_val = ["+15V", "+10V", "+5V", " 0V", "-5V", "-10V", "-15V"]
        vol_y_pos = [22, 94, 167, 240, 314, 387, 460]
        for name, y in zip(vol_val, vol_y_pos):
            vol_label = tk.Label(root, text=name, font=("Helvetica", 10))
            vol_label.place(x=10, y=y)

        self.timestamp_label = tk.Label(self.root, text="TimeStamp: N/A")
        self.timestamp_label.place(x=820, y=430)

        self.adc_label = tk.Label(root, text="ADC Value: N/A")
        self.adc_label.place(x=820, y=455)

        medium_rect = tk.Frame(width=350, height=375, bg="white", relief="solid", bd=1)
        medium_rect.place(x=790, y=25)

        canvas_inside_medium = tk.Canvas(medium_rect, width=350, height=375, bg="white")
        canvas_inside_medium.pack()

        canvas_inside_medium.create_line(0, 126, 350, 126, fill="black", width=2)
        canvas_inside_medium.create_line(0, 251, 350, 251, fill="black", width=2)

        signal_labels = [tk.Label(text="LOW", font=("Helvetica", 12)) for _ in range(3)]
        for i, y in enumerate([70, 195, 325]):
            signal_labels[i].place(x=1160, y=y)

        arm_num = ["ARM_1", "ARM_2", "ARM_3"]
        arm_y_pos = [70, 195, 325]
        for name, y in zip(arm_num, arm_y_pos):
            arm_label = tk.Label(text=name, font=("Helvetica", 12))
            arm_label.place(x=715, y=y)

        for i, variable_name in enumerate(["ARM_1", "ARM_2", "ARM_3", "FIRE"]):
            x_position = 50 + (i % 3) * 180 if i < 3 else 50 + 2 * 190 + 260
            label = tk.Label(self.root, text=f"{variable_name} = OFF", font=("Arial", 16))
            label.place(x=x_position, y=700)

            toggle_button = ARMToggleButton(self.root, self.on_image, self.off_image, variable_name, label, action_handler)
            toggle_button.place(x=x_position+10, y=525)
            self.toggle_buttons.append(toggle_button)

            # Image 가 None 일 경우 대체 Text 를 표시
            if not self.on_image:
               on_image_label=tk.Label(self.root, text="None-Image", font=("Arial", 14))
               on_image_label.place(x=x_position+10, y=575)
            if not self.off_image:
                off_image_label = tk.Label(self.root, text="None-Image", font=("Arial", 14))
                off_image_label.place(x=x_position+10, y=575)  # 버튼 하단

        diar_label = tk.Label(self.root, text="DIAR = OFF", font=("Arial", 16))
        diar_label.place(x=920, y=700)
        
        toggle_diar = DiarToggleButton(self.root, diar_label, action_handler, self.serial_reader)
        toggle_diar.place(x=930, y=525)

        # Image 가 None 일 경우 대체 Text 를 표시
        if not self.diar_on:
            diar_on_label = tk.Label(self.root, text="None-Image", font=("Arial", 14))
            diar_on_label.place(x=925, y=575)
        if not self.diar_off:
            diar_off_label = tk.Label(self.root, text="None-Image", font=("Arial", 14))
            diar_off_label.place(x=925, y=575)

        fuze_var = tk.StringVar(value="50ms")  # 초기 값을 Delay로 설정

        signal_graph = SignalGraph(root, canvas_inside_medium, action_handler, signal_labels, fuze_var)

        fuze_canvas = tk.Canvas(root, width=125, height=75)
        fuze_canvas.place(x=545, y=525)
        fuze_canvas.create_rectangle(10, 10, 125, 70, outline="black", width=1)

        fuze_quick = tk.Radiobutton(root, text="Quick", variable=fuze_var, value="20ms", command=signal_graph.update_fuze_mode, font=("Arial", 12))
        fuze_quick.place(x=570, y=550)

        delay_canvas = tk.Canvas(root, width=125, height=75)
        delay_canvas.place(x=545, y=605)
        delay_canvas.create_rectangle(10, 10, 125, 70, outline="black", width=1)

        delay_fuze = tk.Radiobutton(root, text="Delay", variable=fuze_var, value="50ms", command=signal_graph.update_fuze_mode, font=("Arial", 12))
        delay_fuze.place(x=570, y=630)

    # Serial Queue 확인, 새로운 데이터 그래프 반영
    def update_adc_graph(self):
        try:
            while not self.serial_queue.empty():
                data=self.serial_queue.get()
                voltage=float(data)
                self.adc_graph.update_adc_value(voltage)
        except ValueError:
            pass    # data 가 숫자로 변환 되지 않을 시 무시

        self.root.after(100, self.update_adc_graph)

    # Serial 통신 시작
    def start_serial_read(self):
        self.serial_reader.start()

"""pico 와 통신을 담당 하는 클래스 혹은 Thread, 연결 실패 시 3번 연결 시도"""
class SerialRead(threading.Thread):
    def __init__(self, serial_queue):
        super().__init__(daemon=True)  # Thread 초기화 및 데몬 모드 설정
        self.serial_queue = serial_queue  # 시리얼 data 를 저장 하는 큐
        self.running = True  # 루프 종료를 제어 하는 플래그
        self.ser = None

        # 빠른 통신을 위해 baudrate = 912600, timeout=0.01 문제가 생길 경우 baudrate를 낮추기, 최대 3번 연결 시도
        for attempt in range(3):
            try:
                self.ser = serial.Serial('/dev/ttyTHS1', 912600, timeout=0.01)
                print("Serial connection established")
                break
            except serial.SerialException as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # 세 번째 시도 에서도 실패 하면 종료
                    print("Serial connection failed")

    # serial data 를 읽고 큐에 추가
    def run(self):
        while self.running:
            if self.ser:
                try:
                    data = self.ser.readline().strip()
                    if data:
                        self.serial_queue.put(data)
                except serial.SerialException as e:
                    print(f"Serial error: {e}")
                    self.ser = None  # 연결이 끊어진 경우 None 으로 설정
                time.sleep(0.1)
            else:
                time.sleep(1)  # 시리얼 연결이 없을 때 재시도 간격

    # 루프 종료 및 Serial port 닫기
    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

"""SerialRead class 에서 data 를 받아와 graph 를 그리고 텍스트 라벨을 update 를 담당 하는 클래스"""
class ADCGraph:
    def __init__(self, canvas, label):
        self.volt_values = []
        self.canvas = canvas
        self.label = label

    def update_adc_value(self, voltage):
        self.volt_values.append(voltage)

        if len(self.volt_values) > 70:  # 70개를 초과 하면 가장 오래된 값 삭제
            self.volt_values.pop(0)

        self.label.config(text=f"ADC Value: {voltage:.2f}", font=("Helvetica", 14))

        # 그래프 update
        self.update_graph()

    def update_graph(self):
        self.canvas.delete("adc_volt_graph")

        if not self.volt_values:  # 값이 없을 경우 처리
            return
        
        # Y축 값 계산 범위를 설정 (전압 값의 최대/최소에 따른 Y축 제한 설정)
        y_offset = 225  # 캔버스 중앙을 기준

        for i in range(len(self.volt_values) - 1):
            x1 = i * 10
            y1 = y_offset - self.volt_values[i] * 15
            x2 = (i + 1) * 10
            y2 = y_offset - self.volt_values[i + 1] * 15
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="adc_volt_graph")

"""TimeStamp 클래스"""
class TimeUpdate:
    def __init__(self, label):
        self.label = label
        self.running = True
        self.update_timestamp()

    # TimeStamp update
    def update_timestamp(self):
        if self.running:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.label.config(text=f"TimeStamp: {current_time}", font=("Helvetica", 14))
            self.label.after(100, self.update_timestamp)

    # TimeStamp update 중지
    def stop(self):
        self.running = False

"""ARM_1, ARM_2, ARM_3, FIRE 버튼에 대한 로직과 각 버튼 상태에 따라 이미지 변경을 담당하는 클래스"""
class ARMToggleButton(tk.Frame):
    def __init__(self, main_window, on_image, off_image, variable_name, label, action_handler, *args, **kwargs):
        super().__init__(main_window, *args, **kwargs)
        self.variable_name = variable_name
        self.label = label
        self.is_on = False
        self.action_handler = action_handler

        self.on_image = on_image
        self.off_image = off_image

        self.button = tk.Button(self, image=self.off_image, command=self.toggle)
        self.button.pack()

    # ARM 버튼 제어 로직
    def toggle(self):
        if self.variable_name == "ARM_2" and not self.action_handler.ARM_1:
            return
        elif self.variable_name == "ARM_3" and not self.action_handler.ARM_2:
            return
        elif self.variable_name == "FIRE" and not self.action_handler.ARM_3:
            return

        self.is_on = not self.is_on
        self.action_handler.toggle_update(self.variable_name, self.is_on)
        self.update_button_display()

    # button image 및 label update
    def update_button_display(self):
        if self.is_on:
            self.button.config(image=self.on_image)
            self.label.config(text=f"{self.variable_name} = ON")
        else:
            self.button.config(image=self.off_image)
            self.label.config(text=f"{self.variable_name} = OFF")

"""각 버튼에 기능을 담당 하는 클래스"""
class ButtonActionHandler:
    def __init__(self, button, serial_reader):
        self.app = button
        self.serial_reader = serial_reader
        # 각 버튼 상태를 관리 하는 속성 추가
        self.ARM_1 = False
        self.ARM_2 = False
        self.ARM_3 = False
        self.FIRE = False

    # 버튼에 따른 동작을 실행 하고 상태 update
    def toggle_update(self, button_name, state):
        setattr(self, button_name, state)  # 버튼 상태 update
        print(f"{button_name} {'활성화' if state else '비활성화'}")

        if button_name == "ARM_1":
            self.arm_1_action(state)
        
    def arm_1_action(self, is_on):
        if is_on:
            self.send_signal_to_pico(True)
        else:
            self.send_signal_to_pico(False)
        pass

    def arm_2_action(self, is_on):
        pass

    def arm_3_action(self, is_on):
        pass

    def fire_action(self, is_on):
        pass

    # Pico 에 신호 전송
    def send_signal_to_pico(self, state):
        try:
            if self.serial_reader.ser:  # Serial 연결이 있는지 확인
                if state:
                    self.serial_reader.ser.write(b'1')  # '1'전송
                    print("Sent '1' to Pico")
                else:
                    self.serial_reader.ser.write(b'0')  # '0' 전송
                    print("Sent '0' to Pico")
                self.serial_reader.ser.flush()
        except serial.SerialException as e:
            print(f"Failed to send data to Pico: {e}")

"""DIAR 버튼 기능과 DIAR 버튼 상태에 따라 DIAR 버튼 이미지 변경을 담당하는 클래스"""
class DiarToggleButton(tk.Frame):
    def __init__(self, main_window, label, action_handler, serial_reader):
        super().__init__(main_window)
        self.DIAR = False
        self.label = label
        self.action_handler = action_handler
        self.serial_reader = serial_reader
        self.diar_on_image = self.action_handler.app.diar_on
        self.diar_off_image = self.action_handler.app.diar_off

        self.button = tk.Button(self, image=self.diar_off_image, command=self.toggle)
        self.button.pack()

    def toggle(self):
        if not self.action_handler.FIRE:
            return  # FIRE 버튼이 OFF일 때는 동작하지 않음

        self.DIAR = not self.DIAR
        self.update_button_display()    # DIAR 상태 변경

        if self.DIAR:
            self.reset_all()
            # noinspection PyArgumentList
            self.after(2000, self.reset_diar)

    # DIAR 버튼이 ON되면 초기화 및 2초 후 DIAR 버튼도 OFF로 설정
    def reset_diar(self):
        self.DIAR = False
        self.update_button_display()

    # 모든 버튼과 상태 초기화 -> 버튼 OFF, 신호 그래프 LOW
    def reset_all(self):
        for button in self.action_handler.app.toggle_buttons:
            button.is_on = False
            button.update_button_display()

        # ButtonActionHandler 상태 초기화
        self.action_handler.ARM_1 = False
        self.action_handler.ARM_2 = False
        self.action_handler.ARM_3 = False
        self.action_handler.FIRE = False

        try:
            if self.serial_reader.ser:
                self.serial_reader.ser.write(b'0')
                self.serial_reader.ser.flush()
                print("Sent '0' to Pico")
        except serial.SerialException as e:
            print(f"Failed to send data to Pico: {e}")

    # DIAR 버튼 UI 업데이트
    def update_button_display(self):
        if self.DIAR:
            self.button.config(image=self.diar_on_image)
            self.label.config(text="DIAR = ON")
        else:
            self.button.config(image=self.diar_off_image)
            self.label.config(text="DIAR = OFF")

"""ARM_1, ARM_2, ARM_3 버튼 상태에 따라 신호 그래프 HIGH/LOW 그리기 및 텍스트 라벨 업데이트를 담당하는 클래스"""
class SignalGraph(tk.Frame):
    def __init__(self, main_window, canvas, action_handler, signal_labels, fuze_var):
        super().__init__(main_window)
        self.root = main_window  # root 객체를 받아서 이후 after() 메서드에 사용 (실시간 신호 그래프 업데이트를 위해)
        self.canvas = canvas
        self.action_handler = action_handler
        self.signal_labels = signal_labels
        self.fuze_var = fuze_var

        # 신호 데이터를 저장하는 리스트 (각각 ARM_1, ARM_2, ARM_3에 대한 신호)
        self.signal_Data1 = []
        self.signal_Data2 = []
        self.signal_Data3 = []

        # ARM_3의 토글 간격 (순발/지연 모드를 위한 시간 간격) 프로그램 시작 시 초기 값을 delay로 되어 있기 때문에 50 이후 ARM_3 버튼을 누를 때마다 변화
        self.ARM_3_toggle_interval = 50

        self.update_loop()  # 신호 처리 및 그래프 업데이트를 위한 주기적 루프 시작

    def update_signal(self, variable_name, new_state):
        if variable_name == "ARM_1":
            self.update_signal_history(self.signal_Data1, new_state)
        elif variable_name == "ARM_2":
            self.update_signal_history(self.signal_Data2, new_state)
        elif variable_name == "ARM_3":
            self.update_signal_history(self.signal_Data3, new_state)

    def update_fuze_mode(self):
        selected_fuze = self.fuze_var.get()
        if selected_fuze == "20ms":
            self.ARM_3_toggle_interval = 20
        elif selected_fuze == "50ms":
            self.ARM_3_toggle_interval = 50

    @staticmethod
    def update_signal_history(signal_list, new_signal_value):
        signal_list.append(new_signal_value)
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

        # 100ms 후에 다시 루프 실행 
        self.root.after(100, self.update_loop)

    # ARM_3의 순발/지연 신호 데이터를 업데이트
    def update_signal_arm_3(self):
        quick_data = [0, 1]
        delay_data = [0, 0, 1, 1]

        # 순발 모드 (20ms) 또는 지연 모드 (50ms)에 따른 신호 업데이트
        if self.ARM_3_toggle_interval == 20:
            for i in quick_data:
                self.update_signal_history(self.signal_Data3, i)
        elif self.ARM_3_toggle_interval == 50:
            for i in delay_data:
                self.update_signal_history(self.signal_Data3, i)

    # ARM 버튼 상태에 따라 텍스트 라벨을 업데이트
    def update_signal_labels(self):
        self.signal_labels[0].config(text="HIGH" if self.action_handler.ARM_1 else "LOW")
        self.signal_labels[1].config(text="HIGH" if self.action_handler.ARM_2 else "LOW")
        # ARM_3에 텍스트 라벨은 ARM_1,ARM_2 처럼 on/off에 따라 HIGH/LOW 하나만 그리지만 ARM_3는 HIGH/LOW를 번갈아 그리기 때문에 추 후 수정 보류 
        self.signal_labels[2].config(text="HIGH" if self.action_handler.ARM_3 else "LOW")

    def update_graph(self):
        self.canvas.delete("all")
        self.canvas.create_line(0, 126, 350, 126, fill="black", width=2)
        self.canvas.create_line(0, 251, 350, 251, fill="black", width=2)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = SAPPED(root)
    app.start_serial_read()
    root.geometry("1220x740")

    def on_closing():
            app.serial_reader.stop()  # 스레드 종료
            app.time_updater.stop()  # 타임스탬프 업데이트 중지
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
