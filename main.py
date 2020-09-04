import tkinter as tk
from PIL import ImageTk,Image  
import networkx as nx
import sys

dot = "dot.png"
deads = ["updead.png", "rightdead.png", "downdead.png", "leftdead.png"]
partials = ["up.png", "right.png", "down.png", "left.png"]
through = ["leftright.png", "downup.png"]
branches = ["leftrightup.png", "downrightup.png", "downleftright.png", "downleftup.png"]
turns = ["downleft.png", "leftup.png", "rightup.png", "downright.png"]

ids = [dot] + deads + partials + through + branches + turns
base_path = getattr(sys, '_MEIPASS', '.')+'/'

class MapperOptions(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("200x100")
        self.title("Dragonfable Mapper Options")
        self.iconbitmap(base_path + "mappericon.ico")
        
        midframe = tk.Frame(self, width=200)
        title_label = tk.Label(self, text="DF Mapper!", font=("Helvetica", 16))
        self.x_entry = tk.Entry(midframe)
        self.y_entry = tk.Entry(midframe)
        x_label = tk.Label(midframe, text="x", font=("Helvetica", 16))
        
        self.x_entry.grid(row=1, column=0)
        self.y_entry.grid(row=1, column=2)
        x_label.grid(row=1, column=1)
        midframe.grid_columnconfigure(0, weight=1, uniform="third")
        midframe.grid_columnconfigure(1, weight=1, uniform="third")
        midframe.grid_columnconfigure(2, weight=1, uniform="third")

        title_label.pack()
        midframe.pack()
        go_button = tk.Button(text="Go!", command=self.go)
        go_button.pack()

    def popup(self, message):
        w = tk.Toplevel()
        label = tk.Label(w, text=message)
        label.pack(fill='x', padx=50, pady=5)
        button_close = tk.Button(w, text="Close", command=w.destroy)
        button_close.pack(fill='x')

    def go(self):  
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
        except ValueError:
            self.popup("Missing Info!")
            return
        
        self.destroy()
        m = MapperGUI(x, y)
        m.mainloop()

        
                
        

class MapperGUI(tk.Tk):
    def __init__(self, mazex, mazey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iconbitmap(base_path + "mappericon.ico")
        self.maze_dims = (mazex, mazey)
        self.functional_maze = [[-1 for i in range(mazex)] for j in range(mazey)]
        self.aesthetic_maze = [[-1 for i in range(mazex)] for j in range(mazey)]
        self.graph = nx.Graph()

        self.geometry("520x520")
        self.title("Dragonfable Mapper")

        self.last_pressed = None

        canvas = tk.Canvas(self, width=500, height=500)
        canvas.grid(row=0, column=0)

        scroll_x = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        scroll_y = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")

        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        canvas.configure(scrollregion=(0, 0, self.maze_dims[0]*50,self.maze_dims[1]*50))
        self.canvas = canvas
        self.buttons = []
        self.imgs = []
        self.setup_buttons()

    def setup_buttons(self):
        for x in range(self.maze_dims[0]):
            for y in range(self.maze_dims[1]):
                b = tk.Button(self.canvas, text=".", command=lambda x=x, y=y: self.button_pressed(x, y), relief=tk.FLAT)
                b_window = self.canvas.create_window(x*50, y*50, width=50, height=50, anchor=tk.NW, window=b)
                self.buttons.append(b_window)
    
    def make_img_name(self, d, l, r, u):
        s = ""
        if d:
            s += "down"
        if l:
            s += "left"
        if r:
            s += "right"
        if u:
            s += "up"
        if s == "":
            return "dot.png"
        return s + ".png"
    


    def coord_to_name(self,x , y):
        return str(x) + "," + str(y)
    
    def name_to_coord(self, s):
        return [int(x) for x in s.split(",")]
        

    def name_to_joins(self, s):
        if "dead" in s:
            return [True for i in range(10)]
        k = ["down", "left", "right", "up"]
        r = [False, False, False, False]
        for n, name in enumerate(k):
            if name in s:
                r[n] = True
        
        return r
    
    def count_connections(self, c):
        return sum([1 for a in c if a])
    
    def check_cycles(self):
        try:
            _ = list(nx.find_cycle(self.graph, orientation="ignore"))
            return True
        except nx.NetworkXNoCycle:
            return False

    def button_pressed(self, x, y):
        if self.last_pressed is None:
            self.set_square(x, y, self.make_img_name(0, 0, 0, 0))
            self.last_pressed = (x, y)
            return

        
        up, down, left, right = None, None, None, None
        pressed = (x, y)
        if pressed[1] > 0:
            up = self.functional_maze[pressed[1]-1][pressed[0]]
        if pressed[1] < self.maze_dims[1]-1:
            down = self.functional_maze[pressed[1]+1][pressed[0]]
        if pressed[0] > 0:
            left = self.functional_maze[pressed[1]][pressed[0]-1]
        if pressed[0] < self.maze_dims[0]-1:
            right = self.functional_maze[pressed[1]][pressed[0]+1]
        #print(self.check_cycles(), self.graph.edges)

        elligible = [False, False, False, False]

        if up is not None:
            if self.count_connections(self.name_to_joins(ids[up])) < 3 and self.name_to_joins(ids[up])[0] == False and up != -1:
                self.graph.add_edge(self.coord_to_name(pressed[0], pressed[1]-1), self.coord_to_name(pressed[0], pressed[1]) )
                if not self.check_cycles():
                    elligible[0] = True
                self.graph.remove_edge(self.coord_to_name(pressed[0], pressed[1]-1), self.coord_to_name(pressed[0], pressed[1]) )
                
        if left is not None:
            if self.count_connections(self.name_to_joins(ids[left])) < 3 and self.name_to_joins(ids[left])[2] == False and left != -1:
                self.graph.add_edge(self.coord_to_name(pressed[0]-1, pressed[1]), self.coord_to_name(pressed[0], pressed[1]) )
                if not self.check_cycles():
                    elligible[1] = True
                self.graph.remove_edge(self.coord_to_name(pressed[0]-1, pressed[1]), self.coord_to_name(pressed[0], pressed[1]) )
        if right is not None:
            if self.count_connections(self.name_to_joins(ids[right])) < 3 and self.name_to_joins(ids[right])[1] == False and right != -1:
                self.graph.add_edge(self.coord_to_name(pressed[0]+1, pressed[1]), self.coord_to_name(pressed[0], pressed[1]) )
                if not self.check_cycles():
                    elligible[2] = True
                self.graph.remove_edge(self.coord_to_name(pressed[0]+1, pressed[1]), self.coord_to_name(pressed[0], pressed[1]) )
        if down is not None:
            if self.count_connections(self.name_to_joins(ids[down])) < 3 and self.name_to_joins(ids[down])[3] == False and down != -1:
                self.graph.add_edge(self.coord_to_name(pressed[0], pressed[1]+1), self.coord_to_name(pressed[0], pressed[1]) )
                if not self.check_cycles():
                    elligible[3] = True
                self.graph.remove_edge(self.coord_to_name(pressed[0], pressed[1]+1), self.coord_to_name(pressed[0], pressed[1]) )
        
        print(elligible)
        count = sum([1 for x in elligible if x])
        if count >1:
            last = [False, False, False, False]
            if pressed[0] == self.last_pressed[0] and pressed[1] == self.last_pressed[1]+1:
                last[0] = True
            elif pressed[0] == self.last_pressed[0]+1 and pressed[1] == self.last_pressed[1]:
                last[1] = True
            elif pressed[0]+1 == self.last_pressed[0] and pressed[1] == self.last_pressed[1]:
                last[2] = True
            elif pressed[0] == self.last_pressed[0] and pressed[1] == self.last_pressed[1]-1:
                last[3] = True
            anded = []
            if last != [False, False, False, False]:
                for n in range(4):
                    if last[n] and elligible[n]:
                        anded.append(True)
                    else:
                        anded.append(False)
                elligible = anded

        count = sum([1 for x in elligible if x])
        if count > 1:
            choices = ["up", "left", "right", "down"]
            available = [choices[i] for i in range(4) if elligible[i]]
            
            w = tk.Toplevel()
            label = tk.Label(w, text="Please choose which to connect to:" + ", ".join(available))
            label.pack(fill='x', padx=50, pady=5)
            for n, a in enumerate(available):
                button_close = tk.Button(w, text=a, command=lambda a=a: self.choose(a, w))
                button_close.pack(fill='x')

            self.wait_window(w)
            elligible = [False, False, False, False]
            elligible[choices.index(self.choice)] = True

        if elligible[0]:
            self.graph.add_edge(self.coord_to_name(pressed[0], pressed[1]-1), self.coord_to_name(pressed[0], pressed[1]) )
            conn = self.name_to_joins(ids[up])
            conn[0] = True
            self.set_square(pressed[0], pressed[1]-1, self.make_img_name(conn[0], conn[1], conn[2], conn[3]))
            self.set_square(pressed[0], pressed[1], self.make_img_name(0, 0, 0, 1))
        if elligible[1]:
            self.graph.add_edge(self.coord_to_name(pressed[0]-1, pressed[1]), self.coord_to_name(pressed[0], pressed[1]) )
            conn = self.name_to_joins(ids[left])
            conn[2] = True
            self.set_square(pressed[0]-1, pressed[1], self.make_img_name(conn[0], conn[1], conn[2], conn[3]))
            self.set_square(pressed[0], pressed[1], self.make_img_name(0, 1, 0, 0))
        if elligible[2]:
            self.graph.add_edge(self.coord_to_name(pressed[0]+1, pressed[1]), self.coord_to_name(pressed[0], pressed[1]) )
            conn = self.name_to_joins(ids[right])
            conn[1] = True
            self.set_square(pressed[0]+1, pressed[1], self.make_img_name(conn[0], conn[1], conn[2], conn[3]))
            self.set_square(pressed[0], pressed[1], self.make_img_name(0, 0, 1, 0))
        if elligible[3]:
            self.graph.add_edge(self.coord_to_name(pressed[0], pressed[1]+1), self.coord_to_name(pressed[0], pressed[1]) )
            conn = self.name_to_joins(ids[down])
            conn[3] = True
            self.set_square(pressed[0], pressed[1]+1, self.make_img_name(conn[0], conn[1], conn[2], conn[3]))
            self.set_square(pressed[0], pressed[1], self.make_img_name(1, 0, 0, 0))
        self.last_pressed = pressed
    
    def choose(self, x, w):
        self.choice = x
        w.destroy()
    
    def set_square(self, x, y, i):
        self.canvas.delete(self.buttons[(x*self.maze_dims[1])+y])
        img = ImageTk.PhotoImage(Image.open(base_path + "images/"+ i))
        #self.canvas.create_image(x*50, y*50, anchor=tk.NW, image=img) 
        b = tk.Button(self.canvas, image=img, command=lambda x=x, y=y, i=i: self.toggle_pressed(x, y, i), relief=tk.FLAT)
        b_window = self.canvas.create_window(x*50, y*50, width=50, height=50, anchor=tk.NW, window=b)
        self.buttons[(x*self.maze_dims[1])+y] = b_window

        self.imgs.append(img)
        self.functional_maze[y][x] = ids.index(i)
    
    def toggle_pressed(self, x, y, f):
        if self.count_connections(self.name_to_joins(f)) == 1:
            self.set_square(x, y, ids[ids.index(f)-4])


x = MapperOptions()

x.mainloop()
