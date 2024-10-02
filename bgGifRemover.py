from PIL import Image, ImageSequence
from rembg import remove
import io

def remove_background_gif(input_path, output_path):
    # Ouvrir le GIF
    gif = Image.open(input_path)

    # Liste pour stocker les nouveaux cadres après suppression de l'arrière-plan
    frames = []
    
    # Conserver les durées, méthode de disposal et autres métadonnées
    durations = []
    disposal_methods = []
    transparency_index = gif.info.get('transparency', None)  # Transparence initiale si disponible
    
    # Parcourir chaque cadre du GIF
    for frame in ImageSequence.Iterator(gif):
        # Conserver les métadonnées de durée et de mode d'élimination (disposal)
        durations.append(gif.info['duration'])
        disposal_methods.append(gif.disposal_method if hasattr(gif, 'disposal_method') else 2)
        
        # Convertir chaque cadre en mode RGBA pour gérer la transparence
        frame = frame.convert("RGBA")

        # Convertir le cadre en bytes pour l'utiliser avec rembg
        with io.BytesIO() as buffer:
            frame.save(buffer, format="PNG")
            frame_bytes = buffer.getvalue()

        # Supprimer l'arrière-plan avec rembg
        frame_no_bg_bytes = remove(frame_bytes)

        # Charger les données de l'image sans arrière-plan en tant qu'image PIL
        frame_no_bg = Image.open(io.BytesIO(frame_no_bg_bytes)).convert("RGBA")

        # Ajuster la taille du cadre sans arrière-plan pour qu'elle corresponde au cadre original
        frame_no_bg = frame_no_bg.resize(gif.size, Image.Resampling.LANCZOS)

        # Ajouter le cadre modifié à la liste des cadres
        frames.append(frame_no_bg)

    # Sauvegarder le nouveau GIF en conservant l'animation et la durée d'origine
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=gif.info.get("loop", 0),
        disposal=disposal_methods,
        transparency=transparency_index,
        optimize=False  # Ne pas optimiser pour éviter les artefacts
    )

# Exemple d'utilisation
input_gif = "assets/StudOr.gif"  # Chemin vers le GIF original
output_gif = "assets/StudOr_bg_removed.gif"  # Chemin du GIF de sortie

# Retirer l'arrière-plan mais préserver le texte blanc
remove_background_gif(input_gif, output_gif)
