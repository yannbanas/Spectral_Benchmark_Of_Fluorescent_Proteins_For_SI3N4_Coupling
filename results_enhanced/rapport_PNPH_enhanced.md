# 📊 Rapport PNPH Amélioré : FPs + Indicateurs GECI/GEVI

**Date :** 2025-12-25 11:53
**Projet :** PNPH (Photonic-Neural Hybrid Platform)
**Auteur :** M. Panda

---

## 1. Résumé Exécutif

Ce benchmark évalue **517 protéines fluorescentes** et 
**17 indicateurs optogénétiques** pour leur compatibilité 
avec une interface neuro-photonique Si₃N₄.

### Score PNPH

Le score PNPH composite intègre :
- **Couplage spectral** (20%) : Transmission dans waveguide Si₃N₄
- **Brightness** (20%) : QY × log(brightness)
- **Cinétique** (25%) : Rapidité de réponse (critique pour spikes)
- **Photostabilité** (15%) : Durée de vie en imagerie
- **Sensibilité** (20%) : ΔF/F

---

## 2. Résultats FPs Classiques

### Top 5 FPs pour PNPH

| Rang | Nom | λ_em (nm) | QY | Score PNPH |
|------|-----|-----------|-----|------------|
| 1 | GFPxm18 | 502 | 0.96 | 0.657 |
| 2 | GFPxm16 | 504 | 0.74 | 0.631 |
| 3 | AausFP1 | 510 | 0.97 | 0.628 |
| 4 | GFPxm19 | 502 | 0.70 | 0.626 |
| 5 | bfloGFPa1 | 512 | 1.00 | 0.626 |


### Distribution par catégorie

Les FPs **vertes** dominent en nombre, mais les FPs **orange-rouge** 
ont un meilleur couplage Si₃N₄.

---

## 3. Indicateurs Calciques (GECI)

### Top 3 GECI pour PNPH

| Rang | Nom | τ_rise (ms) | ΔF/F (%) | Score PNPH |
|------|-----|-------------|----------|------------|
| 1 | jGCaMP8f | 2.0 | 15.0 | 0.720 |
| 2 | jGCaMP8m | 5.0 | 20.0 | 0.657 |
| 3 | jGCaMP8s | 8.0 | 25.0 | 0.623 |


### Recommandation GECI

**Pour spike detection rapide :** jGCaMP8f (τ_rise = 2 ms)
**Pour sensibilité maximale :** jGCaMP8s (ΔF/F = 25%)
**Pour compromis :** jGCaMP8m

---

## 4. Indicateurs Voltage (GEVI)

### Top 3 GEVI pour PNPH

| Rang | Nom | τ_rise (ms) | ΔF/F (%) | Score PNPH |
|------|-----|-------------|----------|------------|
| 1 | jASAP | 0.85 | -55.0 | 0.747 |
| 2 | ASAP4e | 1.20 | +41.0 | 0.730 |
| 3 | Voltron2 | 0.40 | -30.0 | 0.727 |


### Recommandation GEVI

**Pour résolution temporelle :** ASAP5 (τ_rise = 0.78 ms)
**Pour photostabilité :** ASAP4e (positif, photostable)
**Pour SNR maximal :** jASAP (amélioration Janelia)

---

## 5. Comparaison GECI vs GEVI

| Critère | GECI (jGCaMP8f) | GEVI (ASAP5) |
|---------|-----------------|--------------|
| τ_rise | 2 ms | 0.78 ms |
| |ΔF/F| | 15% | 35% |
| Photostabilité | ★★★★☆ | ★★★☆☆ |
| SNR | ★★★★★ | ★★★★☆ |
| Résolution spikes | ~50 Hz | ~100 Hz |
| Complexité | Simple | Plus complexe |

**Verdict :** 
- GECI pour applications standard (imagerie calcique populaire)
- GEVI pour résolution temporelle critique (subthreshold, timing précis)

---

## 6. Recommandations pour PNPH

### Configuration optimale

```
Couche biologique :
├── Indicateur principal : jGCaMP8f (calcium, rapide)
├── OU : ASAP4e (voltage, photostable)
└── Reporter structurel : StayGold (ultra-stable)

Couche photonique :
├── Waveguide : Si₃N₄ (300×800 nm)
├── λ optimal : 510-520 nm (vert)
└── Longueur : 1-2 cm (pertes < 5%)
```

### Prochaines étapes

1. [ ] Tester jGCaMP8f sur MEA Axion
2. [ ] Comparer ASAP4e vs ASAP5 en culture
3. [ ] Mesurer couplage réel waveguide
4. [ ] Optimiser grating coupler pour λ=515 nm

---

## 7. Références

1. Zhang et al. (2023) Nature - jGCaMP8
2. Evans et al. (2023) Nat Methods - ASAP4
3. Tiwari et al. (2024) Neuron - ASAP5
4. Bhairavabhottla et al. (2022) - StayGold

---

*Rapport généré par le benchmark PNPH amélioré v2*
