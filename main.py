import tkinter as tk

def on_click(event):
    global selected_piece
    if not selected_piece:
        selected_piece = event.widget
    else:
        if selected_piece != event.widget:
            temp_text = selected_piece.cget("text")
            selected_piece.config(text=event.widget.cget("text"))
            event.widget.config(text=temp_text)
            selected_piece = None

root = tk.Tk()
root.title("Игра Пазлы")

canvas = tk.Canvas(root, width=600, height=400, bg='white')
canvas.pack()

piece1 = tk.Label(canvas, text="Пазл 1", bg='lightblue')
piece1_window = canvas.create_window(100, 50, window=piece1)

piece2 = tk.Label(canvas, text="Пазл 2", bg='lightgreen')
piece2_window = canvas.create_window(140, 50, window=piece2)

piece3 = tk.Label(canvas, text="Пазл 3", bg='lightpink')
piece3_window = canvas.create_window(100, 70, window=piece3)

piece4 = tk.Label(canvas, text="Пазл 4", bg='lightyellow')
piece4_window = canvas.create_window(140, 70, window=piece4)

selected_piece = None

piece1.bind("<Button-1>", on_click)
piece2.bind("<Button-1>", on_click)
piece3.bind("<Button-1>", on_click)
piece4.bind("<Button-1>", on_click)

root.mainloop()