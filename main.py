import speech_recognition as sr
import numpy as np
import matplotlib.pyplot as plt
import cv2
from easygui import buttonbox
import os
from PIL import Image, ImageTk
from itertools import count
import tkinter as tk
import string

# Characters supported
alphabet = list(string.ascii_lowercase)

# Define ImageLabel class once
class ImageLabel(tk.Label):
    """A label that displays images, and plays them if they are GIFs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        self.delay = im.info.get('duration', 100)

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc = (self.loc + 1) % len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

# Load ISL GIF dictionary
isl_gif = {f.replace(".gif", "").lower(): f for f in os.listdir("ISL_Gifs") if f.endswith(".gif")}

# Main speech-to-sign function
def func():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Ready to listen...")

        while True:
            print("Listening...")
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio).lower()
                print(f"You said: {text}")

                # Clean punctuation
                text = text.translate(str.maketrans('', '', string.punctuation))

                if text in ["goodbye", "good bye", "bye"]:
                    print("👋 Goodbye!")
                    break

                elif text in isl_gif:
                    gif_path = os.path.join("ISL_Gifs", isl_gif[text])
                    if os.path.exists(gif_path):
                        root = tk.Tk()
                        lbl = ImageLabel(root)
                        lbl.pack()
                        lbl.load(gif_path)
                        root.mainloop()
                    else:
                        print(f"GIF for '{text}' not found.")
                else:
                    for char in text:
                        if char in alphabet:
                            img_path = os.path.join("letters", f"{char}.jpg")
                            if os.path.exists(img_path):
                                img = Image.open(img_path)
                                plt.imshow(np.asarray(img))
                                plt.axis("off")
                                plt.draw()
                                plt.pause(0.8)
                            else:
                                print(f"Image for '{char}' not found.")
                    plt.close()

            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

# Main Menu
while True:
    image = "signlang.jpg"
    msg = "SIGN LANGUAGE TRANSLATOR"
    choices = ["START", "END"]
    reply = buttonbox(msg, image=image, choices=choices)
    if reply == "START":
        func()
    elif reply == "END":
        break
