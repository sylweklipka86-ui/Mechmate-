import argparse
import random
import shutil
from pathlib import Path

import cv2
import numpy as np


KLASY = [
    "white_pawn",
    "white_knight",
    "white_bishop",
    "white_rook",
    "white_queen",
    "white_king",
    "black_pawn",
    "black_knight",
    "black_bishop",
    "black_rook",
    "black_queen",
    "black_king",
]

NAZWY = [
    "Bialy pion",
    "Bialy skoczek",
    "Bialy goniec",
    "Biala wieza",
    "Bialy hetman",
    "Bialy krol",
    "Czarny pion",
    "Czarny skoczek",
    "Czarny goniec",
    "Czarna wieza",
    "Czarny hetman",
    "Czarny krol",
]


class Oznaczanie:
    def __init__(self, images, output):
        self.images = images
        self.output = output
        self.current = 0
        self.active_class = None
        self.start = None
        self.end = None
        self.dragging = False
        self.annotations = []
        self.window = "Oznaczanie figur szachowych"

        split_file = output / "splits.txt"
        saved_splits = {}
        if split_file.exists():
            for line in split_file.read_text(encoding="utf-8").splitlines():
                values = line.rsplit(maxsplit=1)
                if len(values) == 2 and values[1] in {"train", "val"}:
                    saved_splits[values[0]] = values[1]

        self.splits = {
            image: saved_splits[image.name]
            for image in images
            if image.name in saved_splits
        }
        new_images = [image for image in images if image not in self.splits]
        random.Random(42).shuffle(new_images)
        all_names = set(saved_splits) | {image.name for image in images}
        desired_val_count = (
            max(1, int(len(all_names) * 0.2 + 0.5))
            if len(all_names) > 1 else 0
        )
        val_count = sum(split == "val" for split in saved_splits.values())
        for image in new_images:
            split = "val" if val_count < desired_val_count else "train"
            self.splits[image] = split
            if split == "val":
                val_count += 1

        output.mkdir(parents=True, exist_ok=True)
        saved_splits.update({
            image.name: self.splits[image]
            for image in images
        })
        split_lines = [
            f"{name} {split}"
            for name, split in sorted(saved_splits.items())
        ]
        split_file.write_text("\n".join(split_lines) + "\n", encoding="utf-8")

    def label_path(self, image_path):
        split = self.splits[image_path]
        return self.output / "labels" / split / f"{image_path.stem}.txt"

    def image_path(self, image_path):
        split = self.splits[image_path]
        return self.output / "images" / split / image_path.name

    def load_annotations(self):
        self.annotations = []
        path = self.label_path(self.images[self.current])
        if not path.exists():
            return

        for line in path.read_text(encoding="utf-8").splitlines():
            values = line.split()
            if len(values) != 5:
                continue
            class_id, x, y, width, height = values
            self.annotations.append(
                (int(class_id), float(x), float(y), float(width), float(height))
            )

    def save_annotations(self):
        image_path = self.images[self.current]
        image = cv2.imread(str(image_path))
        if image is None:
            raise SystemExit(f"Nie można otworzyć zdjęcia: {image_path}")

        label_path = self.label_path(image_path)
        label_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"{class_id} {x:.6f} {y:.6f} {box_width:.6f} {box_height:.6f}"
            for class_id, x, y, box_width, box_height in self.annotations
        ]
        label_path.write_text("\n".join(lines), encoding="utf-8")

        target_image = self.image_path(image_path)
        target_image.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path, target_image)
        self.write_data_file()

    def write_data_file(self):
        data_file = self.output / "data.yaml"
        root = str(self.output.resolve()).replace("\\", "/")
        lines = [f"path: '{root}'", "train: images/train", "val: images/val", "names:"]
        lines.extend(f"  {index}: {name}" for index, name in enumerate(KLASY))
        data_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def add_box(self):
        if self.active_class is None:
            return
        image = cv2.imread(str(self.images[self.current]))
        if image is None:
            return
        height, width = image.shape[:2]
        scale = min(1100 / width, 720 / height, 1)
        x1, y1 = self.start
        x2, y2 = self.end
        left, right = sorted((x1, x2))
        top, bottom = sorted((y1, y2))
        if right - left < 4 or bottom - top < 4:
            return

        left, right = left / scale, right / scale
        top, bottom = top / scale, bottom / scale
        center_x = (left + right) / 2 / width
        center_y = (top + bottom) / 2 / height
        box_width = (right - left) / width
        box_height = (bottom - top) / height
        self.annotations.append(
            (self.active_class, center_x, center_y, box_width, box_height)
        )

    def on_mouse(self, event, x, y, flags, parameter):
        image = cv2.imread(str(self.images[self.current]))
        if image is None:
            return
        height, width = image.shape[:2]
        scale = min(1100 / width, 720 / height, 1)
        shown_width = int(width * scale)

        if x >= shown_width:
            if event == cv2.EVENT_LBUTTONDOWN:
                row = y // 45
                if 0 <= row < len(KLASY):
                    self.active_class = row
            return

        point = (min(x, shown_width), y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = point
            self.end = point
            self.dragging = True
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.end = point
        elif event == cv2.EVENT_LBUTTONUP and self.dragging:
            self.end = point
            self.dragging = False
            self.add_box()

    def draw(self):
        image_path = self.images[self.current]
        image = cv2.imread(str(image_path))
        if image is None:
            raise SystemExit(f"Nie można otworzyć zdjęcia: {image_path}")
        height, width = image.shape[:2]
        scale = min(1100 / width, 720 / height, 1)
        shown_width = int(width * scale)
        shown_height = int(height * scale)
        shown = cv2.resize(image, (shown_width, shown_height))

        for class_id, x, y, box_width, box_height in self.annotations:
            left = int((x - box_width / 2) * width * scale)
            top = int((y - box_height / 2) * height * scale)
            right = int((x + box_width / 2) * width * scale)
            bottom = int((y + box_height / 2) * height * scale)
            cv2.rectangle(shown, (left, top), (right, bottom), (0, 220, 0), 2)
            cv2.putText(
                shown, NAZWY[class_id], (left, max(18, top - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 0), 2,
            )

        if self.dragging and self.start and self.end:
            cv2.rectangle(shown, self.start, self.end, (255, 0, 0), 2)

        panel = np.full((shown_height, 270, 3), 35, dtype=np.uint8)
        for index, name in enumerate(NAZWY):
            y = index * 45
            color = (0, 180, 0) if index == self.active_class else (220, 220, 220)
            cv2.putText(
                panel, f"{index + 1}. {name}", (10, y + 29),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1,
            )
        canvas = np.zeros((shown_height, shown_width + 270, 3), dtype=np.uint8)
        canvas[:, :shown_width] = shown
        canvas[:, shown_width:] = panel
        cv2.putText(
            canvas, f"{self.current + 1}/{len(self.images)}: {image_path.name}",
            (10, shown_height - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (0, 255, 255), 2,
        )
        cv2.putText(
            canvas, "Kliknij klase, zaznacz figure. u=cofnij s=dalej p=wstecz q=koniec",
            (10, shown_height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.48,
            (0, 255, 255), 1,
        )
        cv2.putText(
            canvas, "Zaznaczaj tylko figury, nie pola ani calej planszy.",
            (10, shown_height - 62), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (0, 255, 255), 1,
        )
        cv2.imshow(self.window, canvas)

    def run(self):
        cv2.namedWindow(self.window)
        cv2.setMouseCallback(self.window, self.on_mouse)
        self.load_annotations()

        while True:
            self.draw()
            key = cv2.waitKey(30) & 0xFF
            if key == ord("u"):
                if self.annotations:
                    self.annotations.pop()
            elif key == ord("s"):
                self.save_annotations()
                if self.current == len(self.images) - 1:
                    break
                self.current += 1
                self.load_annotations()
            elif key == ord("p"):
                self.save_annotations()
                self.current = max(0, self.current - 1)
                self.load_annotations()
            elif key == ord("q") or key == 27:
                self.save_annotations()
                break

        cv2.destroyAllWindows()
        print(f"Zapisano dataset w: {self.output}")
        print("Sprawdz zdjecia i etykiety, zanim zaczniesz trening.")


def main():
    parser = argparse.ArgumentParser(
        description="Lokalne oznaczanie figur do treningu YOLO"
    )
    parser.add_argument(
        "--images",
        default=str(Path.home() / "Pictures" / "Camera Roll"),
        help="Folder ze zdjęciami",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parent / "chess_dataset"),
        help="Folder, w którym zapisze się dataset",
    )
    parser.add_argument(
        "--only-new",
        action="store_true",
        help="Oznaczaj tylko zdjęcia, których jeszcze nie ma w datasecie",
    )
    args = parser.parse_args()

    image_folder = Path(args.images)
    if not image_folder.is_dir():
        raise SystemExit(f"Nie znaleziono folderu ze zdjęciami: {image_folder}")
    images = sorted(
        path for path in image_folder.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
    )
    output_folder = Path(args.output)
    if args.only_new:
        known_images = set()
        for split in ("train", "val"):
            split_folder = output_folder / "images" / split
            if split_folder.exists():
                known_images.update(
                    path.name for path in split_folder.iterdir() if path.is_file()
                )
        images = [path for path in images if path.name not in known_images]
    if not images:
        if args.only_new:
            raise SystemExit(f"Nie znaleziono nowych zdjęć w folderze: {image_folder}")
        raise SystemExit(f"Nie znaleziono zdjęć w folderze: {image_folder}")

    Oznaczanie(images, output_folder).run()


if __name__ == "__main__":
    main()
