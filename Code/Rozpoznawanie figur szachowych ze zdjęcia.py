# Rozpoznawanie figur szachowych ze zdjęcia
# Instalacja: pip install ultralytics opencv-python
# Użycie ze zdjęcia: python chess_detect.py plansza.jpg --model chess.pt
# Użycie z kamerką: python chess_detect.py --camera --model chess.pt
# `chess.pt` musi być modelem YOLO wytrenowanym do rozpoznawania figur.
# Bez --board kliknij cztery rogi pól planszy, by dopasować perspektywę.

import argparse
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def nazwa_figury(class_name):
    """Zamień nazwę klasy modelu na krótką polską nazwę figury."""
    name = class_name.lower().replace("_", " ").replace("-", " ")
    names = {
        "pawn": "pion",
        "rook": "wieża",
        "knight": "skoczek",
        "bishop": "goniec",
        "queen": "hetman",
        "king": "król",
        "pion": "pion",
        "wieza": "wieża",
        "skoczek": "skoczek",
        "goniec": "goniec",
        "hetman": "hetman",
        "krol": "król",
    }
    for word in name.split():
        if word in names:
            return names[word]
    return name


def kolor_figury(class_name, image, x1, y1, x2, y2):
    """Odczytaj kolor z nazwy klasy, a w razie jego braku oszacuj z obrazu."""
    name = class_name.lower()
    if any(word in name for word in ("white", "bial", "bia")):
        return "biały"
    if any(word in name for word in ("black", "czarn")):
        return "czarny"

    crop = image[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
    if crop.size == 0:
        return "nieznany kolor"
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return "biała" if gray.mean() >= 128 else "czarna"


def pole_szachowe(x, y, transform, orientation):
    """Wylicz pole po przeliczeniu obrazu na współrzędne planszy."""
    point = np.array([[[x, y]]], dtype=np.float32)
    column, row = cv2.perspectiveTransform(point, transform)[0][0]
    if not (0 <= column < 8 and 0 <= row < 8):
        return None

    column = int(column)
    row = int(row)
    files = "abcdefgh"

    if orientation == "white":
        return f"{files[column]}{8 - row}"
    return f"{files[7 - column]}{row + 1}"


def macierz_planszy(corners):
    """Oblicz przeliczenie z obrazu do siatki 8 na 8."""
    points = np.float32(corners)
    if not cv2.isContourConvex(points) or cv2.contourArea(points) < 100:
        raise SystemExit("Cztery rogi muszą tworzyć poprawny obrys planszy.")

    grid = np.float32([[0, 0], [8, 0], [8, 8], [0, 8]])
    return cv2.getPerspectiveTransform(points, grid)


def punkt_na_obrazie(column, row, inverse_transform):
    point = np.array([[[column, row]]], dtype=np.float32)
    result = cv2.perspectiveTransform(point, inverse_transform)[0][0]
    return tuple(np.round(result).astype(int))


def narysuj_pola(image, transform, orientation):
    """Narysuj perspektywiczną siatkę i nazwy pól."""
    inverse_transform = np.linalg.inv(transform).astype(np.float32)
    overlay = image.copy()
    for i in range(9):
        cv2.line(
            overlay,
            punkt_na_obrazie(i, 0, inverse_transform),
            punkt_na_obrazie(i, 8, inverse_transform),
            (0, 180, 255), 1,
        )
        cv2.line(
            overlay,
            punkt_na_obrazie(0, i, inverse_transform),
            punkt_na_obrazie(8, i, inverse_transform),
            (0, 180, 255), 1,
        )
    cv2.addWeighted(overlay, 0.45, image, 0.55, 0, image)

    for row in range(8):
        for column in range(8):
            x, y = punkt_na_obrazie(
                column + 0.08, row + 0.25, inverse_transform,
            )
            center = punkt_na_obrazie(
                column + 0.5, row + 0.5, inverse_transform,
            )
            square = pole_szachowe(*center, transform, orientation)
            cv2.putText(
                image, square, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (0, 0, 0), 3, cv2.LINE_AA,
            )
            cv2.putText(
                image, square, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (255, 255, 255), 1, cv2.LINE_AA,
            )


def wybierz_narozniki(image):
    """Kliknij cztery rogi planszy: lewy górny, zgodnie z ruchem wskazówek."""
    corners = []
    window = "Zaznacz cztery rogi szachownicy"

    def on_click(event, x, y, flags, parameter):
        if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
            corners.append((x, y))

    cv2.namedWindow(window)
    cv2.setMouseCallback(window, on_click)
    print("Kliknij rogi pól: lewy górny, prawy górny, prawy dolny, lewy dolny.")
    print("Enter zatwierdza, r czyści zaznaczenie, Esc anuluje.")

    while True:
        preview = image.copy()
        for index, point in enumerate(corners):
            cv2.circle(preview, point, 6, (0, 0, 255), -1)
            cv2.putText(
                preview, str(index + 1), (point[0] + 8, point[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
            )
        if len(corners) > 1:
            cv2.polylines(
                preview, [np.array(corners, dtype=np.int32)],
                len(corners) == 4, (0, 180, 255), 2,
            )
        cv2.imshow(window, preview)
        key = cv2.waitKey(20) & 0xFF
        if key in (10, 13) and len(corners) == 4:
            break
        if key == ord("r"):
            corners.clear()
        if key == 27:
            cv2.destroyWindow(window)
            raise SystemExit("Anulowano zaznaczanie szachownicy.")

    cv2.destroyWindow(window)
    macierz_planszy(corners)
    return corners


def narożniki_z_prostokata(board):
    x1, y1, x2, y2 = board
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]


def oznacz_figury(image, source_image, result, model, transform, orientation, show_console=True):
    for detection in result.boxes:
        x1, y1, x2, y2 = map(int, detection.xyxy[0].tolist())
        name = str(model.names[int(detection.cls[0])])
        score = float(detection.conf[0])
        color = kolor_figury(name, source_image, x1, y1, x2, y2)
        piece = nazwa_figury(name)
        square = pole_szachowe(
            (x1 + x2) // 2, max(y1, y2 - 1), transform, orientation,
        )
        square_label = square or "poza planszą"
        label = f"{color} {piece} {square_label} {score:.0%}"

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 200, 0), 2)
        cv2.putText(
            image, label, (x1, max(y1 - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 0), 2,
        )
        if show_console:
            print(label)
    return image


def main():
    parser = argparse.ArgumentParser(description="Rozpoznawanie figur szachowych")
    parser.add_argument("image", nargs="?", help="Zdjęcie planszy")
    parser.add_argument(
        "--camera",
        nargs="?",
        const=0,
        type=int,
        metavar="NUMER",
        help="Podgląd z kamerki (domyślnie kamerka nr 0)",
    )
    parser.add_argument("--model", default="chess.pt", help="Wytrenowany model YOLO")
    parser.add_argument("--output", default="wynik.jpg", help="Ścieżka obrazu wynikowego")
    parser.add_argument("--confidence", type=float, default=0.35)
    parser.add_argument(
        "--board",
        nargs=4,
        type=int,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Prostokątny obszar planszy; bez tej opcji wskażesz cztery rogi",
    )
    parser.add_argument(
        "--orientation",
        choices=("white", "black"),
        default="white",
        help="Kolor gracza stojącego u dołu zdjęcia",
    )
    args = parser.parse_args()

    if args.image is None and args.camera is None:
        parser.error("Podaj zdjęcie albo użyj opcji --camera.")
    if args.image is not None and args.camera is not None:
        parser.error("Wybierz zdjęcie albo --camera, nie oba naraz.")
    if not Path(args.model).is_file():
        raise SystemExit(
            f"Brak pliku modelu: {args.model}. Potrzebny jest model YOLO "
            "wytrenowany na figurach szachowych; model ogólny ich nie rozpoznaje."
        )

    model = YOLO(args.model)

    if args.camera is not None:
        camera = cv2.VideoCapture(args.camera)
        if not camera.isOpened():
            raise SystemExit(f"Nie można uruchomić kamerki nr {args.camera}.")

        corners = narożniki_z_prostokata(args.board) if args.board else None
        print("Podgląd działa. Naciśnij q, aby zakończyć, albo s, aby zapisać klatkę.")
        while True:
            ok, frame = camera.read()
            if not ok:
                camera.release()
                cv2.destroyAllWindows()
                raise SystemExit("Nie udało się odczytać obrazu z kamerki.")

            height, width = frame.shape[:2]
            if corners is None:
                corners = wybierz_narozniki(frame)
            if any(x < 0 or y < 0 or x > width or y > height for x, y in corners):
                camera.release()
                cv2.destroyAllWindows()
                raise SystemExit("Rogi planszy muszą znajdować się w obrazie z kamerki.")

            transform = macierz_planszy(corners)
            original = frame.copy()
            narysuj_pola(frame, transform, args.orientation)
            result = model.predict(original, conf=args.confidence, verbose=False)[0]
            oznacz_figury(
                frame, original, result, model, transform, args.orientation,
                show_console=False,
            )
            cv2.imshow("Rozpoznawanie szachownicy", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                if not cv2.imwrite(args.output, frame):
                    camera.release()
                    cv2.destroyAllWindows()
                    raise SystemExit(f"Nie udało się zapisać wyniku: {args.output}")
                print(f"Zapisano: {args.output}")

        camera.release()
        cv2.destroyAllWindows()
        return

    image = cv2.imread(args.image)
    if image is None:
        raise SystemExit(f"Nie można otworzyć zdjęcia: {args.image}")

    height, width = image.shape[:2]
    corners = (
        narożniki_z_prostokata(args.board)
        if args.board else wybierz_narozniki(image)
    )
    if any(x < 0 or y < 0 or x > width or y > height for x, y in corners):
        raise SystemExit("Rogi planszy muszą znajdować się w zdjęciu.")

    transform = macierz_planszy(corners)
    original = image.copy()
    narysuj_pola(image, transform, args.orientation)
    result = model.predict(original, conf=args.confidence, verbose=False)[0]
    oznacz_figury(image, original, result, model, transform, args.orientation)
    if not cv2.imwrite(args.output, image):
        raise SystemExit(f"Nie udało się zapisać wyniku: {args.output}")
    print(f"Zapisano: {args.output}")
    cv2.imshow("Rozpoznawanie szachownicy", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
