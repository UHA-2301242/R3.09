---
icon: server
---

# Lancement du serveur

Après l'installation de l'application, vous devriez être en capacité de lancer le serveur à l'aide de la commande suivante :

```
sae302_server
```

Dans le cas où vous n'arrivez pas à lancer le serveur à l'aide de cette commande, vous pouvez aussi utiliser la commande suivante : (À partir du dossier racine du projet)

```
python ./src/sae302/server
```

Vous devriez obtenir la sortie suivante :

<figure><img src="../.gitbook/assets/image (6).png" alt=""><figcaption><p>Lancement du serveur à partir de l'alias de script</p></figcaption></figure>

Vous pouvez spécifier un nombre avec ce script pour lancer le serveur un port différent :

<figure><img src="../.gitbook/assets/image (7).png" alt=""><figcaption></figcaption></figure>

{% hint style="danger" %}
Vous ne pouvez pas faire Ctrl+C sur Windows lors de l'utilisation du serveur.

Cela est dû à une limitation de Python : [https://github.com/python/cpython/issues/80116](https://github.com/python/cpython/issues/80116)

Pour éteindre le serveur, vous devez fermer votre terminal.
{% endhint %}

## Capacités

Le serveur va automatiquement découvrir quel fichiers il peut exécuter en fonction des programmes disponible sur le système.

À ce jour, le serveur peut exécuter des fichiers de type :

* Python (Requiert la commande `python`)
* Java (Requiert la commande `java`)
* C (Requiert la commande `gcc`)
* C++ (Requiert la commande `g++`)

Si un client envoie un fichier, mais que le serveur ne peut pas exécuter ce fichier, il enverra une erreur au client.
