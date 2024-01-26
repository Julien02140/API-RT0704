from flask import Flask, jsonify, request,g
import json
import hashlib
import os
#installer request pour la method post

app = Flask(__name__)

videotheque = []
films = []
films_populaires= []
genres = []
utilisateurs = []

def lire_fichier_json(nom_fichier):
    chemin_fichier = os.path.join(os.path.dirname(__file__), '..', 'data', nom_fichier)

    with open(chemin_fichier, 'r+') as fichier:
        contenu_json = json.load(fichier)

    return contenu_json

def modifier_fichier_json(dico,nom_fichier):
    chemin_fichier = os.path.join(os.path.dirname(__file__), '..', 'data', nom_fichier)

    with open(chemin_fichier, 'r+') as fichier:
        fichier.seek(0)
        json.dump(dico, fichier, indent=2)
        fichier.truncate()
    return

videotheque = lire_fichier_json('videotheque.json')
films = lire_fichier_json('films.json')
films_populaires = lire_fichier_json('films_populaires.json')
genres = lire_fichier_json('genres.json')
utilisateurs = lire_fichier_json('utilisateur.json')


def creer_videotheque(user_id):
    nouv_video = {

        "id_utilisateur": user_id,
        "liste_films": []
    }
    
    videotheque.append(nouv_video)

    modifier_fichier_json(videotheque,"videotheque.json")
    

@app.route('/recherche/<string:chaine>')
def recherche(chaine):
    return chaine

def chercher_videotheque(user_id):
    for video in videotheque:
        id_video = video.get("id_utilisateur")   
        print("id video :",id_video) 
        if id_video == user_id:
            print("videotheque trouve",video)
            return video
    return "erreur, ne trouve pas la videotheque du user"  

@app.route('/ma_videotheque/<int:id>') #id de l'utilisateur
def ma_videotheque(id):
    print("dans la fonction videotheque ")
    for video in videotheque:
        id_video = video.get("id_utilisateur")
        print("id video :",id_video)
        if id_video == id:
            liste_films = video.get("liste_films")
            print(liste_films)
            return jsonify({"liste_films": liste_films})
    return "pas trouve id utilisateur"
    
#cette route vérifie si le user est dans la base de donnée
@app.route('/verif_user', methods=['POST'])
def verif_user():
    donnee = request.form
    print(donnee)
    #récuper les infos de la requête POST
    pseudo_user = donnee.get("username")
    password_user = donnee.get("password")
    #On vérifie si le user est bien dans le json
    for utilisateur in utilisateurs:
        print(utilisateur.get("pseudo"))
        print(utilisateur.get("mot_de_passe"))
        password_chiffrer = hashlib.sha256(password_user.encode('utf-8')).hexdigest()
        print("mot de passe : ",password_chiffrer)
        if utilisateur.get("pseudo") == pseudo_user and password_chiffrer == utilisateur.get("mot_de_passe"):
            id = utilisateur.get("id")
            return jsonify({"message": "Connexion OK","id": id})
    #si on arrive la, alors aucun utilisateur ne correspond
    return jsonify({"message": "NON"})

@app.route('/register_user',methods=['POST'])
def register_user():
    dernier_user = utilisateurs[-1]
    next_id = dernier_user["id"] + 1
    donnee  = request.form
    password = donnee.get("password")
    password_chiffrer = hashlib.sha256(password.encode('utf-8')).hexdigest()
    new_user = {
        "id": next_id,
        "nom" : donnee.get("lastname"),
        "prenom": donnee.get("firstname"),
        "pseudo": donnee.get("pseudo"),
        "age": donnee.get("age"),
        "mot_de_passe": password_chiffrer,
        "email": donnee.get("email")
    }
    utilisateurs.append(new_user) #ajoute au dico user le nouvel user

    modifier_fichier_json(utilisateurs,"utilisateur.json")

    creer_videotheque(next_id)
    
    return jsonify({"message":"Utilisateur ajouté"})

@app.route('/films_populaires')
def get_films_populaires():
    return jsonify(films_populaires)

@app.route('/trouver_film/<int:film_id>')
def trouver_film(film_id): #prends l'id du film en paramètre, retrouve le film dans films_populaires.json
    # Affiche tous les IDs dans la liste de films
    print("voici l'id du film",film_id)
    for film in films:
        if film['id'] == film_id:
            print(film["title"])
            return jsonify(film)
    for film in films_populaires:
        if film['id'] == film_id:
            print(film["title"])
            return jsonify(film)
        
    print("film pas trouve")
    return "erreur film non trouve"

@app.route('/ajout_film/<int:user_id>/<int:film_id>')
def ajout_film(user_id,film_id):
    print("AJOUT D UN FILM")
    film = trouver_film(film_id)
    video = chercher_videotheque(user_id)
    for film in video.get("liste_films"):
        if film == film_id:
            print("film deja dans la videothequ")
            return jsonify({"message" : "Deja dans la videotheque"})
    print("AJOUT DU FILM ID", film_id)
    print(video)
    nouv_video = video.get("liste_films")
    nouv_video.append(film_id)
    print("nouv_video ajouter")
    modifier_fichier_json(videotheque,"videotheque.json")    
    return jsonify({"message": "film ajouté"})
    
@app.route('/supprimer_film/<int:user_id>/<int:film_id>')
def supprimer_film(user_id,film_id):
    print("SUPPRIMER FILM DANS LA VIDEOTHEQUE, ID FILM :", film_id)
    film = trouver_film(film_id)
    for user in videotheque:
        if user["id_utilisateur"] == user_id:
            if film_id in user["liste_films"]:
                user["liste_films"].remove(film_id)
                print("film supprimé")
                modifier_fichier_json(videotheque,"videotheque.json")
                return jsonify({"message" : "film supprimé"})  
            else:
                #normalement impossible de tomber dans cette condition
                print("l'id n'a pas été trouvé")
                return jsonify({"message": "pas trouvé"})
            
@app.route('/recherche_film/<string:mot>')
def recherche_film(mot):
    liste_films = []
    for film in films:
        if film["title"].lower().startswith(mot.lower()):
            liste_films.append(film)
    print("liste des films trouvés api :",liste_films)
    return jsonify({"liste_films" : liste_films})

@app.route('/recherche_genre/<int:id>')
def recherche_genre(id):
    liste_films = []
    for film in films:
        liste_id = film["genre_ids"]
        for film_id in liste_id:
            if film_id == id:
                liste_films.append(film)
    return jsonify({"message" : liste_films})
        

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=int("5000"),debug=True)
    print("api start")

