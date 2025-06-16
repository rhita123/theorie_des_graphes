import os
import copy
from queue import Queue

class Graph_Struct():
    def __init__(self, filepath):
        """
        Constructeur de la classe Graph_Struct.
        lit le fichier texte, construit le dictionnaire du graphe, crée la matrice et lance les calculs
        """
        self.filepath = filepath
        self.name = os.path.basename(filepath)
        self.raw_data = Graph_Struct.read_file(self.filepath)
        self.dict_graph = Graph_Struct.parse_raw_data(self.raw_data)
        self.node_count = len(self.dict_graph)
        self.matrix = self.create_matrix()
        self.arc_count = 0

        for node in self.dict_graph:
            for _ in self.dict_graph[node][1]:
                self.arc_count += 1
        
        self.is_valid = self.verify_graph()
        if self.is_valid[0]:
            self.ranks_computing()
            self.compute_dates()
            self.critical_paths()

    def read_file(filepath):
        """
        Lit le contenu d'un fichier texte et le renvoie sous forme de chaîne de caractères
        """
        file = open(filepath, "r")
        res = file.read()
        file.close()
        return res

    def parse_raw_data(raw_data):
        """
        Transforme les données brutes du fichier texte en dictionnaire :
        chaque tâche est associée à sa durée et à ses prédécesseurs.
        """
        res = dict()
        nodes_in = []
        raw_data_lines = raw_data.split('\n')
        max = '0'
        for line in raw_data_lines:
            raw_vals = line.split(' ')
            preds = []
            idx = 0

            if raw_vals[0].isnumeric():
                if int(raw_vals[0]) > int(max):
                    max = raw_vals[0]
                for val in raw_vals:
                    if val.isnumeric():
                        if idx != 0 and idx != 1:
                            nodes_in.append(val)
                            preds.append(val)
                    idx += 1  

                if preds == []:
                    preds.append('0')
                res[raw_vals[0]] = (raw_vals[1], preds)

        ending_nodes = []
        for key in res.keys():
            if key not in nodes_in:
                ending_nodes.append(key)
        
        res[str(int(max)+1)] = (str(0), ending_nodes)
        res['0'] = (str(0), [])

        return res

    def create_matrix(self):
        """
       Crée la matrice des valeurs (matrice d'adjacence) du graphe.
        Les cases contiennent les durées ou un * si aucun lien.
        """
        matrix = []
        for _ in range(self.node_count):
            line = []
            for _ in range(self.node_count):
                line.append('*')
            matrix.append(line)
            
        for i in range(self.node_count):
            node = str(i)
            for pred in self.dict_graph[node][1]:
                matrix[int(pred)][i] = self.dict_graph[pred][0]
        return matrix

    def to_str_graph_creation(self):
        """
       Renvoie une chaîne de caractères contenant les informations sur la création du graphe.
       Nombre de sommets, arcs, et triplets source -> destination = durée.
        """
        res = "Création du graphe d'ordonnancement :\n"
        res += "Nombre de sommets : " + str(self.node_count) + "\n"
        res += "Nombre d'arcs : " + str(self.arc_count) + "\n"

        for i in range(self.node_count):
            node = str(i)
            for j in range(self.node_count):
                current_node = str(j)
                if str(node) in self.dict_graph[current_node][1]:
                    res += node + " -> " + current_node + " = " + self.dict_graph[node][0] + "\n"
        return res
    
    def to_str_matrix(self):
        """
        Renvoie la matrice des valeurs sous forme textuelle, pour affichage.
        """
        res = "Matrice des valeurs\n"
        
        size = 4
        text = ' ' * size + ' '.join(str(val).ljust(size) for val in range(self.node_count)) + "\n"
        i = 0
        for line in self.matrix:
            text += ' '.join(str(i).ljust(size) for val in [str(i)]) + ' '.join(str(val).ljust(size) for val in line) + "\n"
            i += 1
        return res + text
    
    def to_str_ranks(self):
        """
       Renvoie un texte qui montre à quel rang se trouve chaque sommet.
       utile pour voir si le calcul des rangs a bien marché.
        """
        res = "Rangs des sommets :\n"
        if self.is_valid[0]:
            for i in range(self.node_count):
                res += "Le sommet " + str(i) + " est au rang " + str(self.ranks[str(i)]) + "\n"
            return res
        else:
            return ""
    
    def to_str_dates(self):
        """
        Renvoie une chaîne de caractères qui affiche un tableau des dates au plus tôt,
        des dates au plus tard et des marges totales pour chaque sommet.
        """
        res = "Dates pour chaque sommet\n"
        res += "%-8s%-3s%-25s%-3s%-25s%-3s%-14s" % ("Sommet", "|", "Calendrier au plus tôt", "|", "Calendrier au plus tard", "|", "Marge totale")
        res += "\n"
        for i in range(self.node_count):
            res += "%-8s%-3s%-25s%-3s%-25s%-3s%-14s" % (str(i), "|", str(self.dates[str(i)][0]), "|", str(self.dates[str(i)][1]), "|", str(self.dates[str(i)][2]))
            res += "\n"
        return res
    
    def to_str_critical_paths(self):
        """
       Renvoie une chaîne de caractères qui affiche tous les chemins critiques du graphe.

        """
        res = "Chemin(s) critique(s)\n"
        for path in self.crit_paths:
            length = len(path)
            for i in range(length):
                if i != length - 1:
                    res += path[i] + " -> "
                else :
                    res += path[i] + "\n"
        return res

    def verify_graph(self):
        """
        Vérifie si le graphe est un graphe d'ordonnancement.
    1. Vérifie que tous les arcs ont une valeur positive.
    2. Détecte s'il existe un circuit dans le graphe (chemin qui revient au même sommet).

        """
        is_valid = True
        res = "Vérification des arcs du graphe\n"

        # Détection des arcs negatifs
        for i in range(self.node_count):
            node = str(i)
            if int(self.dict_graph[node][0]) < 0:
                is_valid = False
                res += "Les arcs partant du sommet " +  node + " ont la valeur négative : " + self.dict_graph[node][0] + "\n"
        if is_valid:
            res += "Le graphe ne possède pas d'arc à valeur négative\n"
        
        res += "\nDétection de circuit (Parcours largeur)\n"
        # Détection de circuits
        for i in range(self.node_count):
            bfs_res = self.breadth_firs_search(str(i), str(i))
            if bfs_res != []:
                is_valid = False
                res += "Chemin du sommet " + str(i) + " au sommet " + str(i) + " (Circuit : "
                len_bfs_res = len(bfs_res)
                for i in range(len_bfs_res):
                    if i != len_bfs_res - 1:
                        res += bfs_res[i] + " -> "
                    else :
                        res +=bfs_res[i] + ")\n"
            else:
                res += "Pas de chemin du sommet " + str(i) + " au sommet " + str(i) + "\n"
        
        if not is_valid:
            res += "Ce graphe n'est pas un graphe d'ordonnancement.\nAinsi il est impossible d'executer le calcul des rangs, du calendrier au plus tôt, du calendrier au plus tard et des marges.\n" 
        else:
            res += "Ce graphe est un graphe d'ordonnancement\n"
        return (is_valid, res)
    
    def breadth_firs_search(self, start_node, end_node):
        """
       Recherche un chemin entre deux sommets du graphe en utilisant un parcours en largeur.

    :param start_node: sommet de départ (sous forme de chaîne)
    :param end_node: sommet d'arrivée (sous forme de chaîne)
    :return: liste des sommets du chemin trouvé (ou [] s'il n'existe pas)
        """
        fifo = Queue()
        visited = [False] * self.node_count
        fifo.put((start_node, [start_node]))

        while not fifo.empty():
            (node, current_path) = fifo.get()
            visited[int(node)] = True
            adjacent_list = self.matrix[int(node)]

            for neighbor in range(self.node_count):
                if adjacent_list[neighbor] != "*" and visited[int(neighbor)] == False:
                    new_current_path = copy.deepcopy(current_path)
                    new_current_path.append(str(neighbor))
                    fifo.put((str(neighbor), new_current_path))
                elif adjacent_list[neighbor] != "*" and str(neighbor) == end_node:
                    new_current_path = copy.deepcopy(current_path)
                    new_current_path.append(str(neighbor))
                    return new_current_path
        return []
    
    def critical_paths(self):
        """
       Lance la recherche de tous les chemins critiques du graphe.
        Elle démarre au sommet 0 et utilise une fonction récursive pour explorer les chemins.
        """
        self.crit_paths = []
        self.critical_paths_rec('0', "0", 0)

    def critical_paths_rec(self, node, path, count):
        """
       Fonction récursive utilisée pour trouver tous les chemins critiques.
        Si on est arrivé au dernier sommet avec la durée totale attendue, on enregistre le chemin.
        Sinon, on continue à explorer les successeurs.
    
    :param node: sommet actuel (en chaîne de caractères)
    :param path: chemin parcouru jusqu'à présent (sous forme de texte)
    :param count: durée totale cumulée du chemin actuel
        """
        if node == str(self.node_count - 1) and self.dates[str(self.node_count - 1)][1] == count:
            res = path.split(",")
            self.crit_paths.append(res)
        else :
            for neighbor in range(self.node_count):
                if self.matrix[int(node)][neighbor] != "*":
                    self.critical_paths_rec(str(neighbor), path + "," + str(neighbor), count + int(self.dict_graph[str(neighbor)][0]))

    def ranks_computing(self):
        """
       Fonction principale qui initialise et lance le calcul des rangs de chaque sommet.
    Elle appelle une fonction récursive pour déterminer le rang de chaque tâche.
    Elle prépare aussi un dictionnaire inversé pour organiser les sommets par rang.
        """
        self.ranks = dict()
        self.ranks['0'] = 0
        self.ranks_computing_rec('0')

        self.ranks_dict_reverted = dict()
        for key in self.ranks:
            if self.ranks[key] not in self.ranks_dict_reverted.keys():
                self.ranks_dict_reverted[self.ranks[key]] = [key]
            else:
                self.ranks_dict_reverted[self.ranks[key]].append(key)

    def ranks_computing_rec(self, node):
        """
        Fonction récursive qui calcule le rang d’un sommet à partir de ses prédécesseurs.
    Si un sommet n’a pas encore de rang, on lui en attribue un.
    Si son rang actuel peut être amélioré, on le met à jour.

    :param node: sommet actuel (sous forme de chaîne)
        """
        for i in range(self.node_count):
            neighbor = str(i)
            neighbor_value = self.matrix[int(node)][i]
            if neighbor_value != "*":
                if neighbor not in self.ranks.keys():
                    self.ranks[neighbor] = self.ranks[node] + 1
                    self.ranks_computing_rec(neighbor)
                elif self.ranks[neighbor] < self.ranks[node] + 1:
                    self.ranks[neighbor] = self.ranks[node] + 1
                    self.ranks_computing_rec(neighbor)

    def compute_dates(self):
        """
         Calcule le calendrier au plus tôt, au plus tard, et la marge totale pour chaque sommet.
    - D'abord, on parcourt le graphe de gauche à droite (du début vers la fin) pour les dates au plus tôt.
    - Ensuite, on repart de droite à gauche (de la fin vers le début) pour les dates au plus tard.
    - Enfin, on calcule la marge comme la différence entre les deux.
        """
        self.dates = dict()
        for node in range(self.node_count):
            self.dates[str(node)] = [0, 0, 0]
        self.dates['0'][0] = 0

        for i in range(1, len(self.ranks_dict_reverted)):
            for node in self.ranks_dict_reverted[i]:
                max_val = 0
                for pred in range(self.node_count):
                    if self.matrix[pred][int(node)] != "*":
                        new_val = self.dates[str(pred)][0] + int(self.dict_graph[str(pred)][0])
                        if max_val < new_val:
                            max_val = new_val
                self.dates[node][0] = max_val
        
        self.dates[str(self.node_count-1)][1] = self.dates[str(self.node_count-1)][0]
        for i in reversed(range(0, len(self.ranks_dict_reverted) - 1)):
            for node in self.ranks_dict_reverted[i]:
                min_val = -1
                for succ in range(self.node_count):
                    if self.matrix[int(node)][succ] != "*":
                        new_val = self.dates[str(succ)][1] - int(self.dict_graph[node][0])
                        if min_val == -1 or min_val > new_val:
                            min_val = new_val
                self.dates[node][1] = min_val
        
        for node in range(self.node_count):
            self.dates[str(node)][2] = self.dates[str(node)][1] - self.dates[str(node)][0]