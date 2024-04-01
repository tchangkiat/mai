import pyaudio
import wave
import threading
import keyboard
import whisper

from mai.helpers import logging


class Transcriber:
    def __init__(
        self,
        callback_func,
        chunk=1024,
        sample_format=pyaudio.paInt16,
        channels=1,
        fs=44100,
        filename="output.wav",
    ):
        self.log = logging.Logging.get_instance()

        self.callback_func = callback_func
        self.chunk = chunk
        self.sample_format = sample_format
        self.channels = channels
        self.fs = fs
        self.filename = filename
        self.frames = []
        self.log.sys("Loading OpenAI Whisper Model")
        self.model = whisper.load_model("base.en")
        self.log.sys("Loaded OpenAI Whisper Model")
        self.p = pyaudio.PyAudio()
        self.recording = False
        self.trans = {
            "recording": "🔴 Recording",
            "stopped": "🔄 Stopped recording",
            "tutorial": "To begin or end a recording, press",
            "transcription": "🗣️",
        }
        self.set_hotkey("space")

    def toggle_recording(self):
        self.recording = not self.recording
        if self.recording:
            print(self.trans["recording"])
            self.frames = []  # Clear previous recording frames
            threading.Thread(target=self.record).start()
        else:
            print(self.trans["stopped"])

    def record(self):
        stream = self.p.open(
            format=self.sample_format,
            channels=self.channels,
            rate=self.fs,
            frames_per_buffer=self.chunk,
            input=True,
        )
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        stream.stop_stream()
        stream.close()
        self.transcribe_recording()

    def transcribe_recording(self):
        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b"".join(self.frames))

        options = {"language": "English", "task": "transcribe"}
        transcription = self.model.transcribe(self.filename, **options, fp16=False)[
            "text"
        ]
        print(self.trans["transcription"], transcription)
        self.callback_func(transcription)

    def set_hotkey(self, hotkey):
        keyboard.add_hotkey(hotkey, self.toggle_recording, suppress=True)
        print(self.trans["tutorial"], hotkey)
        keyboard.wait("esc")
