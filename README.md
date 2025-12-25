# 🔬 Projet P2 : Benchmark FPs pour Couplage Si₃N₄

**Objectif :** Identifier les protéines fluorescentes optimales pour coupler efficacement dans un waveguide Si₃N₄ dans le contexte du PNPH.

---

## 📋 Contexte

Pour le projet PNPH (Photonic-Neural Hybrid Platform), tu dois choisir quelle protéine fluorescente utiliser pour convertir l'activité neuronale en signal optique. Mais toutes les FPs ne sont pas égales face à un waveguide Si₃N₄ !

```
Neurone → FP → Photons → Waveguide Si₃N₄ → Détecteur
                  ↑
          Quel spectre est optimal ?
```

**Ce projet répond à :** *Parmi les 685 FPs de ton dataset, lesquelles ont le meilleur couplage avec un waveguide Si₃N₄ ?*

---

## 🚀 Quick Start

### 1. Installation

```bash
# Cloner/créer le dossier
mkdir fp_sin_benchmark && cd fp_sin_benchmark

# Installer les dépendances
pip install numpy pandas matplotlib scipy
```

### 2. Lancer avec données synthétiques (test)

```bash
python 01_fp_sin_coupling_benchmark.py
```

### 3. Lancer avec TES données FPbase

```bash
# Modifier la ligne dans le script :
# fp_db = FPDatabase(data_source='chemin/vers/ton/fpbase_dataset.csv')

python 01_fp_sin_coupling_benchmark.py
```

---

## 📊 Résultats Attendus

Le script génère :

| Fichier | Description |
|---------|-------------|
| `waveguide_transmission.png` | Spectre de transmission Si₃N₄ |
| `coupling_distribution.png` | Distribution des scores par catégorie |
| `top_candidates.png` | Visualisation des meilleures FPs |
| `rapport_P2_benchmark.md` | Rapport complet en Markdown |
| `fp_coupling_results.csv` | Données complètes exportées |

---

## 🧮 Méthodologie

### Score de couplage

```
Score = ∫ Emission(λ) × Transmission(λ) dλ / ∫ Emission(λ) dλ
```

- **Emission(λ)** : Spectre d'émission de la FP (modèle gaussien)
- **Transmission(λ)** : Transmission du waveguide Si₃N₄ (données littérature)

### Score composite

```
Composite = Score_couplage × QY × log10(Brightness) / 3
```

Intègre le rendement quantique et la brillance pour un ranking plus réaliste.

### Modèle Si₃N₄

- Indice de réfraction : Formule de Sellmeier (Luke et al. 2015)
- Pertes de propagation : Interpolation sur données publiées (Blumenthal 2018)
- Plage : 400-800 nm (visible)

---

## 📁 Structure du projet

```
fp_sin_benchmark/
├── 01_fp_sin_coupling_benchmark.py   # Script principal
├── 02_connect_fpbase.py              # Connexion à tes données
├── README.md                         # Ce fichier
├── results/                          # Résultats générés
│   ├── waveguide_transmission.png
│   ├── coupling_distribution.png
│   ├── top_candidates.png
│   ├── rapport_P2_benchmark.md
│   └── fp_coupling_results.csv
└── data/                             # Tes données FPbase
    └── fpbase_dataset.csv            # À ajouter !
```

---

## 🔗 Connexion à tes données Master

Tu as déjà 685 FPs avec structures AlphaFold2. Pour les utiliser :

### Format CSV attendu

```csv
id,name,ex_peak_nm,em_peak_nm,ex_fwhm_nm,em_fwhm_nm,quantum_yield,brightness,category
FP_0001,EGFP,488,507,30,35,0.60,33600,Green
FP_0002,mCherry,587,610,40,45,0.22,15900,Red
...
```

### Colonnes requises

| Colonne | Description | Obligatoire |
|---------|-------------|-------------|
| `id` | Identifiant unique | ✅ |
| `name` | Nom de la FP | ✅ |
| `em_peak_nm` | λ émission (nm) | ✅ |
| `ex_peak_nm` | λ excitation (nm) | ⚪ |
| `quantum_yield` | Rendement quantique (0-1) | ⚪ |
| `brightness` | Brillance (ε × QY) | ⚪ |
| `em_fwhm_nm` | Largeur à mi-hauteur émission | ⚪ |

---

## 📈 Interprétation des résultats

### Score de couplage

| Score | Interprétation |
|-------|----------------|
| > 0.95 | Excellent - Pertes < 5% |
| 0.90 - 0.95 | Bon - Pertes 5-10% |
| 0.80 - 0.90 | Acceptable - Pertes 10-20% |
| < 0.80 | Mauvais - Éviter |

### Zone spectrale optimale

```
400 nm        500 nm        600 nm        700 nm        800 nm
   |-------------|-------------|-------------|-------------|
   UV    Bleu     Vert    Jaune   Orange   Rouge    Far-Red
   ↓              ↓              ↓                  ↓
Pertes élevées   OK      ★ OPTIMAL ★           Très bon
(~5%)          (~3%)      (~2%)               (~1%)
```

**Recommandation :** FPs émettant entre **550-650 nm** (jaune-orange-rouge)

---

## 🎯 Prochaines étapes

1. **Connecter tes vraies données** (1h)
   - Exporter ton dataset FPbase en CSV
   - Lancer le benchmark

2. **Ajouter indicateurs dynamiques** (P1 - 1-2 semaines)
   - Intégrer τ_on, τ_off pour GCaMPs
   - Créer score dynamique

3. **Modéliser grating coupler** (P7 - 4-6 semaines)
   - Efficacité de couplage en fonction de l'angle
   - Optimiser le design

---

## 📚 Références

1. **Blumenthal et al. (2018)** - "Silicon Nitride in Silicon Photonics" - Proc. IEEE
2. **Luke et al. (2015)** - "Broadband mid-infrared frequency comb generation in a Si3N4 microresonator" - Opt. Lett.
3. **Lambert (2019)** - "FPbase: a community-editable fluorescent protein database" - Nat. Methods

---

## 📝 Citation

Si tu utilises ce travail dans ta thèse :

```bibtex
@misc{panda2025fpsin,
  author = {Panda, M.},
  title = {Benchmark of Fluorescent Proteins for Si3N4 Waveguide Coupling},
  year = {2025},
  note = {PNPH Project - Pre-doctoral work}
}
```

---

*Projet P2 - PNPH Pipeline*  
*M. Panda - Décembre 2025*
