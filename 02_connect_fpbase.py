#!/usr/bin/env python3
"""
================================================================================
02_connect_fpbase.py - Connexion à tes données FPbase réelles
================================================================================

Ce script t'aide à :
1. Charger ton dataset FPbase existant (685 FPs)
2. Le convertir au format requis par le benchmark
3. Lancer l'analyse avec tes vraies données

Usage :
    python 02_connect_fpbase.py --input ton_dataset.csv
    
Ou interactivement :
    python 02_connect_fpbase.py

================================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json

# Import du benchmark principal
from importlib.util import spec_from_file_location, module_from_spec

def load_benchmark_module():
    """Charge le module de benchmark."""
    spec = spec_from_file_location("benchmark", "./01_fp_sin_coupling_benchmark.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class FPbaseConnector:
    """
    Connecteur pour charger et convertir des données FPbase.
    """
    
    # Mapping des colonnes possibles vers le format standard
    COLUMN_MAPPINGS = {
        # λ émission
        'em_peak_nm': ['em_peak_nm', 'emission_max', 'em_max', 'λ_em', 
                       'emission_peak', 'em', 'emission_wavelength', 'EmMax', 'em_peak'],
        # λ excitation
        'ex_peak_nm': ['ex_peak_nm', 'excitation_max', 'ex_max', 'λ_ex',
                       'excitation_peak', 'ex', 'excitation_wavelength', 'ExMax', 'ex_peak'],
        # Rendement quantique
        'quantum_yield': ['quantum_yield', 'qy', 'QY', 'quantumYield', 
                          'quantum_efficiency', 'phi', 'Qy'],
        # Brillance
        'brightness': ['brightness', 'Brightness', 'relative_brightness'],
        # Coefficient d'extinction
        'extinction': ['extinction', 'epsilon', 'ext_coeff', 'EC',
                       'molar_extinction', 'extinction_coefficient', 'ExtCoeff'],
        # Nom
        'name': ['name', 'Name', 'protein_name', 'fp_name', 'slug'],
        # ID
        'id': ['id', 'ID', 'uuid', 'fpbase_id', 'protein_id', 'ProteinID'],
        # FWHM
        'em_fwhm_nm': ['em_fwhm', 'emission_fwhm', 'em_bandwidth'],
        'ex_fwhm_nm': ['ex_fwhm', 'excitation_fwhm', 'ex_bandwidth'],
    }
    
    # Catégories spectrales
    SPECTRAL_CATEGORIES = {
        (350, 420): 'UV',
        (420, 460): 'Blue', 
        (460, 495): 'Cyan',
        (495, 530): 'Green',
        (530, 565): 'Yellow',
        (565, 600): 'Orange',
        (600, 650): 'Red',
        (650, 800): 'Far-Red',
    }
    
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.raw_data = None
        self.converted_data = None
        
    def load(self, filepath=None):
        """
        Charge un fichier CSV/JSON de données FPbase.
        """
        if filepath:
            self.filepath = filepath
            
        path = Path(self.filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {path}")
        
        print(f"📂 Chargement de {path.name}...")
        
        # Détecter le format
        if path.suffix.lower() == '.json':
            self.raw_data = pd.read_json(path)
        elif path.suffix.lower() == '.csv':
            self.raw_data = pd.read_csv(path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            self.raw_data = pd.read_excel(path)
        else:
            # Essayer CSV par défaut
            self.raw_data = pd.read_csv(path)
        
        print(f"   ✓ {len(self.raw_data)} entrées chargées")
        print(f"   Colonnes: {list(self.raw_data.columns)}")
        
        return self
    
    def _find_column(self, standard_name):
        """Trouve la colonne correspondante dans les données brutes."""
        possible_names = self.COLUMN_MAPPINGS.get(standard_name, [standard_name])
        
        for col in possible_names:
            if col in self.raw_data.columns:
                return col
            # Essayer en minuscules
            for raw_col in self.raw_data.columns:
                if raw_col.lower() == col.lower():
                    return raw_col
        
        return None
    
    def _categorize_emission(self, em_nm):
        """Assigne une catégorie spectrale basée sur λ_em."""
        for (low, high), category in self.SPECTRAL_CATEGORIES.items():
            if low <= em_nm < high:
                return category
        return 'Other'
    
    def convert(self):
        """
        Convertit les données au format standard du benchmark.
        """
        if self.raw_data is None:
            raise ValueError("Charger les données d'abord avec load()")
        
        print("\n🔄 Conversion au format standard...")
        
        converted = pd.DataFrame()
        
        # ID
        id_col = self._find_column('id')
        if id_col:
            converted['id'] = self.raw_data[id_col]
        else:
            converted['id'] = [f'FP_{i:04d}' for i in range(len(self.raw_data))]
        
        # Nom
        name_col = self._find_column('name')
        if name_col:
            converted['name'] = self.raw_data[name_col]
        else:
            converted['name'] = converted['id']
        
        # λ émission (REQUIS)
        em_col = self._find_column('em_peak_nm')
        if em_col is None:
            raise ValueError("❌ Colonne λ émission non trouvée! "
                           f"Colonnes disponibles: {list(self.raw_data.columns)}")
        converted['em_peak_nm'] = pd.to_numeric(self.raw_data[em_col], errors='coerce')
        
        # λ excitation (optionnel)
        ex_col = self._find_column('ex_peak_nm')
        if ex_col:
            converted['ex_peak_nm'] = pd.to_numeric(self.raw_data[ex_col], errors='coerce')
        else:
            converted['ex_peak_nm'] = converted['em_peak_nm'] - 20  # Stokes shift estimé
        
        # Quantum yield (optionnel)
        qy_col = self._find_column('quantum_yield')
        if qy_col:
            converted['quantum_yield'] = pd.to_numeric(self.raw_data[qy_col], errors='coerce')
            # Normaliser si >1 (parfois en pourcentage)
            if converted['quantum_yield'].max() > 1:
                converted['quantum_yield'] /= 100
            # Remplacer les NaN par une valeur par défaut
            converted['quantum_yield'] = converted['quantum_yield'].fillna(0.5)
        else:
            converted['quantum_yield'] = 0.5  # Valeur par défaut
        
        # Brightness
        bright_col = self._find_column('brightness')
        ext_col = self._find_column('extinction')
        
        if bright_col:
            converted['brightness'] = pd.to_numeric(self.raw_data[bright_col], errors='coerce')
            converted['brightness'] = converted['brightness'].fillna(1000)  # Valeur par défaut
        elif ext_col:
            # Calculer: brightness = extinction × QY
            ext = pd.to_numeric(self.raw_data[ext_col], errors='coerce').fillna(50000)
            converted['brightness'] = ext * converted['quantum_yield']
        else:
            converted['brightness'] = converted['quantum_yield'] * 50000  # Estimé
        
        # S'assurer qu'il n'y a pas de valeurs négatives ou nulles
        converted['brightness'] = converted['brightness'].clip(lower=1)
        
        # FWHM émission (optionnel)
        em_fwhm_col = self._find_column('em_fwhm_nm')
        if em_fwhm_col:
            converted['em_fwhm_nm'] = pd.to_numeric(self.raw_data[em_fwhm_col], errors='coerce')
        else:
            converted['em_fwhm_nm'] = 40  # Valeur typique
        
        # FWHM excitation (optionnel)
        ex_fwhm_col = self._find_column('ex_fwhm_nm')
        if ex_fwhm_col:
            converted['ex_fwhm_nm'] = pd.to_numeric(self.raw_data[ex_fwhm_col], errors='coerce')
        else:
            converted['ex_fwhm_nm'] = 35  # Valeur typique
        
        # Catégorie spectrale
        converted['category'] = converted['em_peak_nm'].apply(self._categorize_emission)
        
        # Couleur pour plots
        color_map = {
            'UV': 'violet', 'Blue': 'blue', 'Cyan': 'cyan',
            'Green': 'green', 'Yellow': 'gold', 'Orange': 'orange',
            'Red': 'red', 'Far-Red': 'darkred', 'Other': 'gray'
        }
        converted['color'] = converted['category'].map(color_map)
        
        # Stokes shift
        converted['stokes_shift_nm'] = converted['em_peak_nm'] - converted['ex_peak_nm']
        
        # Nettoyer les NaN
        initial_count = len(converted)
        converted = converted.dropna(subset=['em_peak_nm'])
        converted = converted[converted['em_peak_nm'] > 0]
        
        if len(converted) < initial_count:
            print(f"   ⚠️ {initial_count - len(converted)} entrées supprimées (données manquantes)")
        
        self.converted_data = converted
        
        print(f"   ✓ {len(converted)} FPs converties")
        print(f"\n   📊 Distribution par catégorie:")
        for cat, count in converted['category'].value_counts().items():
            print(f"      {cat}: {count}")
        
        return self
    
    def save(self, output_path='data/fpbase_converted.csv'):
        """Sauvegarde les données converties."""
        if self.converted_data is None:
            raise ValueError("Convertir les données d'abord avec convert()")
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        self.converted_data.to_csv(path, index=False)
        print(f"\n💾 Données sauvegardées: {path}")
        
        return path
    
    def run_benchmark(self):
        """
        Lance le benchmark avec les données converties.
        """
        if self.converted_data is None:
            raise ValueError("Convertir les données d'abord avec convert()")
        
        print("\n" + "="*70)
        print("LANCEMENT DU BENCHMARK AVEC TES DONNÉES")
        print("="*70)
        
        # Sauvegarder temporairement
        temp_path = Path('data/temp_fpbase.csv')
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        self.converted_data.to_csv(temp_path, index=False)
        
        # Charger et exécuter le benchmark
        benchmark = load_benchmark_module()
        
        # Créer le waveguide
        waveguide = benchmark.Si3N4_Waveguide()
        
        # Charger les données
        fp_db = benchmark.FPDatabase(data_source=str(temp_path))
        fp_db.fps = self.converted_data  # Utiliser directement les données converties
        
        # Analyser
        analyzer = benchmark.CouplingAnalyzer(waveguide, fp_db)
        results = analyzer.analyze_all()
        
        # Visualiser
        viz = benchmark.CouplingVisualizer(analyzer)
        viz.plot_waveguide_transmission()
        viz.plot_coupling_distribution()
        viz.plot_top_candidates()
        viz.generate_report()
        
        # Sauvegarder résultats
        results.to_csv('results/fp_coupling_results_real.csv', index=False)
        
        # Nettoyer
        temp_path.unlink()
        
        return results


def interactive_mode():
    """Mode interactif pour guider l'utilisateur."""
    print("\n" + "="*70)
    print("🔌 CONNECTEUR FPBASE - Mode Interactif")
    print("="*70)
    
    print("""
Ce script t'aide à connecter tes données FPbase au benchmark.

Fichiers supportés :
- CSV (.csv)
- JSON (.json)
- Excel (.xlsx, .xls)

Colonnes requises :
- λ émission (em_peak_nm, emission_max, λ_em, ...)

Colonnes optionnelles :
- λ excitation
- Rendement quantique
- Brillance / Coefficient d'extinction
- Nom, ID
""")
    
    # Demander le fichier
    filepath = input("\n📁 Chemin vers ton fichier de données FPbase: ").strip()
    
    if not filepath:
        print("\n❌ Aucun fichier spécifié. Abandon.")
        return
    
    # Charger et convertir
    connector = FPbaseConnector()
    
    try:
        connector.load(filepath)
        connector.convert()
        
        # Demander si lancer le benchmark
        response = input("\n🚀 Lancer le benchmark maintenant? [O/n]: ").strip().lower()
        
        if response != 'n':
            connector.run_benchmark()
            print("\n✅ Benchmark terminé! Résultats dans ./results/")
        else:
            # Sauvegarder seulement
            output = input("💾 Chemin de sortie [data/fpbase_converted.csv]: ").strip()
            if not output:
                output = 'data/fpbase_converted.csv'
            connector.save(output)
            print(f"\n✅ Données converties sauvegardées dans {output}")
            print("   Lance le benchmark avec :")
            print(f"   python 01_fp_sin_coupling_benchmark.py")
            print(f"   (modifier fp_db = FPDatabase(data_source='{output}'))")
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Connecter des données FPbase au benchmark Si₃N₄'
    )
    parser.add_argument('--input', '-i', type=str, 
                       help='Fichier de données FPbase')
    parser.add_argument('--output', '-o', type=str,
                       default='data/fpbase_converted.csv',
                       help='Fichier de sortie')
    parser.add_argument('--run-benchmark', '-r', action='store_true',
                       help='Lancer le benchmark après conversion')
    
    args = parser.parse_args()
    
    if args.input:
        # Mode ligne de commande
        connector = FPbaseConnector()
        connector.load(args.input)
        connector.convert()
        connector.save(args.output)
        
        if args.run_benchmark:
            connector.run_benchmark()
    else:
        # Mode interactif
        interactive_mode()


if __name__ == '__main__':
    main()