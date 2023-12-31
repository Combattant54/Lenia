from screen import CanvasGame

from tkinter import Tk
# windows = Tk()
# windows.wm_title("Simulation de lenia")

# #titre
# label = Label(windows, text="Configuration de la simulation")
# label.pack()

# m_var = DoubleVar()
# m_var_slider = Scale(windows, variable=m_var, )

# # exit
# exit_button = Button(windows, text="Fermer", bg="red", command=windows.quit)
# exit_button.pack()

# windows.mainloop()

def main():
    window = Tk()
    window.title("Simulation - Lenia")
    game = CanvasGame(window)
    
    window.mainloop()

if __name__ == "__main__":
    main()