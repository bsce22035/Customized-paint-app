import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import mediapipe as mp
import threading

# Initialize global variables
brush_color = (0, 0, 255)
brush_size = 5
drawing = False
canvas = np.ones((600, 800, 3), dtype=np.uint8) * 255

# Tkinter setup
root = tk.Tk()
root.title("Customized Painting App")

# Canvas for drawing
paint_canvas = tk.Canvas(root, width=800, height=600)
paint_canvas.pack()

# Function to update canvas in Tkinter window
def update_canvas():
    image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    image = ImageTk.PhotoImage(image)
    paint_canvas.create_image(0, 0, image=image, anchor=tk.NW)
    paint_canvas.image = image

# Mouse event function
def draw(event):
    global drawing
    x, y = event.x, event.y

    if event.type == tk.EventType.ButtonPress:
        drawing = True
    elif event.type == tk.EventType.Motion and drawing:
        cv2.circle(canvas, (x, y), brush_size, brush_color, -1)
        update_canvas()
    elif event.type == tk.EventType.ButtonRelease:
        drawing = False

paint_canvas.bind("<ButtonPress-1>", draw)
paint_canvas.bind("<B1-Motion>", draw)
paint_canvas.bind("<ButtonRelease-1>", draw)

# Brush color change function
def change_color(new_color):
    global brush_color
    brush_color = new_color

# Change brush size
def increase_size():
    global brush_size
    brush_size += 1

def decrease_size():
    global brush_size
    if brush_size > 1:
        brush_size -= 1

# Clear canvas
def clear_canvas():
    global canvas
    canvas[:] = 255
    update_canvas()

# Save canvas to file
def save_canvas():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        cv2.imwrite(file_path, canvas)

# UI buttons
color_frame = tk.Frame(root)
color_frame.pack()

tk.Button(color_frame, text="Red", command=lambda: change_color((255, 0, 0))).pack(side=tk.LEFT)
tk.Button(color_frame, text="Green", command=lambda: change_color((0, 255, 0))).pack(side=tk.LEFT)
tk.Button(color_frame, text="Blue", command=lambda: change_color((0, 0, 255))).pack(side=tk.LEFT)
tk.Button(color_frame, text="Black", command=lambda: change_color((0, 0, 0))).pack(side=tk.LEFT)

size_frame = tk.Frame(root)
size_frame.pack()

tk.Button(size_frame, text="+", command=increase_size).pack(side=tk.LEFT)
tk.Button(size_frame, text="-", command=decrease_size).pack(side=tk.LEFT)

action_frame = tk.Frame(root)
action_frame.pack()

tk.Button(action_frame, text="Clear", command=clear_canvas).pack(side=tk.LEFT)
tk.Button(action_frame, text="Save", command=save_canvas).pack(side=tk.LEFT)

# Mediapipe Hand Tracker setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Hand tracking and canvas update function
def hand_tracking():
    global canvas, brush_size, brush_color

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip image horizontally
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x = int(index_finger_tip.x * frame.shape[1])
                y = int(index_finger_tip.y * frame.shape[0])

                # Update the canvas based on finger position
                cv2.circle(canvas, (x, y), brush_size, brush_color, -1)

        # Show camera feed with hand landmarks
        cv2.imshow("Hand Tracking", frame)

        # Update the Tkinter canvas
        update_canvas()

        # Exit if 'q' is pressed (for webcam window)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start the hand tracking in a separate thread
hand_thread = threading.Thread(target=hand_tracking)
hand_thread.start()

# Start the Tkinter main loop
root.mainloop()
