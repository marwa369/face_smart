import tkinter as tk
from tkinter import messagebox
import sqlite3
import cv2
from PIL import Image, ImageTk
import io
import face_recognition
import json
import datetime

# Connexion à la base de données
conn = sqlite3.connect('don.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS employes (
                    id INTEGER PRIMARY KEY,
                    nom TEXT,
                    prenom TEXT,
                    date_debut TEXT,
                    date_fin TEXT,
                    poste TEXT,
                    departement TEXT,
                    photo BLOB,
                    face text )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS horaires (
                    id INTEGER PRIMARY KEY,
                    employe_id INTEGER,
                    temps_arrivee TEXT,
                    temps_depart TEXT,
                    FOREIGN KEY (employe_id) REFERENCES employes(id))''')
conn.commit()



   
def pointer_arriver():
    try:
        # Ouvrir la caméra
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            messagebox.showerror("Erreur", "Impossible de capturer l'image de la webcam.")
            return
        
        # Conversion pour face_recognition
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(frame_rgb)

        if not face_encodings:
            messagebox.showerror("Erreur", "Aucun visage détecté.")
            return
        
        # Récupérer les encodages de la base de données
        face_encoding = face_encodings[0]
        cursor.execute("SELECT id, face FROM employes")
        rows = cursor.fetchall()

        # Comparer avec ceux de la base de données
        for row in rows:
            employe_id = row[0]
            employe_face = json.loads(row[1])

            match = face_recognition.compare_faces([employe_face], face_encoding, tolerance=0.6)

            if match[0]:
                heure_arrivee = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO horaires (employe_id, temps_arrivee) VALUES (?, ?)", 
                               (employe_id, heure_arrivee))
                conn.commit()  # Engager la transaction
                messagebox.showinfo("Succès", f"L'employé {employe_id} a pointé à l'heure {heure_arrivee}.")
                return
        
        messagebox.showerror("Erreur", "Aucun employé correspondant trouvé.")

    except sqlite3.OperationalError as e:
        messagebox.showerror("Erreur de base de données", f"Erreur opérationnelle : {str(e)}")
    except Exception as ex:
        messagebox.showerror("Erreur inattendue", f"Une erreur inattendue s'est produite : {str(ex)}")

# Fonction pour pointer le départ
def pointer_depart():
    try:
        # Ouvrir la caméra
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            messagebox.showerror("Erreur", "Impossible de capturer l'image de la webcam.")
            return
        
        # Conversion pour face_recognition
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(frame_rgb)

        if not face_encodings:
            messagebox.showerror("Erreur", "Aucun visage détecté.")
            return
        
        # Récupérer les encodages de la base de données
        face_encoding = face_encodings[0]
        cursor.execute("SELECT id, face FROM employes")
        rows = cursor.fetchall()

        # Comparer avec ceux de la base de données
        for row in rows:
            employe_id = row[0]
            employe_face = json.loads(row[1])

            match = face_recognition.compare_faces([employe_face], face_encoding, tolerance=0.6)

            if match[0]:
                heure_depart = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Vérifier si l'employé a déjà pointé l'arrivée
                cursor.execute("SELECT id FROM horaires WHERE employe_id = ? AND temps_arrivee IS NOT NULL AND temps_depart IS NULL",
                               (employe_id,))
                resultat = cursor.fetchone()

                if resultat:
                    # Ajouter le temps de départ
                    cursor.execute("UPDATE horaires SET temps_depart = ? WHERE id = ?", 
                                   (heure_depart, resultat[0]))
                    conn.commit()  # Engager la transaction
                    messagebox.showinfo("Succès", f"L'employé {employe_id} a pointé à l'heure {heure_depart} pour le départ.")
                    return
                else:
                    messagebox.showerror("Erreur", "L'employé n'a pas pointé l'arrivée aujourd'hui.")
                    return
        
        messagebox.showerror("Erreur", "Aucun employé correspondant trouvé.")

    except sqlite3.OperationalError as e:
        messagebox.showerror("Erreur de base de données", f"Erreur opérationnelle : {str(e)}")
    except Exception as ex:
        messagebox.showerror("Erreur inattendue", f"Une erreur inattendue s'est produite : {str(ex)}")

# Gestion des ressources


def detecter_visages(image, cascade):
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    name="test" 
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(frame_rgb )
    if len(face_encodings) > 0:
            face_encoding = face_encodings[0]
            encoding_str = json.dumps(list(face_encoding))
            # Rechercher des correspondances dans la base de données
            cursor.execute("SELECT face, nom FROM employes")
            rows = cursor.fetchall()

# Convertir les encodages en listes de nombres flottants
            database_encodings = [json.loads(row[0]) for row in rows]
            database_names = [row[1] for row in rows] 
            matches = face_recognition.compare_faces(database_encodings, face_encoding, tolerance=0.6)

            if True in matches:
              match_index = matches.index(True)
              name = database_names[match_index] 
            else:
              name = "Inconnu"
    # Détecter les visages dans l'image
    name = str(name)
    visages = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Dessiner des rectangles autour des visages détectés
    for (x, y, w, h) in visages:
        # Dessiner un rectangle autour du visage
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
       
        # Générer un encodage facial
       
       
        # Ajouter une étiquette avec le nom attribué au visage (remplacer 'NomVisage' par le nom réel)
        cv2.putText(image, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    return image
def demarrer_reconnaissance_faciale():
    

    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)

    # Démarrer la capture vidéo à partir de la webcam
    cap = cv2.VideoCapture(0)

    # Vérifier si la capture vidéo est ouverte
    if not cap.isOpened():
        print("Erreur: la webcam ne peut pas être ouverte.")
        return

    while True:
        # Lire l'image de la webcam
        ret, frame = cap.read()
       
        # Vérifier si la lecture de l'image a réussi
        if not ret:
            print("Erreur: Impossible de lire l'image de la webcam.")
            break
       
        # Détecter les visages dans l'image et afficher le nom attribué à chaque visage
        frame= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = detecter_visages(frame, cascade)
        # Afficher l'image traitée
        cv2.imshow('Reconnaissance faciale', frame)

        key = cv2.waitKey(30)

        
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()




# Fonction pour ajouter un employé
def ajouter_employe():
    nom = nom_entry.get()
    prenom = prenom_entry.get()
    departement = departement_var.get()
    date_debut = date_debut_entry.get()
    date_fin = date_fin_entry.get()
    poste = poste_entry.get()
    cap = cv2.VideoCapture(0)

    # Capturer une seule image
    ret, frame = cap.read()

    # Fermer la webcam
    cap.release()

    if ret:
        # Conversion de l'image en format compatible Tkinter
        image= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir les couleurs
        photo = Image.fromarray(image)  # Créer une image PIL
        photo_tk = ImageTk.PhotoImage(photo)  # Convertir en format Tkinter

        # Enregistrer l'image en mémoire
        image_bytes = io.BytesIO()
        photo.save(image_bytes, format='PNG')  # Sauvegarder l'image au format binaire
        image_bytes.seek(0)
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) > 0:
            face_encoding = face_encodings[0]
            encoding_str = json.dumps(list(face_encoding))
            cursor.execute('''INSERT INTO employes (nom, prenom, departement, date_debut, date_fin, poste , face, photo) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (nom, prenom, departement, date_debut, date_fin, poste,encoding_str,image_bytes.getvalue()))
        

            conn.commit()
    messagebox.showinfo("Succès", "Employé ajouté avec succès !")
    afficher_employes_listbox()

