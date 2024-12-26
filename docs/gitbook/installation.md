---
description: Guide d'installation pour le programme client/serveur
icon: wrench
---

# Installation

L'installation du client et du serveur se font ensemble. Il n'y a pas besoin d'instructions différenciées.

## Installation de Python

{% hint style="info" %}
Ce projet requiert la **dernière** version de Python, soit `Python 3.13`. Faites bien attention à la version utilisé.

Vous pouvez vérifier votre version de Python avec la commande : `python -V`
{% endhint %}

Pour installer Python sur votre machine, vous pouvez vous rendre sur le site de [Python](https://python.org/) afin d'installer la version de Python.

Version 3.13.1 : [https://www.python.org/downloads/release/python-3131/](https://www.python.org/downloads/release/python-3131/)

Prenez l'installateur correspondant à votre machine, exécutez la pour installer sur votre machine.\
Un redémarrage peut être nécessaire.

***

{% hint style="warning" %}
En fonction de votre plateforme et de la manière vous avez installer Python, vous devez utiliser soit la commande `py`, `python`, ou encore `python3`.\
Pour simplifier ce guide, la commande `python` sera utilisé tout du long. Adaptez la commande selon votre besoin.\
Vous pouvez vérifier quel commande est à votre disposition grâce à votre terminal.
{% endhint %}

## Clonage du repository

Vous devez disposer de l'outil [Git](https://git-scm.com/) pour cette étape.

Afin de copier le code nécessaire à l'installation, vous devez copier le dépôt du code.\
Pour ce faire, dans votre terminal, exécutez la commande suivante :&#x20;

```
git clone https://github.com/UHA-2301242/R3.09.git
```

Cela aura pour effet de télécharger le dépôt dans le répertoire auquel vous êtes situé.\
Vous obtiendrez automatiquement la dernière mise à jour du dépôt.

## Installation des dépendances

Ce projet utilise PyQt6, qui est une dépendance obligatoire.

Afin d'installer ces dépendances, utilisez la commande ci-dessous **dans le répertoire du dépôt** :&#x20;

```
python -m pip install .
```

{% hint style="info" %}
Si vous obtenez l'erreur

{% code overflow="wrap" %}
```python
ERROR: Directory '.' is not installable. Neither 'setup.py' nor 'pyproject.toml' found.
```
{% endcode %}

...vérifiez que vous êtes dans le bon répertoire.
{% endhint %}

Nous vous conseillons d'utiliser un [environnement virtuel](https://docs.python.org/fr/3.13/library/venv.html) si vous savez le faire.

## Lancement du projet

Pour lancer le projet, référez vous aux pages dédiés :&#x20;

{% content-ref url="execution/lancement-du-serveur.md" %}
[lancement-du-serveur.md](execution/lancement-du-serveur.md)
{% endcontent-ref %}

{% content-ref url="execution/lancement-du-client.md" %}
[lancement-du-client.md](execution/lancement-du-client.md)
{% endcontent-ref %}
