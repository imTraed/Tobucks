#!/usr/bin/env python
"""
Script para generar una SECRET_KEY segura para Flask
Ejecutar: python generate_secret_key.py
"""

import secrets
import base64

def generate_secret_key(length=32):
    """Generar una clave secreta segura"""
    # Usando secrets para criptografía segura
    random_bytes = secrets.token_bytes(length)
    return base64.b64encode(random_bytes).decode('utf-8')

if __name__ == "__main__":
    key = generate_secret_key()
    
    print("\n" + "="*60)
    print("🔐 SECRET_KEY GENERADA PARA FLASK")
    print("="*60)
    print(f"\nCopia esta clave en tu .env o variables de entorno:\n")
    print(f"SECRET_KEY={key}\n")
    print("="*60)
    print("\n✅ IMPORTANTE:")
    print("   - Guarda esta clave en un lugar seguro")
    print("   - Nunca la compartas ni la publiques")
    print("   - Usa la misma clave en producción para firmar sesiones")
    print("   - Si la pierdes, todos los usuarios tendrán que re-login")
    print("\n")
