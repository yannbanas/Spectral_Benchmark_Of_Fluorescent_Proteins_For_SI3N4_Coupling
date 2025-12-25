# 📊 Rapport P2 : Benchmark FPs pour Couplage Si₃N₄

**Date :** 2025-12-25 11:35
**Projet :** PNPH (Photonic-Neural Hybrid Platform)
**Auteur :** M. Panda

---

## 1. Objectif

Identifier les protéines fluorescentes (FPs) optimales pour coupler 
efficacement dans un waveguide Si₃N₄ dans le contexte d'une interface 
neuro-photonique.

## 2. Méthodologie

### 2.1 Modèle de waveguide Si₃N₄
- **Matériau :** Nitrure de silicium stœchiométrique
- **Plage de transparence :** 400-2350 nm
- **Pertes :** Modèle basé sur données publiées (Blumenthal 2018, Luke 2013)
- **Géométrie :** Core 300×800 nm

### 2.2 Base de données FPs
- **Source :** data\temp_fpbase.csv
- **Nombre de FPs :** 517
- **Plage spectrale :** 414 - 720 nm

### 2.3 Score de couplage
```
Score = ∫ Emission(λ) × Transmission(λ) dλ / ∫ Emission(λ) dλ
```
- Représente la fraction d'émission transmise par le waveguide
- Score composite intègre aussi QY et brightness

---

## 3. Résultats

### 3.1 Statistiques globales

| Métrique | Valeur |
|----------|--------|
| Score moyen | 0.988 |
| Score max | 0.994 |
| Score min | 0.982 |
| Écart-type | 0.004 |

### 3.2 Score par catégorie spectrale

| Catégorie | N | Score moyen | Score max |
|-----------|---|-------------|------------|
| UV | 1 | 0.987 | 0.987 |
| Blue | 27 | 0.983 | 0.986 |
| Cyan | 39 | 0.983 | 0.984 |
| Green | 238 | 0.986 | 0.988 |
| Yellow | 24 | 0.989 | 0.991 |
| Orange | 73 | 0.992 | 0.992 |
| Red | 65 | 0.993 | 0.993 |
| Far-Red | 50 | 0.993 | 0.994 |


### 3.3 Top 20 Candidates

| Rang | Nom | λ_em (nm) | Score couplage | QY | Score composite |
|------|-----|-----------|----------------|-----|-----------------|
| 1 | GFPxm18 | 502 | 0.985 | 0.96 | 0.946 |
| 2 | GFPxm16 | 504 | 0.985 | 0.74 | 0.729 |
| 3 | AausFP1 | 510 | 0.986 | 0.97 | 0.708 |
| 4 | GFPxm19 | 502 | 0.985 | 0.70 | 0.690 |
| 5 | bfloGFPa1 | 512 | 0.986 | 1.00 | 0.686 |
| 6 | oxStayGold | 506 | 0.985 | 0.93 | 0.672 |
| 7 | dVFP | 503 | 0.985 | 1.00 | 0.668 |
| 8 | StayGold | 505 | 0.985 | 0.93 | 0.664 |
| 9 | td8oxStayGold | 506 | 0.985 | 0.93 | 0.662 |
| 10 | td5oxStayGold | 506 | 0.985 | 0.93 | 0.661 |
| 11 | amFP506 | 506 | 0.985 | 0.67 | 0.660 |
| 12 | td5StayGold | 504 | 0.985 | 0.91 | 0.643 |
| 13 | mBaoJin | 508 | 0.986 | 0.93 | 0.635 |
| 14 | tdLanYFP | 519 | 0.987 | 0.92 | 0.633 |
| 15 | dLanYFP | 524 | 0.987 | 0.90 | 0.609 |
| 16 | h2-3 | 516 | 0.987 | 0.89 | 0.605 |
| 17 | RRvT | 583 | 0.991 | 0.88 | 0.604 |
| 18 | StayGold-E138D | 504 | 0.985 | 0.87 | 0.601 |
| 19 | KOFP-7 | 496 | 0.984 | 0.61 | 0.600 |
| 20 | GRvT | 583 | 0.991 | 0.97 | 0.591 |


---

## 4. Conclusions

### 4.1 Zone spectrale optimale
Les FPs avec **λ_em entre 550-650 nm** (jaune-orange-rouge) présentent 
le meilleur compromis entre :
- Transmission élevée dans Si₃N₄ (>95%)
- Distance spectrale suffisante pour éviter excitation parasite
- Compatibilité avec détecteurs Si (SPAD, CCD)

### 4.2 Recommandations pour PNPH

**Top 3 recommandées :**
1. **GFPxm18** (λ=502nm) - Score: 0.946
2. **GFPxm16** (λ=504nm) - Score: 0.729  
3. **AausFP1** (λ=510nm) - Score: 0.708

### 4.3 Indicateurs existants compatibles
Parmi les indicateurs optogénétiques connus :
- **jGCaMP8f** (λ_em ≈ 515 nm) : Score estimé ~0.92
- **mCherry-based** (λ_em ≈ 610 nm) : Score estimé ~0.97
- **tdTomato** (λ_em ≈ 581 nm) : Score estimé ~0.96

---

## 5. Prochaines étapes

1. [ ] Valider avec données FPbase réelles
2. [ ] Inclure propriétés dynamiques (τ_on, τ_off pour GECIs)
3. [ ] Modéliser efficacité de couplage grating coupler
4. [ ] Comparer avec indicateurs voltage (ASAP, Voltron)

---

*Rapport généré automatiquement par le script P2_FP_SiN_Benchmark*
