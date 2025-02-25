import requests  # Module pour effectuer des requêtes HTTP
import tkinter as tk  # Module pour l'interface graphique
from tkinter import ttk, messagebox  # Widgets avancés et boîtes de dialogue
from PIL import Image, ImageTk  # Manipulation et affichage d'images
import io  # Gestion des flux d'entrée/sortie pour les images
import random  # Génération de nombres aléatoires
import time  # Gestion du temps (ex: pauses)

class PokedexApp:
    def __init__(self, root):
        """Initialisation de l'application Pokédex."""
        self.root = root
        self.root.title("Pokédex")  # Définition du titre de la fenêtre
        self.root.geometry("1280x720")  # Définition des dimensions de base
        self.root.state('zoomed')  # Ouvre la fenêtre en mode maximisé
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Gestion de la fermeture
        self.create_widgets()  # Création de l'interface utilisateur
        self.pokemon_data = {}  # Dictionnaire contenant les données des Pokémon
        self.team1 = []  # Liste pour l'équipe 1
        self.team2 = []  # Liste pour l'équipe 2
        self.load_pokemon_data()  # Chargement des données des Pokémon
        print("Ouverture du Pokédex")

    def create_widgets(self):
        """Création et agencement des widgets de l'interface graphique."""
        style = ttk.Style()
        # Configuration du style des boutons, labels, entrées et listes
        style.configure("TButton", font=("Helvetica", 10), padding=10)
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("TListbox", font=("Helvetica", 10))

        # Cadre principal de l'application
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Création d'un canvas pour supporter le défilement
        canvas = tk.Canvas(main_frame, bg="#f0f0f0")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Barre de défilement verticale
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Lier la barre de défilement au canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Création d'un second cadre à l'intérieur du canvas
        second_frame = tk.Frame(canvas, bg="#f0f0f0")
        canvas.create_window((0, 0), window=second_frame, anchor="nw")

        # Configuration du positionnement des colonnes
        second_frame.grid_columnconfigure(0, weight=1)
        second_frame.grid_columnconfigure(1, weight=1)
        second_frame.grid_columnconfigure(2, weight=1)

        # Label et champ de recherche
        self.search_label = ttk.Label(second_frame, text="Rechercher un Pokémon:", background="#f0f0f0")
        self.search_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.search_entry = ttk.Entry(second_frame)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.search_button = ttk.Button(second_frame, text="Rechercher", command=self.search_pokemon)
        self.search_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Liste des Pokémon disponibles
        self.pokemon_listbox = tk.Listbox(second_frame, font=("Helvetica", 10), bg="#ffffff", bd=2, relief="groove")
        self.pokemon_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.pokemon_listbox.bind('<<ListboxSelect>>', self.display_pokemon_info)
        
        # Label pour afficher les informations du Pokémon sélectionné
        self.pokemon_info_label = ttk.Label(second_frame, text="", justify=tk.LEFT, background="#f0f0f0")
        self.pokemon_info_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        
        # Zone pour afficher l'image du Pokémon
        self.pokemon_image_label = tk.Label(second_frame, bg="#f0f0f0")
        self.pokemon_image_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Boutons pour ajouter/retirer des Pokémon aux équipes
        self.add_to_team1_button = ttk.Button(second_frame, text="Ajouter à l'équipe 1", command=self.add_to_team1)
        self.add_to_team1_button.grid(row=4, column=0, padx=10, pady=10)

        self.remove_from_team1_button = ttk.Button(second_frame, text="Retirer de l'équipe 1", command=self.remove_from_team1)
        self.remove_from_team1_button.grid(row=4, column=1, padx=10, pady=10)

        self.team1_label = ttk.Label(second_frame, text="Équipe 1 de Pokémon:", justify=tk.LEFT, background="#f0f0f0")
        self.team1_label.grid(row=5, column=0, padx=10, pady=10)

        self.team1_listbox = tk.Listbox(second_frame, font=("Helvetica", 10), bg="#ffffff", bd=2, relief="groove")
        self.team1_listbox.grid(row=6, column=0, padx=10, pady=10)

        # Équipe 2
        self.add_to_team2_button = ttk.Button(second_frame, text="Ajouter à l'équipe 2", command=self.add_to_team2)
        self.add_to_team2_button.grid(row=4, column=2, padx=10, pady=10)

        self.remove_from_team2_button = ttk.Button(second_frame, text="Retirer de l'équipe 2", command=self.remove_from_team2)
        self.remove_from_team2_button.grid(row=4, column=3, padx=10, pady=10)

        self.team2_label = ttk.Label(second_frame, text="Équipe 2 de Pokémon:", justify=tk.LEFT, background="#f0f0f0")
        self.team2_label.grid(row=5, column=2, padx=10, pady=10)

        self.team2_listbox = tk.Listbox(second_frame, font=("Helvetica", 10), bg="#ffffff", bd=2, relief="groove")
        self.team2_listbox.grid(row=6, column=2, padx=10, pady=10)

        # Bouton pour démarrer un combat
        self.battle_button = ttk.Button(second_frame, text="Commencer le combat", command=self.start_battle)
        self.battle_button.grid(row=7, columnspan=3, pady=20)

    def load_pokemon_data(self):
        """Charge les données des Pokémon depuis l'API."""
        for i in range(1, 152):  # Limite aux 151 premiers Pokémon
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}")
            if response.status_code == 200:
                data = response.json()
                self.pokemon_data[data['name']] = data
                self.pokemon_listbox.insert(tk.END, data['name'])

    def search_pokemon(self):
        """Recherche un Pokémon dans la liste et affiche ses informations."""
        search_term = self.search_entry.get().lower()
        if search_term in self.pokemon_data:
            index = list(self.pokemon_data.keys()).index(search_term)
            self.pokemon_listbox.selection_clear(0, tk.END)
            self.pokemon_listbox.selection_set(index)
            self.pokemon_listbox.activate(index)
            self.display_pokemon_info(search_term)
        else:
            self.pokemon_info_label.config(text="Pokémon non trouvé.")
            self.pokemon_image_label.config(image='')
    
    def display_pokemon_info(self, event=None):
        """Affiche les informations et l'image du Pokémon sélectionné."""
        if event:
            if isinstance(event, str):
                selected_pokemon = event  # Si l'événement est une chaîne, on l'utilise directement
            else:
                selection = self.pokemon_listbox.curselection()  # Récupération de la sélection dans la liste
                if selection:
                    selected_pokemon = self.pokemon_listbox.get(selection)
                else:
                    return
        else:
            return

        # Récupération des données du Pokémon sélectionné
        pokemon = self.pokemon_data[selected_pokemon]
        info = f"Nom: {pokemon['name'].capitalize()}\n"
        info += f"ID: {pokemon['id']}\n"
        info += f"Taille: {pokemon['height']}\n"
        info += f"Poids: {pokemon['weight']}\n"
        info += f"Types: {', '.join([t['type']['name'] for t in pokemon['types']])}\n"
        
        self.pokemon_info_label.config(text=info)  # Mise à jour du label avec les infos du Pokémon
        
        # Chargement et affichage de l'image du Pokémon
        image_url = pokemon['sprites']['front_default']
        if image_url:
            image_response = requests.get(image_url)
            image_data = image_response.content
            image = Image.open(io.BytesIO(image_data))
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.pokemon_image_label.config(image=photo)
            self.pokemon_image_label.image = photo  # Important pour éviter la suppression de l'image par le garbage collector

    def add_to_team1(self):
        """Ajoute un Pokémon sélectionné à l'équipe 1, avec une limite de 5 Pokémon."""
        selection = self.pokemon_listbox.curselection()
        if selection and len(self.team1) < 5:
            selected_pokemon = self.pokemon_listbox.get(selection)
            if selected_pokemon not in [p['name'] for p in self.team1]:
                pokemon = self.pokemon_data[selected_pokemon]
                self.team1.append(pokemon)
                self.team1_listbox.insert(tk.END, selected_pokemon)
            else:
                messagebox.showerror("Erreur", "Ce Pokémon est déjà dans l'équipe 1.")
        elif len(self.team1) >= 5:
            messagebox.showerror("Erreur", "Vous ne pouvez pas ajouter plus de 5 Pokémon à l'équipe 1.")

    def remove_from_team1(self):
        """Retire un Pokémon sélectionné de l'équipe 1."""
        selection = self.team1_listbox.curselection()
        if selection:
            selected_pokemon = self.team1_listbox.get(selection)
            self.team1 = [p for p in self.team1 if p['name'] != selected_pokemon]
            self.team1_listbox.delete(selection)

    def add_to_team2(self):
        """Ajoute un Pokémon sélectionné à l'équipe 2, avec une limite de 5 Pokémon."""
        selection = self.pokemon_listbox.curselection()
        if selection and len(self.team2) < 5:
            selected_pokemon = self.pokemon_listbox.get(selection)
            if selected_pokemon not in [p['name'] for p in self.team2]:
                pokemon = self.pokemon_data[selected_pokemon]
                self.team2.append(pokemon)
                self.team2_listbox.insert(tk.END, selected_pokemon)
            else:
                messagebox.showerror("Erreur", "Ce Pokémon est déjà dans l'équipe 2.")
        elif len(self.team2) >= 5:
            messagebox.showerror("Erreur", "Vous ne pouvez pas ajouter plus de 5 Pokémon à l'équipe 2.")

    def remove_from_team2(self):
        """Retire un Pokémon sélectionné de l'équipe 2."""
        selection = self.team2_listbox.curselection()
        if selection:
            selected_pokemon = self.team2_listbox.get(selection)
            self.team2 = [p for p in self.team2 if p['name'] != selected_pokemon]
            self.team2_listbox.delete(selection)

    def start_battle(self):
        """Lance un combat entre les deux équipes, si elles sont valides."""
        if len(self.team1) < 1 or len(self.team2) < 1:
            messagebox.showerror("Erreur", "Les deux équipes doivent avoir au moins un Pokémon pour commencer le combat.")
            return
        if len(self.team1) != len(self.team2):
            messagebox.showerror("Erreur", "Les deux équipes doivent avoir le même nombre de Pokémon pour commencer le combat.")
            return

        # Création d'une nouvelle fenêtre pour le combat
        battle_window = tk.Toplevel(self.root)
        battle_window.title("Combat en cours")

        # Chargement de l'image de fond (stade de combat)
        background_image = Image.open("stadium.png")  # Assurez-vous que l'image existe
        background_photo = ImageTk.PhotoImage(background_image)
    
        # Redimensionnement de la fenêtre en fonction de l'image
        battle_window.geometry(f"{background_photo.width()}x{background_photo.height()}")

        background_label = tk.Label(battle_window, image=background_photo)
        background_label.place(relwidth=1, relheight=1)

        # Barre de progression pour simuler le combat
        progress = ttk.Progressbar(battle_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress.pack(pady=20)

        def update_progress():
            """Simule une progression du combat avec une barre de chargement."""
            for i in range(5):
                progress['value'] += 20
                battle_window.update_idletasks()
                time.sleep(1)
            battle_window.destroy()
            self.show_battle_result()

        battle_window.after(100, update_progress)
        battle_window.mainloop()

    def show_battle_result(self):
        """Affiche le résultat du combat en comparant les statistiques des équipes."""
        result_message = "Combat terminé!\n\n"
        team1_wins = 0
        team2_wins = 0
        
        for i in range(min(len(self.team1), len(self.team2))):
            team1_pokemon = self.team1[i]
            team2_pokemon = self.team2[i]
            
            # Calcul de la puissance totale basée sur les statistiques de base
            team1_power = sum(stat['base_stat'] for stat in team1_pokemon['stats'])
            team2_power = sum(stat['base_stat'] for stat in team2_pokemon['stats'])
            
            if team1_power > team2_power:
                result_message += f"{team1_pokemon['name'].capitalize()} a battu {team2_pokemon['name'].capitalize()}!\n"
                team1_wins += 1
            elif team1_power < team2_power:
                result_message += f"{team2_pokemon['name'].capitalize()} a battu {team1_pokemon['name'].capitalize()}!\n"
                team2_wins += 1
            else:
                result_message += f"{team1_pokemon['name'].capitalize()} et {team2_pokemon['name'].capitalize()} sont à égalité!\n"

        # Détermination du vainqueur
        if team1_wins > team2_wins:
            result_message += "\nÉquipe 1 est la gagnante!"
        elif team2_wins > team1_wins:
            result_message += "\nÉquipe 2 est la gagnante!"
        else:
            result_message += "\nLes deux équipes sont à égalité!"

        messagebox.showinfo("Résultat du combat", result_message)

    def on_closing(self):
        """Ferme proprement l'application."""
        print("Fermeture du Pokédex")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexApp(root)
    root.mainloop()
