"""
Module utilitaire pour la gestion des fichiers.
Normalise le stockage des pièces jointes dans temp_files/.
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path


class FileManager:
    """Gestionnaire centralisé pour le stockage des fichiers."""
    
    def __init__(self, base_dir=None):
        """
        Initialise le gestionnaire de fichiers.
        
        Args:
            base_dir: Répertoire de base pour temp_files. 
                     Par défaut: ../temp_files depuis le dossier scripts
        """
        if base_dir is None:
            # Répertoire du script actuel
            script_dir = Path(__file__).parent
            # Remonter au répertoire du projet et aller dans temp_files
            self.temp_files_dir = script_dir.parent / "temp_files"
        else:
            self.temp_files_dir = Path(base_dir)
        
        # Créer le répertoire s'il n'existe pas
        self.temp_files_dir.mkdir(exist_ok=True)
        
        # Créer des sous-dossiers par source
        self.sources = {
            'gmail': self.temp_files_dir / 'gmail',
            'whatsapp': self.temp_files_dir / 'whatsapp',
            'bank': self.temp_files_dir / 'bank',
            'other': self.temp_files_dir / 'other'
        }
        
        for folder in self.sources.values():
            folder.mkdir(exist_ok=True)
    
    def generate_unique_filename(self, original_filename, source='other', content=None):
        """
        Génère un nom de fichier unique pour éviter les collisions.
        
        Args:
            original_filename: Nom du fichier original
            source: Source du fichier (gmail, whatsapp, bank)
            content: Contenu binaire du fichier (optionnel, pour hash)
        
        Returns:
            str: Nom de fichier unique
        """
        # Extraire l'extension
        file_path = Path(original_filename)
        name = file_path.stem
        extension = file_path.suffix
        
        # Timestamp pour unicité
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Hash du contenu si fourni (pour éviter les doublons)
        if content:
            content_hash = hashlib.md5(content).hexdigest()[:8]
            unique_name = f"{name}_{timestamp}_{content_hash}{extension}"
        else:
            unique_name = f"{name}_{timestamp}{extension}"
        
        return unique_name
    
    def save_file(self, content, filename, source='other', original_filename=None):
        """
        Sauvegarde un fichier dans temp_files avec organisation par source.
        
        Args:
            content: Contenu binaire du fichier
            filename: Nom du fichier à sauvegarder
            source: Source du fichier (gmail, whatsapp, bank)
            original_filename: Nom original du fichier (pour générer un nom unique)
        
        Returns:
            str: Chemin absolu du fichier sauvegardé
        """
        # Sélectionner le dossier source
        source_folder = self.sources.get(source, self.sources['other'])
        
        # Générer un nom unique si demandé
        if original_filename:
            filename = self.generate_unique_filename(original_filename, source, content)
        
        # Chemin complet du fichier
        file_path = source_folder / filename
        
        # Sauvegarder le fichier
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Retourner le chemin absolu
        return str(file_path.absolute())
    
    def save_file_from_path(self, source_path, source='other', keep_original_name=False):
        """
        Copie un fichier existant vers temp_files.
        
        Args:
            source_path: Chemin du fichier source
            source: Source du fichier (gmail, whatsapp, bank)
            keep_original_name: Si True, garde le nom original, sinon génère un nom unique
        
        Returns:
            str: Chemin absolu du fichier copié
        """
        source_path = Path(source_path)
        
        # Lire le contenu
        with open(source_path, 'rb') as f:
            content = f.read()
        
        # Déterminer le nom du fichier
        if keep_original_name:
            filename = source_path.name
        else:
            filename = None  # Sera généré automatiquement
        
        return self.save_file(
            content=content,
            filename=filename or source_path.name,
            source=source,
            original_filename=source_path.name if not keep_original_name else None
        )
    
    def get_file_info(self, file_path):
        """
        Récupère des informations sur un fichier.
        
        Args:
            file_path: Chemin du fichier
        
        Returns:
            dict: Informations du fichier (taille, type, etc.)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        
        return {
            'path': str(file_path.absolute()),
            'filename': file_path.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'extension': file_path.suffix,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def cleanup_old_files(self, days=30):
        """
        Supprime les fichiers plus anciens que X jours.
        
        Args:
            days: Nombre de jours
        
        Returns:
            int: Nombre de fichiers supprimés
        """
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for source_folder in self.sources.values():
            for file_path in source_folder.glob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
        
        return deleted_count


# Instance globale du gestionnaire de fichiers
file_manager = FileManager()


def save_attachment(content, filename, source='other'):
    """
    Fonction helper pour sauvegarder rapidement une pièce jointe.
    
    Args:
        content: Contenu binaire du fichier
        filename: Nom du fichier
        source: Source (gmail, whatsapp, bank)
    
    Returns:
        str: Chemin absolu du fichier
    """
    return file_manager.save_file(content, filename, source, original_filename=filename)


if __name__ == "__main__":
    # Test du module
    print("🧪 Test du gestionnaire de fichiers...")
    
    fm = FileManager()
    print(f"✅ Répertoire temp_files: {fm.temp_files_dir}")
    print(f"✅ Sous-dossiers créés:")
    for source, path in fm.sources.items():
        print(f"   - {source}: {path}")
    
    # Test de sauvegarde
    test_content = b"Test content for file manager"
    test_file = fm.save_file(test_content, "test.txt", source="other", original_filename="test.txt")
    print(f"\n✅ Fichier test créé: {test_file}")
    
    # Informations du fichier
    info = fm.get_file_info(test_file)
    print(f"✅ Informations du fichier:")
    print(f"   - Nom: {info['filename']}")
    print(f"   - Taille: {info['size']} bytes")
    print(f"   - Créé: {info['created']}")
    
    print("\n✅ Module file_manager opérationnel!")
