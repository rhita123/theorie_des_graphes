from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter.ttk import *
from D1_graph_structure import *
import os

class Application(Frame):
    def __init__(self, root):
        """
       Initialise tout le contenu visuel de la fenêtre principale de l'application.
        
        :param root: Fenêtre principale de l'application
        """
        Frame.__init__(self, root)
        self.root = root
        self.root.title("Projet des graphes")
        self.root.geometry("1280x720+100+100")
        self.root.configure(bg="white")
        self.root.resizable(True, True)
        self.dict_files = None
        self.text_area1 = None
        self.text_area2 = None
        self.build_menubar()
        self.build_tabcontrol()
    
    def openfiles(self):
        """
         Permet à l'utilisateur de choisir plusieurs fichiers texte depuis son ordinateur.
        Les fichiers sélectionnés sont enregistrés dans un dictionnaire.
        """
        files = filedialog.askopenfilenames(
            initialdir="./",
            title="Choisissez les fichiers textes à ouvrir",
            filetypes=[("Fichier texte", ".txt")])
        self.dict_files = dict()

        for file in files :
            self.dict_files[os.path.basename(file)] = (file, None)

        self.build_menubar()

    def build_tabcontrol(self):
        """
       Crée les deux onglets de l'interface :
        - un pour afficher le fichier brut,
        - un pour afficher les résultats du traitement du graphe.
        """
        tabControl = Notebook(self.root)
        self.tab1 = Frame(tabControl)
        self.tab2 = Frame(tabControl)
        self.labelPrev1 = Label(self.tab1, text = "Aucun fichier n'a été chargé")
        self.labelPrev1.pack()
        self.labelPrev2 = Label(self.tab2, text = "Aucun fichier n'a été chargé")
        self.labelPrev2.pack()

        tabControl.add(self.tab1, text = "Fichier brut")
        tabControl.add(self.tab2, text = "Logs traitement")
        tabControl.pack(expand = 1, fill ="both")

    def build_menubar(self):
        """
        Crée le menu en haut de la fenêtre.
        - Si aucun fichier n’est encore chargé : propose juste d’ouvrir un fichier ou quitter.
        - Si des fichiers sont chargés : ajoute un sous-menu permettant de choisir quel graphe traiter.
        """
        if not self.dict_files:
            self.menubar1 = Menu(self.root)
            menu_file = Menu(self.menubar1, tearoff=0)
            menu_file.add_command(label="Ouvrir", command=self.openfiles)
            menu_file.add_separator()
            menu_file.add_command(label="Quitter", command=self.quit)
            self.menubar1.add_cascade(label="Fichier", menu=menu_file)
            self.root.config(menu=self.menubar1)
        
        else:
            self.menubar2 = Menu(self.root)
            menu_file = Menu(self.menubar2, tearoff=0)
            menu_file.add_command(label="Ouvrir", command=self.openfiles)
            menu_file.add_separator()
            menu_file.add_command(label="Quitter", command=self.quit)
            self.menubar2.add_cascade(label="Fichier", menu=menu_file)

            menu_graphs = Menu(self.menubar2, tearoff=0)
            for filename in self.dict_files.keys():
                menu_graphs.add_command(label=filename, command = lambda k=filename: self.execute(k))
            self.menubar2.add_cascade(label="Graphes", menu=menu_graphs)
            self.root.config(menu=self.menubar2)

    def execute(self, filename):
        """
       Traite le graphe associé au fichier sélectionné.
        Affiche toutes les informations (graphe, matrice, rangs, marges, chemin critique...),
        et les enregistre dans un fichier texte dans le dossier output_files.
        
        :param filename: Nom du fichier sélectionné (clé du dictionnaire self.dict_files)
        """
        g = Graph_Struct(self.dict_files[filename][0])
        res = "Fichier : " + filename + "\n" + g.to_str_graph_creation() + "\n" + g.to_str_matrix() + "\n"+ (g.is_valid[1] + "\n"+ g.to_str_ranks() + "\n" + g.to_str_dates() + "\n" + g.to_str_critical_paths() if g.is_valid[0] else g.is_valid[1])
        self.dict_files[filename] = (self.dict_files[filename][0], g)
        self.labelPrev1.pack_forget()

        file = open("./output_files/D1_" + filename, "w", encoding='utf-8')
        file.write(res)
        file.close()

        if not self.text_area1 and not self.text_area2 :
            self.text_area1 = Text(self.tab1)
            self.text_area1.insert("1.0", g.raw_data)
            self.text_area1.config(state=DISABLED)
            self.text_area1.pack(expand = 1, fill ="both")

            self.labelPrev2.pack_forget()
            self.text_area2 = Text(self.tab2)
            self.text_area2.insert("1.0", res)
            self.text_area2.config(state=DISABLED)
            self.text_area2.pack(expand = 1, fill ="both")
        else :
            self.text_area1.config(state=NORMAL)
            self.text_area1.delete('1.0', END)
            self.text_area1.insert("1.0", g.raw_data)
            self.text_area1.config(state=DISABLED)

            self.text_area2.config(state=NORMAL)
            self.text_area2.delete('1.0', END)
            self.text_area2.insert("1.0", res)
            self.text_area2.config(state=DISABLED)

    def build_textarea(self):
        """
         Crée une zone de texte avec barre de défilement pour afficher les résultats
        ou les fichiers chargés dans l’interface.
        """
        text_area = scrolledtext.ScrolledText(self.root, wrap=WORD,
        width=40,
        height=8,
        font=("Times New Roman", 15))
        text_area.pack()
        text_area.focus()