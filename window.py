import tkinter as tk
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename

button2 = None
button3 = None

def change_image1():
    global button2, button3
    label.destroy()
    button.destroy()
    button2 = Combobox(root)
    button2['values'] = ("Звездная ночь", "Утро в сосновом бору", "Свое изображение")
    button2.current(1)
    button2.grid(column=0, row=0)
    button3 = tk.Button(root, text="выбери сложность", command=change_image2)
    button3.grid(column=0, row=2)

def change_image2():
    global button2, button3
    selected_value = button2.get()
    if selected_value == "Звездная ночь":
        button2.destroy()
        button3.destroy()
        button4 = Combobox(root)
        button4['values'] = ("10 пазл", "20 пазл", "30 пазл")
        button4.current(1)  # установите вариант по умолчанию
        button4.grid(column=0, row=0)
    elif selected_value == "Утро в сосновом бору":
        button2.destroy()
        button3.destroy()
        button4 = Combobox(root)
        button4['values'] = ("10 пазл", "20 пазл", "30 пазл")
        button4.current(1)  # установите вариант по умолчанию
        button4.grid(column=0, row=0)
    elif selected_value == "Свое изображение":
        button2.destroy()
        button3.destroy()
        button6 = tk.Button(root, text="Загрузите изображение", command=open_file)
        button6.pack()

def open_file():
    """Открываем файл для редактирования"""
    filepath = askopenfilename(
    filetypes=[("изображение", "*.png"), ("Все файлы", "*.*")])

root = tk.Tk()
root.title("Игра Пазлы")
root.geometry("900x500")

button = tk.Button(root, text="Выбрать изображение", command=change_image1)
button.pack()

label = tk.Label(root, text="Привет, это игра пазлы!")
label.pack()

root.mainloop()