# Fonction pour afficher les employés
def afficher_employes_listbox():
    # Effacer le contenu précédent de la liste
    employes_listbox.delete(0, tk.END)

    # Récupération de tous les employés
    cursor.execute("SELECT id,nom,prenom,departement ,date_debut,date_fin,poste FROM employes")
    employes = cursor.fetchall()

    # Affichage des employés dans la liste
    for employe in employes:
        id, nom, prenom, departement, date_debut, date_fin, poste = employe
        employe_info = f"{id} | {nom} | {prenom} | {departement} | {date_debut} | {date_fin} | {poste}"
        employes_listbox.insert(tk.END, employe_info)

# Fonction pour supprimer un employé
def supprimer_employe():
    # Récupérer l'ID de l'employé sélectionné
    selected_index = employes_listbox.curselection()
    if selected_index:
        id_employe = employes_listbox.get(selected_index)[0]
        if messagebox.askokcancel("Confirmation", "Êtes-vous sûr de vouloir supprimer cet employé ?"):
            cursor.execute("DELETE FROM employes WHERE id=?", (id_employe,))
            conn.commit()
            afficher_employes_listbox()
    else:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un employé à supprimer.")

# Interface utilisateur
root = tk.Tk()
root.geometry("900x600")
root.title("Gestion des employés")

# Frame principale
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Frame pour l'ajout d'un employé
add_frame = tk.LabelFrame(main_frame, text="Ajouter un employé", padx=10, pady=10)
add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Labels et entrées pour l'ajout d'un employé
tk.Label(add_frame, text="Nom:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Label(add_frame, text="Prénom:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Label(add_frame, text="Département:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Label(add_frame, text="Date début:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
tk.Label(add_frame, text="Date fin:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
tk.Label(add_frame, text="Poste:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
departements = ["Production", "Ventes", "Marketing", "Recherche et Développement", "Comptabilité et Finance", "Ressources humaines"]
nom_entry = tk.Entry(add_frame)
nom_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
prenom_entry = tk.Entry(add_frame)
prenom_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
departement_var = tk.StringVar(root)
departement_var.set(departements[0])
departement_optionmenu = tk.OptionMenu(add_frame, departement_var, *departements)
departement_optionmenu.grid(row=2, column=1, padx=5, pady=5, sticky="w")
date_debut_entry = tk.Entry(add_frame)
date_debut_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
date_fin_entry = tk.Entry(add_frame)
date_fin_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
poste_entry = tk.Entry(add_frame)
poste_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

# Bouton pour ajouter un employé
ajouter_button = tk.Button(add_frame, text="Ajouter employé", command=ajouter_employe)
ajouter_button.grid(row=6, columnspan=2, pady=10)

# Frame pour la liste des employés
list_frame = tk.LabelFrame(main_frame, text="Liste des employés", padx=10, pady=10)
list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

# Liste des employés
employes_listbox = tk.Listbox(list_frame)
employes_listbox.pack(fill=tk.BOTH, expand=True)

# Bouton pour supprimer un employé
delete_button = tk.Button(main_frame, text="Supprimer employé", command=supprimer_employe)
delete_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

start_button = tk.Button(root, text="Démarrer la reconnaissance faciale", command=demarrer_reconnaissance_faciale)
start_button.pack(pady=20)
arriver_button = tk.Button(root, text="Pointer arrivé", command= pointer_arriver)
arriver_button.pack(padx=10)

# Ajouter le bouton "pointer départ" dans le sous-cadre, à côté de "arriver"
depart_button = tk.Button(root, text="Pointer départ", command=pointer_depart)
depart_button.pack(padx=10)
main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure((0, 1), weight=1)

afficher_employes_listbox()


root.mainloop()

conn.close()
