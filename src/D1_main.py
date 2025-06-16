from D1_graph_structure import Graph_Struct
import sys
import io
import os

def main():
    print("=== Projet SM601 - Ordonnancement ===")

    while True:
        filename = input("\nEntrez le chemin du fichier de contraintes (.txt) ou 'exit' pour quitter : ").strip()
        if filename.lower() == "exit":
            print("Fin du programme.")
            break

        try:
            buffer = io.StringIO()
            sys.stdout = buffer

            graph = Graph_Struct(filename)

            print(f"Fichier : {filename}\n")
            print(graph.to_str_graph_creation())
            print(graph.to_str_matrix())
            print(graph.is_valid[1])

            if graph.is_valid[0]:
                print(graph.to_str_ranks())
                print(graph.to_str_dates())
                print(graph.to_str_critical_paths())

            sys.stdout = sys.__stdout__
            output = buffer.getvalue()
            print(output)

            save = input("Souhaitez-vous enregistrer les résultats dans un fichier texte ? (o/n) : ").strip().lower()
            if save == "o":
                base_name = os.path.basename(filename).replace(".txt", "")
                output_filename = f"output_{base_name}.txt"
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"\u2705 Résultats enregistrés dans : {output_filename}")

        except FileNotFoundError:
            sys.stdout = sys.__stdout__
            print(f"\u274c Fichier '{filename}' introuvable.")
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(f"\u274c Erreur lors du traitement : {e}")

        again = input("\nSouhaitez-vous tester un autre fichier ? (o/n) : ").strip().lower()
        if again != 'o':
            print("Fin du programme.")
            break

if __name__ == "__main__":
    main()
