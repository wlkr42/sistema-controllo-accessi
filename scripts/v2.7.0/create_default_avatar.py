#!/usr/bin/env python3
# Crea un avatar di default usando PIL

from PIL import Image, ImageDraw, ImageFont
import os

def create_default_avatar():
    """Crea un avatar di default con icona utente"""
    
    # Dimensioni avatar
    size = (200, 200)
    
    # Crea immagine con sfondo grigio chiaro
    img = Image.new('RGB', size, color='#E0E0E0')
    draw = ImageDraw.Draw(img)
    
    # Disegna un cerchio per la testa
    head_center = (100, 80)
    head_radius = 35
    draw.ellipse(
        [head_center[0] - head_radius, head_center[1] - head_radius,
         head_center[0] + head_radius, head_center[1] + head_radius],
        fill='#9E9E9E'
    )
    
    # Disegna il corpo (semicerchio)
    body_top = 120
    body_width = 70
    draw.ellipse(
        [100 - body_width, body_top,
         100 + body_width, body_top + 100],
        fill='#9E9E9E'
    )
    
    # Copri la parte inferiore per creare un semicerchio
    draw.rectangle(
        [0, 170, 200, 200],
        fill='#E0E0E0'
    )
    
    # Salva l'immagine
    output_path = '/opt/access_control/src/api/static/img/default-avatar.png'
    img.save(output_path, 'PNG')
    print(f"✓ Avatar di default creato: {output_path}")
    
    return output_path

if __name__ == "__main__":
    try:
        # Installa PIL se necessario
        import subprocess
        subprocess.run(['pip3', 'install', 'Pillow'], capture_output=True)
        
        path = create_default_avatar()
        print(f"✅ Avatar creato con successo!")
    except Exception as e:
        print(f"❌ Errore: {e}")