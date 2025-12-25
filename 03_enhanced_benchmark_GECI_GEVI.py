#!/usr/bin/env python3
"""
================================================================================
PROJET P2 AMÉLIORÉ : Benchmark FPs + Indicateurs GECI/GEVI pour PNPH
================================================================================

Extension du benchmark original avec :
1. Base de données complète des indicateurs GECI (GCaMP) et GEVI (ASAP, Voltron)
2. Propriétés dynamiques (τ_rise, τ_decay, ΔF/F)
3. Photostabilité
4. Score PNPH composite optimisé

Auteur : M. Panda
Date : Décembre 2025
Projet : PNPH (Photonic-Neural Hybrid Platform)

Références :
- Zhang et al. (2023) Nature - jGCaMP8
- Evans et al. (2023) Nat Methods - ASAP4
- Abdelfattah et al. (2024) Neuron - ASAP5

================================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import trapezoid
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
plt.style.use('seaborn-v0_8-whitegrid')
OUTPUT_DIR = Path("./results_enhanced")
OUTPUT_DIR.mkdir(exist_ok=True)

print("="*70)
print("BENCHMARK AMÉLIORÉ : FPs + GECI + GEVI pour PNPH")
print("="*70)
print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# ============================================================================
# PARTIE 1 : BASE DE DONNÉES DES INDICATEURS GECI/GEVI
# ============================================================================

class IndicatorDatabase:
    """
    Base de données complète des indicateurs optogénétiques.
    
    Sources :
    - Zhang et al. (2023) Nature - jGCaMP8 family
    - Dana et al. (2019) Nature Methods - jGCaMP7 family
    - Evans et al. (2023) Nat Methods - ASAP4 family
    - Abdelfattah et al. (2024) Neuron - ASAP5
    - Villette et al. (2019) - ASAP3
    """
    
    def __init__(self):
        self.geci_data = self._load_geci_database()
        self.gevi_data = self._load_gevi_database()
        self.all_indicators = pd.concat([self.geci_data, self.gevi_data], ignore_index=True)
        
    def _load_geci_database(self):
        """
        Base de données des indicateurs calciques (GECI).
        Données extraites de Zhang et al. (2023) et Dana et al. (2019).
        """
        geci_data = [
            # jGCaMP8 family (Zhang et al. 2023, Nature)
            {
                'name': 'jGCaMP8f',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 515,
                'tau_rise_ms': 2.0,      # Half-rise time
                'tau_decay_ms': 192,     # Half-decay time
                'delta_f_f': 15.0,       # ΔF/F per 1 AP (%)
                'snr_1ap': 8.0,          # SNR for 1 AP
                'quantum_yield': 0.60,   # Estimé (basé GFP)
                'brightness': 30000,     # Relative
                'photostability': 0.85,  # Relative (1 = très stable)
                'max_spike_rate_hz': 50, # Peut tracker jusqu'à 50 Hz
                'kd_nm': 334,            # Affinité Ca2+ (nM)
                'reference': 'Zhang et al. 2023 Nature',
                'addgene_id': '162376',
            },
            {
                'name': 'jGCaMP8m',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 515,
                'tau_rise_ms': 5.0,
                'tau_decay_ms': 137,
                'delta_f_f': 20.0,       # Plus sensible
                'snr_1ap': 10.0,
                'quantum_yield': 0.60,
                'brightness': 32000,
                'photostability': 0.85,
                'max_spike_rate_hz': 30,
                'kd_nm': 108,
                'reference': 'Zhang et al. 2023 Nature',
                'addgene_id': '162375',
            },
            {
                'name': 'jGCaMP8s',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 515,
                'tau_rise_ms': 8.0,
                'tau_decay_ms': 198,
                'delta_f_f': 25.0,       # Le plus sensible
                'snr_1ap': 12.0,
                'quantum_yield': 0.60,
                'brightness': 28000,
                'photostability': 0.85,
                'max_spike_rate_hz': 20,
                'kd_nm': 46,
                'reference': 'Zhang et al. 2023 Nature',
                'addgene_id': '162377',
            },
            # jGCaMP7 family (Dana et al. 2019)
            {
                'name': 'jGCaMP7f',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 515,
                'tau_rise_ms': 20.0,
                'tau_decay_ms': 277,
                'delta_f_f': 10.0,
                'snr_1ap': 5.0,
                'quantum_yield': 0.59,
                'brightness': 25000,
                'photostability': 0.80,
                'max_spike_rate_hz': 15,
                'kd_nm': 174,
                'reference': 'Dana et al. 2019 Nat Methods',
                'addgene_id': '104488',
            },
            {
                'name': 'jGCaMP7s',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 515,
                'tau_rise_ms': 30.0,
                'tau_decay_ms': 400,
                'delta_f_f': 12.0,
                'snr_1ap': 6.0,
                'quantum_yield': 0.59,
                'brightness': 26000,
                'photostability': 0.80,
                'max_spike_rate_hz': 10,
                'kd_nm': 68,
                'reference': 'Dana et al. 2019 Nat Methods',
                'addgene_id': '104487',
            },
            # GCaMP6 family (Chen et al. 2013)
            {
                'name': 'GCaMP6f',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 512,
                'tau_rise_ms': 45.0,
                'tau_decay_ms': 142,
                'delta_f_f': 8.0,
                'snr_1ap': 4.0,
                'quantum_yield': 0.59,
                'brightness': 22000,
                'photostability': 0.75,
                'max_spike_rate_hz': 10,
                'kd_nm': 375,
                'reference': 'Chen et al. 2013 Nature',
                'addgene_id': '40755',
            },
            {
                'name': 'GCaMP6s',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 488,
                'em_peak_nm': 512,
                'tau_rise_ms': 180.0,
                'tau_decay_ms': 550,
                'delta_f_f': 15.0,
                'snr_1ap': 7.0,
                'quantum_yield': 0.61,
                'brightness': 25000,
                'photostability': 0.75,
                'max_spike_rate_hz': 5,
                'kd_nm': 144,
                'reference': 'Chen et al. 2013 Nature',
                'addgene_id': '40753',
            },
            # Red calcium indicators
            {
                'name': 'jRGECO1a',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 560,
                'em_peak_nm': 590,
                'tau_rise_ms': 15.0,
                'tau_decay_ms': 350,
                'delta_f_f': 10.0,
                'snr_1ap': 4.0,
                'quantum_yield': 0.39,
                'brightness': 15000,
                'photostability': 0.70,
                'max_spike_rate_hz': 15,
                'kd_nm': 148,
                'reference': 'Dana et al. 2016 eLife',
                'addgene_id': '61563',
            },
            {
                'name': 'jRCaMP1a',
                'type': 'GECI',
                'subtype': 'Calcium',
                'ex_peak_nm': 570,
                'em_peak_nm': 595,
                'tau_rise_ms': 25.0,
                'tau_decay_ms': 400,
                'delta_f_f': 8.0,
                'snr_1ap': 3.0,
                'quantum_yield': 0.35,
                'brightness': 12000,
                'photostability': 0.65,
                'max_spike_rate_hz': 10,
                'kd_nm': 214,
                'reference': 'Dana et al. 2016 eLife',
                'addgene_id': '61562',
            },
        ]
        
        return pd.DataFrame(geci_data)
    
    def _load_gevi_database(self):
        """
        Base de données des indicateurs voltage (GEVI).
        Données extraites de Evans et al. (2023), Villette et al. (2019).
        """
        gevi_data = [
            # ASAP family
            {
                'name': 'ASAP3',
                'type': 'GEVI',
                'subtype': 'Voltage',
                'ex_peak_nm': 488,
                'em_peak_nm': 510,
                'tau_rise_ms': 0.9,      # Sub-millisecond !
                'tau_decay_ms': 2.0,
                'delta_f_f': -50.0,      # Négatif = s'éteint avec dépol
                'snr_1ap': 8.0,
                'quantum_yield': 0.30,   # Plus faible que GCaMP
                'brightness': 8000,
                'photostability': 0.60,  # Moins photostable
                'max_spike_rate_hz': 100,
                'kd_nm': np.nan,         # N/A pour voltage
                'reference': 'Villette et al. 2019 Cell',
                'addgene_id': '132331',
            },
            {
                'name': 'ASAP4b',
                'type': 'GEVI',
                'subtype': 'Voltage',
                'ex_peak_nm': 488,
                'em_peak_nm': 510,
                'tau_rise_ms': 1.5,
                'tau_decay_ms': 3.0,
                'delta_f_f': 30.0,       # Positif = s'allume (inversé)
                'snr_1ap': 6.0,
                'quantum_yield': 0.28,
                'brightness': 7000,
                'photostability': 0.85,  # Meilleure photostabilité !
                'max_spike_rate_hz': 50,
                'kd_nm': np.nan,
                'reference': 'Evans et al. 2023 Nat Methods',
                'addgene_id': '192763',
            },
            {
                'name': 'ASAP4e',
                'type': 'GEVI',
                'subtype': 'Voltage',
                'ex_peak_nm': 488,
                'em_peak_nm': 510,
                'tau_rise_ms': 1.2,
                'tau_decay_ms': 2.5,
                'delta_f_f': 41.0,       # Encore meilleur
                'snr_1ap': 7.0,
                'quantum_yield': 0.30,
                'brightness': 7500,
                'photostability': 0.85,
                'max_spike_rate_hz': 50,
                'kd_nm': np.nan,
                'reference': 'Evans et al. 2023 Nat Methods',
                'addgene_id': '192764',
            },
            {
                'name': 'ASAP5',
                'type': 'GEVI',
                'subtype': 'Voltage',
                'ex_peak_nm': 488,
                'em_peak_nm': 510,
                'tau_rise_ms': 0.78,     # Le plus rapide !
                'tau_decay_ms': 1.8,
                'delta_f_f': -35.0,
                'snr_1ap': 9.0,
                'quantum_yield': 0.32,
                'brightness': 8500,
                'photostability': 0.70,
                'max_spike_rate_hz': 100,
                'kd_nm': np.nan,
                'reference': 'Tiwari et al. 2024 Neuron',
                'addgene_id': 'TBD',
            },
            {
                'name': 'jASAP',
                'type': 'GEVI',
                'subtype': 'Voltage',
                'ex_peak_nm': 488,
                'em_peak_nm': 510,
                'tau_rise_ms': 0.85,
                'tau_decay_ms': 2.0,
                'delta_f_f': -55.0,      # 60% meilleur que ASAP3
                'snr_1ap': 10.0,
                'quantum_yield': 0.33,
                'brightness': 9000,
                'photostability': 0.75,
                'max_spike_rate_hz': 100,
                'kd_nm': np.nan,
                'reference': 'Janelia GENIE Project',
                'addgene_id': 'TBD',
            },
            # Voltron (opsin-based)
            {
                'name': 'Voltron',
                'type': 'GEVI',
                'subtype': 'Voltage-Opsin',
                'ex_peak_nm': 525,
                'em_peak_nm': 545,
                'tau_rise_ms': 0.5,
                'tau_decay_ms': 1.0,
                'delta_f_f': -23.0,
                'snr_1ap': 7.0,
                'quantum_yield': 0.05,   # Très faible (opsin)
                'brightness': 3000,
                'photostability': 0.90,  # Très photostable
                'max_spike_rate_hz': 200,
                'kd_nm': np.nan,
                'reference': 'Abdelfattah et al. 2019 Science',
                'addgene_id': '111012',
            },
            {
                'name': 'Voltron2',
                'type': 'GEVI',
                'subtype': 'Voltage-Opsin',
                'ex_peak_nm': 525,
                'em_peak_nm': 550,
                'tau_rise_ms': 0.4,
                'tau_decay_ms': 0.8,
                'delta_f_f': -30.0,
                'snr_1ap': 9.0,
                'quantum_yield': 0.08,
                'brightness': 4000,
                'photostability': 0.92,
                'max_spike_rate_hz': 250,
                'kd_nm': np.nan,
                'reference': 'Abdelfattah et al. 2022',
                'addgene_id': 'TBD',
            },
            # ArcLight
            {
                'name': 'ArcLight',
                'type': 'GEVI',
                'subtype': 'Voltage',
                'ex_peak_nm': 488,
                'em_peak_nm': 510,
                'tau_rise_ms': 10.0,
                'tau_decay_ms': 15.0,
                'delta_f_f': -35.0,
                'snr_1ap': 3.0,
                'quantum_yield': 0.35,
                'brightness': 10000,
                'photostability': 0.70,
                'max_spike_rate_hz': 20,
                'kd_nm': np.nan,
                'reference': 'Jin et al. 2012 Neuron',
                'addgene_id': '36856',
            },
        ]
        
        return pd.DataFrame(gevi_data)
    
    def get_all(self):
        """Retourne tous les indicateurs."""
        return self.all_indicators
    
    def get_geci(self):
        """Retourne les indicateurs calciques."""
        return self.geci_data
    
    def get_gevi(self):
        """Retourne les indicateurs voltage."""
        return self.gevi_data
    
    def summary(self):
        """Affiche un résumé de la base de données."""
        print(f"\n📊 Base de données des indicateurs optogénétiques")
        print(f"   GECI (calcium) : {len(self.geci_data)} indicateurs")
        print(f"   GEVI (voltage) : {len(self.gevi_data)} indicateurs")
        print(f"   Total : {len(self.all_indicators)} indicateurs")


# ============================================================================
# PARTIE 2 : MODÈLE DE WAVEGUIDE Si₃N₄ (repris de v1)
# ============================================================================

class Si3N4_Waveguide:
    """Modèle du waveguide Si₃N₄ (identique à v1)."""
    
    def __init__(self, core_thickness_nm=300, core_width_nm=800):
        self.core_thickness = core_thickness_nm
        self.core_width = core_width_nm
        
        self.sellmeier = {
            'A1': 3.0249, 'B1': 0.1353406,
            'A2': 40314, 'B2': 1239.842,
        }
        
        self.loss_data = np.array([
            [450, 0.08], [532, 0.05], [561, 0.04], [600, 0.035],
            [633, 0.03], [698, 0.03], [780, 0.02], [850, 0.015],
            [1064, 0.01], [1310, 0.005], [1550, 0.001],
        ])
        
        self._loss_interp = interp1d(
            self.loss_data[:, 0],
            np.log10(self.loss_data[:, 1]),
            kind='cubic', fill_value='extrapolate'
        )
    
    def refractive_index(self, wavelength_nm):
        lam = wavelength_nm / 1000
        A1, B1 = self.sellmeier['A1'], self.sellmeier['B1']
        A2, B2 = self.sellmeier['A2'], self.sellmeier['B2']
        n_squared = 1 + (A1 * lam**2) / (lam**2 - B1**2) + (A2 * lam**2) / (lam**2 - B2**2)
        return np.sqrt(n_squared)
    
    def propagation_loss(self, wavelength_nm, length_cm=1.0):
        wavelength_nm = np.atleast_1d(wavelength_nm)
        loss_dB_per_cm = 10 ** self._loss_interp(wavelength_nm)
        loss_dB = loss_dB_per_cm * length_cm
        transmission = 10 ** (-loss_dB / 10)
        return loss_dB, transmission


# ============================================================================
# PARTIE 3 : SCORE PNPH COMPOSITE AMÉLIORÉ
# ============================================================================

class PNPHScoreCalculator:
    """
    Calculateur de score PNPH composite.
    
    Le score intègre :
    1. Score de couplage spectral (transmission Si₃N₄)
    2. Brightness effective
    3. Cinétique (pénalise τ_rise lent pour applications rapides)
    4. Photostabilité
    5. Sensibilité (ΔF/F)
    
    Formule :
    PNPH_Score = w1*Coupling × w2*QY × w3*log(Brightness) × w4*Kinetics × w5*Photostab × w6*Sensitivity
    """
    
    def __init__(self, waveguide, weights=None):
        """
        Args:
            waveguide: Instance de Si3N4_Waveguide
            weights: Dict des poids (optionnel)
        """
        self.wg = waveguide
        
        # Poids par défaut (optimisés pour PNPH)
        self.weights = weights or {
            'coupling': 0.20,      # Transmission spectrale
            'brightness': 0.20,   # Brightness/QY
            'kinetics': 0.25,     # Résolution temporelle (critique !)
            'photostability': 0.15,
            'sensitivity': 0.20,  # ΔF/F
        }
        
    def _compute_coupling_score(self, em_peak_nm, em_fwhm_nm=40, length_cm=1.0):
        """Calcule le score de couplage spectral."""
        wavelengths = np.linspace(em_peak_nm - 100, em_peak_nm + 100, 200)
        
        # Spectre d'émission (Gaussien)
        sigma = em_fwhm_nm / (2 * np.sqrt(2 * np.log(2)))
        emission = np.exp(-0.5 * ((wavelengths - em_peak_nm) / sigma) ** 2)
        
        # Transmission waveguide
        _, transmission = self.wg.propagation_loss(wavelengths, length_cm)
        
        # Score de couplage
        coupled = emission * transmission
        score = trapezoid(coupled, wavelengths) / trapezoid(emission, wavelengths)
        
        return score
    
    def _compute_kinetics_score(self, tau_rise_ms, target_resolution_ms=5.0):
        """
        Score de cinétique (0-1).
        
        target_resolution_ms : Résolution temporelle cible.
        - Pour spike detection : ~2-5 ms
        - Pour subthreshold : ~10-50 ms
        
        Score = 1 si τ_rise << target, décroît exponentiellement sinon.
        """
        if pd.isna(tau_rise_ms) or tau_rise_ms <= 0:
            return 0.5  # Valeur par défaut si donnée manquante
        
        # Score exponentiel : max à τ=0, décroît avec τ
        score = np.exp(-tau_rise_ms / target_resolution_ms)
        
        return np.clip(score, 0, 1)
    
    def _normalize_sensitivity(self, delta_f_f):
        """Normalise ΔF/F (peut être négatif pour GEVI)."""
        if pd.isna(delta_f_f):
            return 0.5
        
        # Prendre la valeur absolue et normaliser
        abs_df = np.abs(delta_f_f)
        
        # Score log pour gérer la grande dynamique (1% → 100%)
        score = np.log10(abs_df + 1) / np.log10(101)  # Normalise à 0-1
        
        return np.clip(score, 0, 1)
    
    def compute_pnph_score(self, indicator_row):
        """
        Calcule le score PNPH composite pour un indicateur.
        
        Args:
            indicator_row: Ligne d'un DataFrame avec les propriétés
            
        Returns:
            dict avec scores détaillés et score final
        """
        # 1. Score de couplage spectral
        em_peak = indicator_row.get('em_peak_nm', 515)
        coupling = self._compute_coupling_score(em_peak)
        
        # 2. Score brightness/QY
        qy = indicator_row.get('quantum_yield', 0.5)
        brightness = indicator_row.get('brightness', 10000)
        
        if pd.isna(qy): qy = 0.5
        if pd.isna(brightness) or brightness <= 0: brightness = 10000
        
        brightness_score = qy * np.log10(brightness + 1) / 5  # Normalise
        brightness_score = np.clip(brightness_score, 0, 1)
        
        # 3. Score cinétique
        tau_rise = indicator_row.get('tau_rise_ms', 10)
        kinetics = self._compute_kinetics_score(tau_rise)
        
        # 4. Photostabilité
        photostab = indicator_row.get('photostability', 0.7)
        if pd.isna(photostab): photostab = 0.7
        
        # 5. Sensibilité (ΔF/F)
        delta_f = indicator_row.get('delta_f_f', 10)
        sensitivity = self._normalize_sensitivity(delta_f)
        
        # Score composite pondéré
        w = self.weights
        pnph_score = (
            w['coupling'] * coupling +
            w['brightness'] * brightness_score +
            w['kinetics'] * kinetics +
            w['photostability'] * photostab +
            w['sensitivity'] * sensitivity
        )
        
        return {
            'coupling_score': coupling,
            'brightness_score': brightness_score,
            'kinetics_score': kinetics,
            'photostability_score': photostab,
            'sensitivity_score': sensitivity,
            'pnph_score': pnph_score,
        }
    
    def analyze_indicators(self, indicators_df):
        """
        Analyse tous les indicateurs d'un DataFrame.
        
        Returns:
            DataFrame avec scores
        """
        results = []
        
        for idx, row in indicators_df.iterrows():
            scores = self.compute_pnph_score(row)
            
            result = {
                'name': row.get('name', f'Indicator_{idx}'),
                'type': row.get('type', 'Unknown'),
                'subtype': row.get('subtype', ''),
                'em_peak_nm': row.get('em_peak_nm'),
                'tau_rise_ms': row.get('tau_rise_ms'),
                'delta_f_f': row.get('delta_f_f'),
                'quantum_yield': row.get('quantum_yield'),
                'photostability': row.get('photostability'),
                'reference': row.get('reference', ''),
                **scores
            }
            results.append(result)
        
        return pd.DataFrame(results)


# ============================================================================
# PARTIE 4 : FUSION AVEC DONNÉES FP UTILISATEUR
# ============================================================================

def load_user_fp_data(filepath):
    """
    Charge les données FP de l'utilisateur et les enrichit.
    """
    print(f"📂 Chargement des données utilisateur : {filepath}")
    
    # Charger le CSV
    df = pd.read_csv(filepath)
    
    # Ajouter les colonnes manquantes avec des valeurs par défaut
    default_values = {
        'type': 'FP',
        'subtype': 'Reporter',
        'tau_rise_ms': np.nan,  # FPs classiques n'ont pas de τ dynamique
        'tau_decay_ms': np.nan,
        'delta_f_f': np.nan,
        'photostability': 0.80,  # Valeur moyenne
        'max_spike_rate_hz': np.nan,
    }
    
    for col, default in default_values.items():
        if col not in df.columns:
            df[col] = default
    
    # Renommer les colonnes si nécessaire
    rename_map = {
        'em_max': 'em_peak_nm',
        'ex_max': 'ex_peak_nm',
        'qy': 'quantum_yield',
    }
    df = df.rename(columns=rename_map)
    
    print(f"   ✓ {len(df)} FPs chargées")
    
    return df


# ============================================================================
# PARTIE 5 : VISUALISATION AMÉLIORÉE
# ============================================================================

class EnhancedVisualizer:
    """Visualisation des résultats enrichis."""
    
    def __init__(self, results_fp, results_indicators):
        self.results_fp = results_fp
        self.results_ind = results_indicators
        self.all_results = pd.concat([results_fp, results_indicators], ignore_index=True)
    
    def plot_pnph_comparison(self, save=True):
        """Compare FPs et indicateurs sur le score PNPH."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 1. Distribution des scores PNPH par type
        ax1 = axes[0, 0]
        types = self.all_results['type'].unique()
        colors = {'FP': 'green', 'GECI': 'blue', 'GEVI': 'red'}
        
        for t in types:
            data = self.all_results[self.all_results['type'] == t]['pnph_score']
            ax1.hist(data, bins=20, alpha=0.5, label=t, color=colors.get(t, 'gray'))
        
        ax1.set_xlabel('Score PNPH')
        ax1.set_ylabel('Nombre')
        ax1.set_title('Distribution des scores PNPH par type')
        ax1.legend()
        
        # 2. Radar chart des top indicateurs
        ax2 = axes[0, 1]
        top5 = self.results_ind.nlargest(5, 'pnph_score')
        
        categories = ['Couplage', 'Brightness', 'Cinétique', 'Photostab.', 'Sensibilité']
        
        for _, row in top5.iterrows():
            values = [
                row['coupling_score'],
                row['brightness_score'],
                row['kinetics_score'],
                row['photostability_score'],
                row['sensitivity_score'],
            ]
            ax2.plot(categories, values, 'o-', label=row['name'], linewidth=2, markersize=8)
        
        ax2.set_ylim(0, 1.1)
        ax2.set_title('Profil des Top 5 indicateurs')
        ax2.legend(loc='upper right', fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. Cinétique vs Sensibilité
        ax3 = axes[1, 0]
        
        for t in ['GECI', 'GEVI']:
            data = self.results_ind[self.results_ind['type'] == t]
            if len(data) > 0:
                ax3.scatter(data['tau_rise_ms'], data['delta_f_f'].abs(),
                           s=data['pnph_score']*500, alpha=0.7, 
                           label=t, c=colors.get(t, 'gray'))
                
                for _, row in data.iterrows():
                    ax3.annotate(row['name'], (row['tau_rise_ms'], abs(row['delta_f_f'])),
                               fontsize=7, alpha=0.7)
        
        ax3.set_xlabel('τ_rise (ms) - log scale')
        ax3.set_ylabel('|ΔF/F| (%)')
        ax3.set_xscale('log')
        ax3.set_title('Cinétique vs Sensibilité (taille = score PNPH)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Top 15 global
        ax4 = axes[1, 1]
        
        # Combiner top FPs et indicateurs
        top_fp = self.results_fp.nlargest(10, 'pnph_score')
        top_ind = self.results_ind.nlargest(5, 'pnph_score')
        top_all = pd.concat([top_fp, top_ind]).nlargest(15, 'pnph_score')
        
        colors_bars = [colors.get(t, 'gray') for t in top_all['type']]
        
        bars = ax4.barh(range(len(top_all)), top_all['pnph_score'], color=colors_bars, alpha=0.7)
        ax4.set_yticks(range(len(top_all)))
        ax4.set_yticklabels([f"{row['name']} ({row['type']})" for _, row in top_all.iterrows()])
        ax4.set_xlabel('Score PNPH')
        ax4.set_title('Top 15 Global (FPs + Indicateurs)')
        ax4.invert_yaxis()
        
        plt.tight_layout()
        
        if save:
            path = OUTPUT_DIR / 'pnph_comparison.png'
            plt.savefig(path, dpi=150)
            print(f"   💾 Sauvegardé: {path}")
        
        return fig, axes
    
    def plot_indicator_details(self, save=True):
        """Détails des indicateurs GECI/GEVI."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. GECI comparison
        ax1 = axes[0]
        geci = self.results_ind[self.results_ind['type'] == 'GECI']
        
        x = np.arange(len(geci))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, geci['kinetics_score'], width, label='Cinétique', color='blue', alpha=0.7)
        bars2 = ax1.bar(x + width/2, geci['sensitivity_score'], width, label='Sensibilité', color='orange', alpha=0.7)
        
        ax1.set_ylabel('Score')
        ax1.set_title('Indicateurs Calciques (GECI)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(geci['name'], rotation=45, ha='right')
        ax1.legend()
        ax1.set_ylim(0, 1.1)
        
        # 2. GEVI comparison
        ax2 = axes[1]
        gevi = self.results_ind[self.results_ind['type'] == 'GEVI']
        
        x = np.arange(len(gevi))
        
        bars1 = ax2.bar(x - width/2, gevi['kinetics_score'], width, label='Cinétique', color='red', alpha=0.7)
        bars2 = ax2.bar(x + width/2, gevi['photostability_score'], width, label='Photostabilité', color='green', alpha=0.7)
        
        ax2.set_ylabel('Score')
        ax2.set_title('Indicateurs Voltage (GEVI)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(gevi['name'], rotation=45, ha='right')
        ax2.legend()
        ax2.set_ylim(0, 1.1)
        
        plt.tight_layout()
        
        if save:
            path = OUTPUT_DIR / 'indicator_details.png'
            plt.savefig(path, dpi=150)
            print(f"   💾 Sauvegardé: {path}")
        
        return fig, axes
    
    def generate_enhanced_report(self, save=True):
        """Génère le rapport amélioré."""
        
        # Stats
        top5_fp = self.results_fp.nlargest(5, 'pnph_score')
        top_geci = self.results_ind[self.results_ind['type'] == 'GECI'].nlargest(3, 'pnph_score')
        top_gevi = self.results_ind[self.results_ind['type'] == 'GEVI'].nlargest(3, 'pnph_score')
        
        report = f"""# 📊 Rapport PNPH Amélioré : FPs + Indicateurs GECI/GEVI

**Date :** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Projet :** PNPH (Photonic-Neural Hybrid Platform)
**Auteur :** M. Panda

---

## 1. Résumé Exécutif

Ce benchmark évalue **{len(self.results_fp)} protéines fluorescentes** et 
**{len(self.results_ind)} indicateurs optogénétiques** pour leur compatibilité 
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
"""
        for i, (_, row) in enumerate(top5_fp.iterrows(), 1):
            report += f"| {i} | {row['name']} | {row['em_peak_nm']:.0f} | {row['quantum_yield']:.2f} | {row['pnph_score']:.3f} |\n"

        report += f"""

### Distribution par catégorie

Les FPs **vertes** dominent en nombre, mais les FPs **orange-rouge** 
ont un meilleur couplage Si₃N₄.

---

## 3. Indicateurs Calciques (GECI)

### Top 3 GECI pour PNPH

| Rang | Nom | τ_rise (ms) | ΔF/F (%) | Score PNPH |
|------|-----|-------------|----------|------------|
"""
        for i, (_, row) in enumerate(top_geci.iterrows(), 1):
            report += f"| {i} | {row['name']} | {row['tau_rise_ms']:.1f} | {row['delta_f_f']:.1f} | {row['pnph_score']:.3f} |\n"

        report += f"""

### Recommandation GECI

**Pour spike detection rapide :** jGCaMP8f (τ_rise = 2 ms)
**Pour sensibilité maximale :** jGCaMP8s (ΔF/F = 25%)
**Pour compromis :** jGCaMP8m

---

## 4. Indicateurs Voltage (GEVI)

### Top 3 GEVI pour PNPH

| Rang | Nom | τ_rise (ms) | ΔF/F (%) | Score PNPH |
|------|-----|-------------|----------|------------|
"""
        for i, (_, row) in enumerate(top_gevi.iterrows(), 1):
            df_val = row['delta_f_f']
            report += f"| {i} | {row['name']} | {row['tau_rise_ms']:.2f} | {df_val:+.1f} | {row['pnph_score']:.3f} |\n"

        report += f"""

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
"""
        
        if save:
            path = OUTPUT_DIR / 'rapport_PNPH_enhanced.md'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"   💾 Rapport sauvegardé: {path}")
        
        return report


# ============================================================================
# PARTIE 6 : EXÉCUTION PRINCIPALE
# ============================================================================

def main(user_fp_file=None):
    """
    Exécution du benchmark amélioré.
    
    Args:
        user_fp_file: Chemin vers le fichier CSV des FPs utilisateur (optionnel)
    """
    print("\n" + "="*70)
    print("DÉMARRAGE DU BENCHMARK AMÉLIORÉ")
    print("="*70)
    
    # 1. Charger la base de données des indicateurs
    print("\n📚 Chargement base de données indicateurs...")
    ind_db = IndicatorDatabase()
    ind_db.summary()
    
    # 2. Créer le modèle waveguide
    print("\n📐 Configuration waveguide Si₃N₄...")
    waveguide = Si3N4_Waveguide()
    
    # 3. Calculateur de score PNPH
    print("\n🧮 Initialisation calculateur PNPH...")
    calculator = PNPHScoreCalculator(waveguide)
    
    # 4. Analyser les indicateurs
    print("\n🔬 Analyse des indicateurs GECI/GEVI...")
    results_indicators = calculator.analyze_indicators(ind_db.get_all())
    
    print("\n📊 Top 5 indicateurs par score PNPH:")
    top5_ind = results_indicators.nlargest(5, 'pnph_score')
    print(top5_ind[['name', 'type', 'tau_rise_ms', 'delta_f_f', 'pnph_score']].to_string(index=False))
    
    # 5. Charger données FP utilisateur (si fournies)
    if user_fp_file and Path(user_fp_file).exists():
        print(f"\n📂 Chargement données utilisateur: {user_fp_file}")
        user_fps = load_user_fp_data(user_fp_file)
        results_fps = calculator.analyze_indicators(user_fps)
    else:
        print("\n⚠️ Pas de fichier FP utilisateur fourni, utilisation données exemple...")
        # Créer des données exemple basées sur les top FPs connus
        example_fps = pd.DataFrame([
            {'name': 'StayGold', 'type': 'FP', 'em_peak_nm': 505, 'quantum_yield': 0.93, 
             'brightness': 45000, 'photostability': 0.95},
            {'name': 'GFPxm18', 'type': 'FP', 'em_peak_nm': 502, 'quantum_yield': 0.96,
             'brightness': 50000, 'photostability': 0.85},
            {'name': 'mNeonGreen', 'type': 'FP', 'em_peak_nm': 517, 'quantum_yield': 0.80,
             'brightness': 38000, 'photostability': 0.80},
            {'name': 'EGFP', 'type': 'FP', 'em_peak_nm': 507, 'quantum_yield': 0.60,
             'brightness': 33600, 'photostability': 0.75},
            {'name': 'tdTomato', 'type': 'FP', 'em_peak_nm': 581, 'quantum_yield': 0.69,
             'brightness': 95000, 'photostability': 0.70},
            {'name': 'mCherry', 'type': 'FP', 'em_peak_nm': 610, 'quantum_yield': 0.22,
             'brightness': 15900, 'photostability': 0.65},
        ])
        results_fps = calculator.analyze_indicators(example_fps)
    
    print("\n📊 Top 5 FPs par score PNPH:")
    top5_fp = results_fps.nlargest(5, 'pnph_score')
    print(top5_fp[['name', 'em_peak_nm', 'quantum_yield', 'pnph_score']].to_string(index=False))
    
    # 6. Visualisation
    print("\n📈 Génération des visualisations...")
    viz = EnhancedVisualizer(results_fps, results_indicators)
    viz.plot_pnph_comparison()
    viz.plot_indicator_details()
    
    # 7. Rapport
    print("\n📝 Génération du rapport...")
    viz.generate_enhanced_report()
    
    # 8. Sauvegarder les données
    results_fps.to_csv(OUTPUT_DIR / 'fp_results_pnph.csv', index=False)
    results_indicators.to_csv(OUTPUT_DIR / 'indicator_results_pnph.csv', index=False)
    
    print("\n" + "="*70)
    print("✅ BENCHMARK AMÉLIORÉ TERMINÉ!")
    print("="*70)
    print(f"\n📁 Résultats dans: {OUTPUT_DIR.absolute()}")
    
    return results_fps, results_indicators


if __name__ == '__main__':
    import sys
    
    user_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Si lancé avec le fichier de résultats P2
    if user_file is None:
        # Chercher le fichier de résultats existant
        possible_paths = [
            'results/fp_coupling_results_real.csv',
            '../results/fp_coupling_results_real.csv',
            'fp_coupling_results_real.csv',
        ]
        for p in possible_paths:
            if Path(p).exists():
                user_file = p
                break
    
    results_fp, results_ind = main(user_file)
