---
description: Introduction à la SAE3.02
icon: circle-info
---

# Introduction - SAE3.02

## SAE3.02 - Architecture Multi-Serveurs pour Compilation et Exécution de Programmes

Cette documentation a été réalisé pour la SAE3.02, dans le but de réaliser une application communicante, entre un client et un serveur.

Le but étant de permettre au client d'envoyer un fichier de code (En Python, Java, etc.), et de laisser le serveur exécuter ce code. Après son exécution, le client reçoit les logs générés.

***

Cette SAE a été particulièrement complexe et a pris beaucoup, beaucoup, **beaucoup** de temps. Beaucoup plus que ce qui a été proposé en cours. Potentiellement le triple du temps donné.

La nécessité d'utiliser la librairie `socket` a rendu la tâche beaucoup plus ardue et complexe assez inutilement, dans un contexte ou d'autres protocoles de communication, plus mature, aurait pu être utilisés (Comme [HTTP](https://docs.python.org/3.13/library/http.server.html#module-http.server)/2 ou [RPC](https://docs.python.org/3/library/xmlrpc.html)).

En contrepartie, cela a permis de mieux comprendre les problématiques bas niveau du réseau et des télécommunications.

***

Pour utiliser l'application, commencer par lire la page d'installation :&#x20;

{% content-ref url="installation.md" %}
[installation.md](installation.md)
{% endcontent-ref %}



{% hint style="warning" %}
Le dépôt ne sera ouvert qu'à partir de 1er janvier, jusqu'à réception de la note de la SAE.
{% endhint %}

