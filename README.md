# ENG 2025 – Automne 2025

## Configuration

Procédure pour configurer ce projet sur un poste de travail virtuel ou personnel. Sauf indication contraire, cette configuration est à faire **une seule fois**.

---

### Machine virtuelle (VDI)

1. Connectez-vous à une machine virtuelle EPFL via une machine de la salle d’exercice, ou à distance via **VMware Horizon Client** (instructions sur [https://vdi.epfl.ch](https://vdi.epfl.ch)).

2. Depuis la machine virtuelle :
   - Ouvrez l’application **Terminal** (via le lanceur en bas à gauche).
   - Tapez exactement cette commande (attention aux espaces) :

```bash
curl 'https://raw.githubusercontent.com/eng209/eng209_2025/refs/heads/main/setup.sh' | bash -s
```

3. Patientez pendant l’installation automatique (cela peut prendre du temps). Une fois l’installation terminée (et sans erreur), **fermez le terminal** puis lancez **Visual Studio Code** (via le même lanceur).

4. Dans VS Code, faites **File → Open Folder**, puis naviguez vers le dossier `workspace`, qui ressemble à ceci :  
   `/Desktop/myfiles/eng209_xxxx/`  
   **Important :** ouvrez bien **le dossier eng209_xxxx**, pas `myfiles` directement.

5. Chaque semaine, récupérez les séries et corrigés depuis **Moodle** et glissez-les dans votre dossier `workspace`.

> 💡 Cette procédure est à faire uniquement **la première fois**. Les fois suivantes, ouvrez simplement VS Code et rechargez le workspace si besoin.

---

### Environnement personnel

Si vous préférez travailler **localement** sur votre propre machine, c’est possible.  
Cette configuration **n’est pas officiellement supportée**, mais nous pouvons vous aider dans la mesure du possible.

**Note importante** : l’examen de mi-semestre aura lieu **sur les machines virtuelles** de l’EPFL, donc nous vous conseillons de vous y habituer.

---

#### macOS (testé sur Sequoia 15.6) et Linux

1. Assurez-vous que **Python 3.12** est installé sur votre machine. Si ce n’est pas le cas, suivez la documentation :
   - [Python pour macOS](https://docs.python.org/3.12/using/mac.html)
   - Utilisez `pkg`, `homebrew`, etc. Assurez-vous que c’est bien **la version 3.12**.

2. Installez **Visual Studio Code** ([instructions ici](https://code.visualstudio.com/docs/setup/mac)).

3. Ouvrez un terminal, puis tapez **ces commandes une par une** :

```bash
mkdir -p ~/myfiles
curl 'https://raw.githubusercontent.com/eng209/eng209_2025/refs/heads/main/setup.sh' | bash -s -- ~/myfiles
cd ~/myfiles/eng209_*
code .
```


> ⚠️  Attention au dossier choisi : Certains dossiers comme ~/Desktop posent problème sur macOS à cause d’attributs de sécurité Apple.

Pour vérifier, vous pouvez faire :
```
xattr -l NomDeDossier
```
Si la commande retourne des attributs comme _com.apple.macl_ ou _com.apple.quarantine_, il est déconseillé d'utiliser ce dossier. Préférez ~/myfiles ou ~/Projects.

---

#### Windows

> ⚠️  Nos outils ne sont pas testés officiellement sur Windows. Procédez à vos risques et périls.


1. Installez:
   - Python 3.12 : https://docs.python.org/3.12/using/windows.html
   - VS Code : https://code.visualstudio.com/docs/setup/windows

2. Téléchargez le script Python :
    setup.py

3. Créez un dossier pour le projet, par exemple :

```bash
C:\Users\YourName\Cours
```

3. Ouvrez un terminal et exécutez :

```powershell
python -m setup --base "C:\Users\YourName\Cours"
```

Remplacez python par le chemin vers Python 3.12 si nécessaire.

