import tkinter as tk
import os
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import subprocess


from tkinter import ttk
from recorder import AudioRecorder
from playback import SoundPlayer, WAVReader


class RecorderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('1000x700')
        self.root.title("Audio Recorder")
        self.root.resizable(False, False)

        self.listbox = tk.Listbox(self.root, width='25', height='35')
        self.listbox.grid(row='0', column='0', sticky='NW')
        self.load_recorded_files()

        self.display_panel = tk.Frame(
            self.root, width='950', height='563', bg='blue')
        self.display_panel.grid(row='0', column='1')

        self.figure = plt.figure(figsize=(9.5, 5.63))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.display_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.control_panel = tk.Frame(self.root, width='1000', height='150')
        self.control_panel.grid(row='1', columnspan='2')

        self.progress_bar = ttk.Progressbar(
            self.display_panel, length='650', orient='horizontal', maximum='100')
        self.progress_bar.place(x='150', y='520')
        self.progress_bar.bind("<Button-1>", self.seek)

        '''self.seek_bar_value = tk.DoubleVar()
        self.seek_bar = tk.Scale(
            self.display_panel, variable=self.seek_bar_value, orient='horizontal', length='650')
        self.seek_bar.place(x='150', y='520')'''

        self.time = tk.StringVar()
        self.time_stamp = tk.Label(self.display_panel, width='10', textvariable=self.time, font=(
            "Arial", 11, "bold"))
        self.time_stamp.place(x='21', y='520')
        # button
        self.record_button = tk.Button(self.control_panel, text="⏺", font=(
            "Arial", 25, "bold"), relief='solid', command=self.toggle_recording)
        self.record_button.place(x='0', y='35')

        self.play_button = tk.Button(self.control_panel, text="⏯", font=(
            "Arial", 25, "bold"), relief='solid', command=self.play_audio)
        self.play_button.place(x='95', y='35')

        self.stop_button = tk.Button(self.control_panel, text="⏹", font=(
            "Arial", 25, "bold"), relief='solid', command=self.stop_audio)
        self.stop_button.place(x='195', y='35')

        self.edit_button = tk.Button(self.control_panel, text="✎", font=(
            "Arial", 25, "bold"), relief='solid', command=self.edit_audio)
        self.edit_button.place(x='295', y='35')

        self.volume = tk.Scale(
            self.control_panel, orient='horizontal', width='25', length='150', from_='0', to='100', command=self.set_volume)
        self.volume.set(1)
        self.volume.place(x='750', y='50')

        self.vol_label = tk.Label(self.control_panel, text="Volume")
        self.vol_label.place(x='750', y='33')

        self.play_speed = tk.Scale(
            self.control_panel, orient='horizontal', width='25', length='150', from_='0.1', to='8', resolution='0.1', command=self.set_play_speed)  # max is 8
        self.play_speed.set(1)
        self.play_speed.place(x='545', y='50')

        self.play_speed_label = tk.Label(self.control_panel, text="Play Speed")
        self.play_speed_label.place(x='545', y='33')
        # Define the function for the timer
        self.recorder = AudioRecorder()
        self.WAVReader = WAVReader(None)
        self.player = SoundPlayer(
            self.WAVReader, self.progress_bar, self.time)
        self.root.mainloop()

    def edit_audio(self):
        subprocess.Popen(['python' , 'trim_gui.py'])

    def load_recorded_files(self):
        recorded_files = [file for file in os.listdir(
            "recorded_files") if file.endswith(".wav")]

        recorded_files = sorted(recorded_files)

        self.listbox.delete(0, tk.END)

        for file in recorded_files:
            self.listbox.insert(tk.END, file)

    def toggle_recording(self):
        if not self.recorder.recording:  # Start recording if not already recording
            self.record_button.config(text="⏹", fg="red")
            threading.Thread(target=self.recorder.record_audio).start()
            self.start_time = time.time()
        else:  # Stop recording if already recording
            self.record_button.config(text="⏺", fg="black")
            self.recorder.stop_recording()
            self.recorder.save_as_wav()
            self.load_recorded_files()

    def play_audio(self, start_time=0):
        if not self.listbox.curselection():
            return
        selected_file = self.listbox.get(self.listbox.curselection())
        self.WAVReader.set_filename(f"recorded_files/{selected_file}")
        if self.WAVReader.get_filename() is None:
            return
        self.WAVReader.read_wav_file()

        audio_data = self.WAVReader.get_audio_data()
        time = [i/self.WAVReader.get_sample_rate()
                for i in range(len(audio_data))]

        self.ax.clear()
        self.ax.plot(time, audio_data, color='b')
        self.ax.set_title(f"{selected_file}")
        self.ax.set_axis_off()
        self.canvas.draw()

        self.player.play_sound()

    def stop_audio(self):
        self.player.stop_sound()

    def set_play_speed(self, speed):
        self.player.playback_speed = float(speed)

    def set_volume(self, volume):
        self.player.set_volume(float(volume))

    def is_recording(self):
        return self.recording

    def seek(self, event):
        # Calculate the new start time based on the mouse click position
        ratio = event.x / self.progress_bar.winfo_width()
        new_start_time = ratio * self.player.get_total_time()

        # Stop the current playback
        self.player.stop_sound()

        # Start playing from the new start time
        self.player.play_sound(start_time=new_start_time)


RecorderApp()
