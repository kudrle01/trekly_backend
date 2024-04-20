# TREKLY BACKEND

## Popis
TREKLY FRONTEND naleznete zde: https://github.com/kudrle01/trekly_frontend

## Požadavky
Pro spuštění aplikace je nezbytné mít nainstalované následující:
- Python (doporučujeme verzi 3.x)
- pip (Python package installer)

## Instalace

Před spuštěním aplikace je potřeba nainstalovat závislosti a nakonfigurovat prostředí. Postupujte podle následujících kroků:

### 1. Klonování repozitáře
Nejprve klonujte repozitář do vašeho lokálního prostředí pomocí Git:
```bash
git clone https://github.com/kudrle01/trekly_backend
cd trekly_backend
```
### 2. Instalace závislostí
Instalujte všechny potřebné závislosti uvedené v souboru `requirements.txt`:
```bash
pip install -r requirements.txt
```
### 3. Nastavení konfigurace
Konfigurace aplikace vyžaduje nastavení prostředí pomocí `.env` souboru. Pro zajištění bezpečnosti a správné funkčnosti aplikace, proveďte následující kroky:

1. Zkopírujte šablonu konfiguračního souboru a pojmenujte ji jako `.env`:
   ```bash
   cp .env.example .env
   ```
2. Otevřete .env soubor ve vašem preferovaném textovém editoru a vyplňte potřebné údaje (např. přístupové klíče, hesla a další konfigurační proměnné) podle komentářů v souboru.

### 4. Spuštění aplikace
Po úspěšném dokončení instalace závislostí a konfigurace nastavení můžete aplikaci spustit následujícím příkazem:

```bash
python run.py
```
## Licence
Tento software je distribuován pod licencí uvedenou v souboru `LICENSE`. Pro podrobnosti o vašich právech a omezeních se prosím odkážete na tento dokument.
