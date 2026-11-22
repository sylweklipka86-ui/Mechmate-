# Instrukcja instalacji

Instrukcja dotyczy Windows i skryptu śledzącego partię z kamerki.

## 1. Zainstaluj Pythona

Zainstaluj Python 3.11 lub nowszy z [python.org](https://www.python.org/downloads/).
Podczas instalacji zaznacz opcję dodania Pythona do `PATH`. Sprawdź instalację
w PowerShell:

```powershell
python --version
```

## 2. Pobierz projekt

Pobierz repozytorium z GitHuba jako ZIP i rozpakuj je albo sklonuj poleceniem:

```powershell
git clone https://github.com/sylweklipka86-ui/Mechmate-.git
```

Otwórz PowerShell w folderze `Mechmate-\Code`, w którym znajduje się
`requirements.txt`.

## 3. Zainstaluj biblioteki

Uruchom:

```powershell
python -m pip install -r requirements.txt
```

Pakiety instalowane z `requirements.txt`:

- `opencv-python` — obraz z kamerki i przetwarzanie obrazu;
- `numpy` — obliczenia obrazu;
- `ultralytics` — uruchamianie modelu YOLO;
- `python-chess` — pozycja partii, legalne ruchy i komunikacja ze Stockfishem.

## 4. Zainstaluj Stockfisha

Pobierz Stockfish z [oficjalnej strony](https://stockfishchess.org/download/).
Skrypt automatycznie szuka go w folderze
`%LOCALAPPDATA%\Programs\Stockfish`. Jeśli zainstalujesz go gdzie indziej,
podaj ścieżkę do pliku `.exe` przez opcję `--stockfish`.

## 5. Skopiuj model figur

Wytrenowane wagi YOLO i zdjęcia treningowe nie są dołączone do repozytorium.
Utwórz folder `Code\models` i skopiuj do niego swój plik modelu pod nazwą
`best.pt`. Wagi są ignorowane przez Git, więc nie zostaną przypadkowo
opublikowane.

## 6. Uruchom program

W folderze `Code` uruchom `Uruchom szachy.bat` albo wpisz:

```powershell
python .\wykrywaj_ruchy.py --orientation black --model .\models\best.pt --engine-time 1.0
```

Kliknij cztery rogi pól szachownicy w kolejności: lewy górny, prawy górny,
prawy dolny, lewy dolny. Zatwierdź Enterem w oknie zaznaczania, ustaw pozycję
startową i naciśnij `i` w oknie kamerki. Białe zaczynają.

Stockfish podpowiada ruch czarnych, ale ramię nie jest jeszcze sterowane przez
program — czarny ruch trzeba wykonać ręcznie. Kamera powinna go wykryć.

## Inne skrypty

Podgląd i rozpoznawanie figur z kamerki:

```powershell
python ".\# Rozpoznawanie figur szachowych ze zdję.py" --camera --model .\models\best.pt --orientation black
```

Oznaczanie nowych zdjęć:

```powershell
python .\oznacz_szachy.py --images "C:\sciezka\do\zdjec" --only-new
```
