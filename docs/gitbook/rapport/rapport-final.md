---
description: Rapport final de la SAE.
icon: copy
---

# Rapport final

## Technologies

### Langage de programmation

Cette SAE utilise **Python 3.13** pour le langage de programmation.\
La raison d'utiliser la dernière version de Python a plusieurs avantages :&#x20;

* Rester à jour avec les dernières versions de Python, et donc d'obtenir les derniers patchs de sécurité, si nécessaire
* Pouvoir utiliser les dernières fonctionnalités de Python utilisé dans ce projet (Par exemple, [PEP 696](https://peps.python.org/pep-0696/), [queue.Queue.shutdown()](https://docs.python.org/release/3.13.0/library/queue.html#queue.Queue.shutdown), etc.).

### Dépendances utilisées

* `PyQt6`
  * Cette librairie permet de créer l'interface utilisateur [du client](../execution/lancement-du-client.md). Elle a été retenue, car elle a déjà été abordée lors de la `R3.09`. Il n'était donc pas intéressant d'apprendre une nouvelle API/librairie pour l'interface.
* `Sphinx`
  * Cette librairie permet la création d'une documentation utilisateur/développeur. Dans ce projet, elle permet la documentation du serveur uniquement, et des composants communs, disponible à [ce lien](https://r309.readthedocs.io/en/latest/). Cette documentation est accompagnée du thème [furo](https://github.com/pradyunsg/furo) pour l'esthétique.\
    La documentation est hébergée par [ReadTheDocs](https://readsthedocs.com/).

#### Outils de développement

Ces outils sont seulement utilisés lors du développement de l'application, pour améliorer la qualité du code :&#x20;

* `black` : Permet de formater le code pour le rendre plus lisible.
* `isort` : Permet de formater les imports Python, pour les rendre plus lisibles.
* `ruff` : Outil de [linting](https://en.wikipedia.org/wiki/Lint_\(software\)). Utilisé pour vérifier et réparer rapidement la qualité globale (Non esthétique) du code.
* `PDM` : Outil de management du projet. Permet d'ajouter les dépendances, de gérer plus facilement le projet, de le [construire](https://packaging.python.org/en/latest/tutorials/packaging-projects/) plus facilement qu'avec `pip`, etc.

***

### Technologies utilisées

Pour la communication entre le serveur et le client :&#x20;

* [`socket`](https://docs.python.org/3/library/socket.html)
  * Technologie imposée. Permet la communication des données du serveur au client, et inversement.\
    Cette librairie est très bas niveau, et il a été très compliqué de la maitriser et de la comprendre, majoritairement dû à son utilisation des [threads](https://docs.python.org/3/library/threading.html), bloquant l'utilisation de variables partagées globalement.
* [`threading`](https://docs.python.org/3/library/threading.html) / [`multithreading`](https://docs.python.org/3/library/multithreading.html)&#x20;
  * Permet de lancer du code en parallèle du code principal, dans un fil de contrôle différent. Cela pose des contraintes qui nécessite de comprendre plus en détail le langage de programmation et son fonctionnement, ce qui n'a jamais été expliqué.\
    La librairie `multithreading` est utilisé pour lancer les programmes envoyés par l'utilisateur. Elle partage le même intérêt que `threading`, dans un contexte entièrement différent.
* &#x20;[`tempfile`](https://docs.python.org/3/library/tempfile.html)&#x20;
  * Librairie utilisée pour créer des fichiers temporaire, pour lancer les scripts de l'utilisateur.
* &#x20;[`ipaddress`](https://docs.python.org/3/library/ipaddress.html)&#x20;
  * Librairie utilisée pour la vérification des adresses IP que l'utilisateur entre. Très complète, elle supporte l'IPv4 et l'IPv6.

***

## Structure du code

### Client

```coq
│  views/             <- Ce dossier contient les interfaces utilisateurs, qui seront affichés dans la fenêtre principale.
│  ├─ windows/        <- Ce dossier contient les interfaces, affichés dans des fenêtres qui s'ouvrent en dehors de la fenêtre principale.
│  │  ├─ logs.py
│  │  ├─ stopwatch.py
│  │ 
│  ├─ enter_chat.py
│  ├─ connection.py
│  ├─ upload.py
│
├─ __main__.py        <- Contient le code principal du client. Tout se trouve dedans, c'est le point d'entrée.
├─ socket_client.py   <- Contient le client socket utilisé uniquement par le client.
```

Le fait d'avoir les interfaces d'utilisateur dans un sous-dossier `views` permet de drastiquement faciliter l'identification et la modification des "widgets" `PyQt6`.

### Commun

Le dossier du code commun rassemble deux fichiers :&#x20;

* `events.py` : Les "signaux" propagés dans le code. Vous pouvez lire plus d'information par rapport aux "signaux" (Aussi connus comment "écouteurs"/"observateurs") sur ce lien : [https://refactoring.guru/fr/design-patterns/observer](https://refactoring.guru/fr/design-patterns/observer)
* `messages.py` : Ce module définit les messages qui seront partagés entre le serveur et le client. Cela permet de créer un protocole de communication entre les deux.

### Serveur

Le serveur rassemble deux fichiers :&#x20;

* `__main__.py` : Le point d'entrée du serveur. Ce fichier va préparer le lancement et va effectuer l'exécution du serveur. Ce module va principalement traiter les messages reçus.
* `executor.py` : Ce module gère l'exécution des scripts reçus de l'utilisateur. Chaque langage de programmation supporté à sa propre classe "exécuteur" de défini. Chaque exécuteur peut lire et exécuter le code du client de manière différemment. (Python peut simplement lancer le fichier, mais C++ doit d'abord le compiler avec la commande `gcc`)

## Difficultés rencontrées

Les difficultés rencontrées dans ce projet sont les suivants :&#x20;

* Manque crucial de temps
  * Ce projet a pris **énormément** de temps en plus que donné à l'IUT.
* Manque de connaissance sur les sockets
  * L'utilisation d'une librairie aussi basse a été très compliquée. De plus, cela nous force à réinventer la roue, là où nous aurions pu utiliser la librairie [RPC](https://docs.python.org/3/library/xmlrpc.client.html), plus haut niveau, et qui aurait été tout aussi adapté à ce projet.

