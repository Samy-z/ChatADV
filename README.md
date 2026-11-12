# ChatADV

Assistant léger pour le travail de bureau, conçu pour tourner sur un
processeur seul (aucune carte graphique requise) : traduire des messages,
rédiger des e-mails récurrents (relances de paiement, réponses aux demandes
de remise, livraisons incomplètes), et retrouver une commande dans un
fichier de suivi. Le modèle embarqué est choisi en comparant plusieurs
modèles open-weight sur ces tâches précises.

**Tout reste sur l'ordinateur.** Aucun service externe, aucun compte, aucune
télémétrie. Le modèle de langue tourne en local via Ollama, en mode
processeur (pas besoin de carte graphique). La recherche de commandes lit le
fichier directement, sans IA : un chiffre sorti d'un tableau n'a pas à
passer par un modèle.

## Lancer

1. Installer [Ollama](https://ollama.com) puis, une fois :
   `ollama pull phi4-mini` (licence MIT; modèle désigné par la campagne de
   comparaison, voir État).
2. `python app.py`
3. Ouvrir http://localhost:8742

Réglages par variables d'environnement : `ASSISTANTE_MODELE` (nom du modèle),
`ASSISTANTE_COMMANDES` (chemin du fichier de commandes, CSV pour l'instant,
Excel .xlsx à venir), `ASSISTANTE_OLLAMA` (adresse du serveur local).

## État

Squelette fonctionnel (2026-11-04) : trois onglets opérationnels contre un
Ollama local, données d'exemple synthétiques incluses.

Modèle définitif choisi (2026-11-12) : **phi4-mini**, désigné par la
campagne de comparaison a-prime (`docs/compare/campaign-assistante.md` du
dépôt a-prime). Le détecteur a certifié les 18 entrées sur 40 où les deux
finalistes divergent, puis un jugement humain à l'aveugle a tranché
(8 contre 6, les traductions 3 contre 1). L'application sert le régime
exact qui a été mesuré : température 0.2, budget de 400 jetons,
processeur seul.

À venir : lecture .xlsx native, remplissage de contrats, règles maison
dans la consigne de rédaction, et un lanceur sans terminal.
