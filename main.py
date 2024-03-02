from tkinter import PhotoImage
import tkinter as tk

def on_click(event):
    global selected_piece
    if not selected_piece:
        selected_piece = event.widget
    else:
        if selected_piece != event.widget:
            selected_image = selected_piece.cget("image")
            selected_piece.config(image=event.widget.cget("image"))
            event.widget.config(image=selected_image)
            selected_piece = None

root = tk.Tk()
root.title("Игра Пазлы")

image1 = PhotoImage(file='1.png')
image2 = PhotoImage(file='2.png')
image3 = PhotoImage(file='3.png')
image4 = PhotoImage(file='4.png')

canvas = tk.Canvas(root, width=600, height=400, bg='white')
canvas.pack()

piece1 = tk.Label(canvas, image=image1, bg='white')
piece1_window = canvas.create_window(100, 50, window=piece1)

piece2 = tk.Label(canvas, image=image2, bg='white')
piece2_window = canvas.create_window(200, 50, window=piece2)

piece3 = tk.Label(canvas, image=image3, bg='white')
piece3_window = canvas.create_window(100, 100, window=piece3)

piece4 = tk.Label(canvas, image=image4, bg='white')
piece4_window = canvas.create_window(200, 100, window=piece4)

selected_piece = None

piece1.bind("<Button-1>", on_click)
piece2.bind("<Button-1>", on_click)
piece3.bind("<Button-1>", on_click)
piece4.bind("<Button-1>", on_click)

root.mainloop()