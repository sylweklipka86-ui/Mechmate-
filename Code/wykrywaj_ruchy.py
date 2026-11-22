import argparse
from collections import Counter, deque
from pathlib import Path
import shutil

import chess
import chess.engine
import cv2
import numpy as np
from ultralytics import YOLO



DOMYSLNY_MODEL = (
    Path(__file__).resolve().parent
    / "runs"
    / "chess-finetune-nov08-hand-photos"
    / "weights"
    / "best.pt"
)

ROZMIAR_OBRAZU_PLANSZY = 800
ROBOT_COLOR = chess.BLACK
STOCKFISH_FOLDER = (
    Path.home() / "AppData" / "Local" / "Programs" / "Stockfish"
)


def find_stockfish_executable(requested_path=None):
    if requested_path:
        executable = Path(requested_path).expanduser()
        if executable.is_file():
            return str(executable)
        raise SystemExit(f"Nie znaleziono Stockfisha: {executable}")

    installed = sorted(STOCKFISH_FOLDER.rglob("stockfish*.exe"))
    if installed:
        return str(installed[0])

    executable = shutil.which("stockfish")
    if executable:
        return executable

    raise SystemExit(
        "Nie znaleziono Stockfisha. Zainstaluj go albo uruchom skrypt "
        "z parametrem --stockfish sciezka\\do\\stockfish.exe."
    )


def get_stockfish_move(engine, board, think_time):
    result = engine.play(board, chess.engine.Limit(time=think_time))
    if result.move is None:
        return None
    return result.move, board.san(result.move)


def wybierz_narozniki(image):
    corners = []
    window = "Zaznacz cztery rogi szachownicy"

    def on_click(event, x, y, flags, parameter):
        if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
            corners.append((x, y))

    cv2.namedWindow(window)
    cv2.setMouseCallback(window, on_click)
    print("Kliknij rogi pol: lewy gorny, prawy gorny, prawy dolny, lewy dolny.")
    print("Enter zatwierdza, r czysci zaznaczenie, Esc anuluje.")

    while True:
        preview = image.copy()
        for index, point in enumerate(corners):
            cv2.circle(preview, point, 6, (0, 0, 255), -1)
            cv2.putText(
                preview,
                str(index + 1),
                (point[0] + 8, point[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
        if len(corners) > 1:
            cv2.polylines(
                preview,
                [np.array(corners, dtype=np.int32)],
                len(corners) == 4,
                (0, 180, 255),
                2,
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
    points = np.float32(corners)
    if not cv2.isContourConvex(points) or cv2.contourArea(points) < 100:
        raise SystemExit("Kliknij cztery rogi tak, aby obejmowaly cala szachownice.")
    return cv2.getPerspectiveTransform(
        points,
        np.float32([[0, 0], [8, 0], [8, 8], [0, 8]]),
    )


def pole_szachowe(x, y, transform, orientation):
    point = np.array([[[x, y]]], dtype=np.float32)
    column, row = cv2.perspectiveTransform(point, transform)[0][0]
    if not (0 <= column < 8 and 0 <= row < 8):
        return None

    file_index = int(column)
    rank_index = int(row)
    if orientation == "white":
        return chess.square_name(chess.square(file_index, 7 - rank_index))
    return chess.square_name(chess.square(7 - file_index, rank_index))


def wyprostuj_plansze(image, transform):
    scale = ROZMIAR_OBRAZU_PLANSZY / 8
    to_pixels = np.float32([
        [scale, 0, 0],
        [0, scale, 0],
        [0, 0, 1],
    ])
    image_transform = to_pixels @ transform
    return cv2.warpPerspective(
        image,
        image_transform,
        (ROZMIAR_OBRAZU_PLANSZY, ROZMIAR_OBRAZU_PLANSZY),
    )


def position_from_board(board):
    return {
        chess.square_name(square): piece.symbol()
        for square, piece in board.piece_map().items()
    }


def changed_squares(before, after):
    return {
        square
        for square in set(before) | set(after)
        if before.get(square) != after.get(square)
    }


def changed_image_squares(reference, current, orientation, include_scores=False):
    reference_gray = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
    current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    difference = (
        current_gray.astype(np.int16) - reference_gray.astype(np.int16)
    )
    brightness_shift = int(np.median(difference))
    difference = np.abs(difference - brightness_shift).astype(np.uint8)
    cell_size = ROZMIAR_OBRAZU_PLANSZY // 8
    margin = cell_size // 5
    square_differences = []

    grid_transform = np.float32([
        [8 / ROZMIAR_OBRAZU_PLANSZY, 0, 0],
        [0, 8 / ROZMIAR_OBRAZU_PLANSZY, 0],
        [0, 0, 1],
    ])
    for row in range(8):
        for column in range(8):
            x1 = column * cell_size + margin
            y1 = row * cell_size + margin
            x2 = (column + 1) * cell_size - margin
            y2 = (row + 1) * cell_size - margin
            patch = cv2.resize(
                difference[y1:y2, x1:x2], (24, 24),
                interpolation=cv2.INTER_AREA,
            )
            score = float(patch.mean())
            square = pole_szachowe(
                (column + 0.5) * cell_size,
                (row + 0.5) * cell_size,
                grid_transform,
                orientation,
            )
            square_differences.append((square, score))

    scores = [score for _, score in square_differences]
    noise = float(np.median(scores))
    mad = float(np.median(np.abs(np.array(scores) - noise)))
    threshold = max(10.0, noise + max(8.0, mad * 3.0))
    changed = {
        square for square, score in square_differences
        if score >= threshold
    }
    if include_scores:
        return changed, dict(square_differences)
    return changed


def stable_changed_squares(changes):
    votes = Counter(square for frame in changes for square in frame)
    required_votes = (len(changes) + 1) // 2
    return {
        square for square, count in votes.items()
        if count >= required_votes
    }


def format_move_history(moves):
    start = max(0, len(moves) - 8)
    if start % 2:
        start -= 1
    formatted = []
    for index in range(start, len(moves), 2):
        move_text = f"{index // 2 + 1}.{moves[index]}"
        if index + 1 < len(moves):
            move_text += f" {moves[index + 1]}"
        formatted.append(move_text)
    return " ".join(formatted)


def override_piece(board, square, piece_type=None, color=None):
    square_index = chess.parse_square(square)
    if piece_type is None:
        board.remove_piece_at(square_index)
    else:
        current_piece = board.piece_at(square_index)
        if color is None:
            color = current_piece.color if current_piece else board.turn
        board.set_piece_at(square_index, chess.Piece(piece_type, color))
    board.castling_rights = board.clean_castling_rights()


def readable_piece_name(class_name):
    parts = class_name.lower().replace("-", "_").split("_")
    colors = {"white": "bialy", "black": "czarny"}
    pieces = {
        "pawn": "pion",
        "knight": "skoczek",
        "bishop": "goniec",
        "rook": "wieza",
        "queen": "hetman",
        "king": "krol",
    }
    color = next((name for key, name in colors.items() if key in parts), None)
    piece = next((name for key, name in pieces.items() if key in parts), None)
    if color and piece:
        return f"{color} {piece}"
    return class_name


def find_move_from_changed_squares(
    board, observed_squares, square_scores=None,
):
    current_position = position_from_board(board)
    candidates = []
    for move in board.legal_moves:
        next_board = board.copy()
        san = board.san(move)
        next_board.push(move)
        expected_changes = changed_squares(
            current_position,
            position_from_board(next_board),
        )
        missing_changes = expected_changes - observed_squares
        extra_changes = observed_squares - expected_changes
        if (
            expected_changes
            and len(missing_changes) <= 1
            and len(extra_changes) <= 1
        ):
            missing_signal = sum(
                (square_scores or {}).get(square, 0.0)
                for square in missing_changes
            )
            extra_signal = sum(
                (square_scores or {}).get(square, 0.0)
                for square in extra_changes
            )
            candidates.append((
                len(missing_changes) + len(extra_changes),
                missing_signal - extra_signal,
                move,
                san,
            ))

    if not candidates:
        return None
    fewest_mismatches = min(candidate[0] for candidate in candidates)
    best = [
        candidate for candidate in candidates
        if candidate[0] == fewest_mismatches
    ]
    strongest_signal = max(candidate[1] for candidate in best)
    best = [
        candidate for candidate in best
        if strongest_signal - candidate[1] < 2.0
    ]
    return (best[0][2], best[0][3]) if len(best) == 1 else None


def draw_piece_detections(image, result, board, transform, orientation):
    names = {
        chess.PAWN: "pion",
        chess.KNIGHT: "skoczek",
        chess.BISHOP: "goniec",
        chess.ROOK: "wieza",
        chess.QUEEN: "hetman",
        chess.KING: "krol",
    }
    detections_by_square = {}

    for detection in result.boxes:
        x1, y1, x2, y2 = map(int, detection.xyxy[0].tolist())
        square = pole_szachowe(
            (x1 + x2) // 2, max(y1, y2 - 1), transform, orientation,
        )
        if square is None:
            continue

        confidence = float(detection.conf[0])
        if (
            square not in detections_by_square
            or confidence > detections_by_square[square][0]
        ):
            class_index = int(detection.cls[0])
            detections_by_square[square] = (
                confidence, (x1, y1, x2, y2), result.names[class_index],
            )

    for square, (confidence, box, detected_name) in detections_by_square.items():
        x1, y1, x2, y2 = box
        piece = board.piece_at(chess.parse_square(square))
        if piece is None:
            label = (
                f"{square}: model {readable_piece_name(detected_name)} "
                f"{confidence:.0%}"
            )
            color = (0, 165, 255)
        else:
            side = "bialy" if piece.color == chess.WHITE else "czarny"
            label = f"{square}: {side} {names[piece.piece_type]}"
            color = (0, 220, 0)

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            image, label, (x1, max(y1 - 7, 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2, cv2.LINE_AA,
        )
    return image


def draw_overlay(
    image, transform, orientation, status, changed=None, move_history=None,
    selected_square=None, correction_mode=False, robot_suggestion=None,
):
    inverse = np.linalg.inv(transform).astype(np.float32)

    def point_on_image(column, row):
        point = np.array([[[column, row]]], dtype=np.float32)
        result = cv2.perspectiveTransform(point, inverse)[0][0]
        return tuple(np.round(result).astype(int))

    overlay = image.copy()
    for square in changed or ():
        file_index = chess.square_file(chess.parse_square(square))
        rank_index = chess.square_rank(chess.parse_square(square))
        if orientation == "white":
            column, row = file_index, 7 - rank_index
        else:
            column, row = 7 - file_index, rank_index
        corners = np.array([
            point_on_image(column, row),
            point_on_image(column + 1, row),
            point_on_image(column + 1, row + 1),
            point_on_image(column, row + 1),
        ], dtype=np.int32)
        cv2.fillPoly(overlay, [corners], (0, 180, 0))
    cv2.addWeighted(overlay, 0.25, image, 0.75, 0, image)

    if selected_square is not None:
        file_index = chess.square_file(chess.parse_square(selected_square))
        rank_index = chess.square_rank(chess.parse_square(selected_square))
        if orientation == "white":
            column, row = file_index, 7 - rank_index
        else:
            column, row = 7 - file_index, rank_index
        corners = np.array([
            point_on_image(column, row),
            point_on_image(column + 1, row),
            point_on_image(column + 1, row + 1),
            point_on_image(column, row + 1),
        ], dtype=np.int32)
        cv2.polylines(image, [corners], True, (0, 255, 255), 3)

    overlay = image.copy()
    for index in range(9):
        cv2.line(
            overlay,
            point_on_image(index, 0),
            point_on_image(index, 8),
            (0, 180, 255),
            1,
        )
        cv2.line(
            overlay,
            point_on_image(0, index),
            point_on_image(8, index),
            (0, 180, 255),
            1,
        )
    cv2.addWeighted(overlay, 0.45, image, 0.55, 0, image)

    for row in range(8):
        for column in range(8):
            x, y = point_on_image(column + 0.08, row + 0.25)
            center_x, center_y = point_on_image(column + 0.5, row + 0.5)
            square = pole_szachowe(
                center_x, center_y, transform, orientation,
            )
            if square is None:
                continue
            cv2.putText(
                image, square, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (0, 0, 0), 3, cv2.LINE_AA,
            )
            cv2.putText(
                image, square, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.45, (255, 255, 255), 1, cv2.LINE_AA,
            )

    panel = np.full((132, image.shape[1], 3), 35, dtype=np.uint8)
    cv2.putText(
        panel, status, (10, 24), cv2.FONT_HERSHEY_SIMPLEX,
        0.52, (255, 255, 255), 1, cv2.LINE_AA,
    )
    moves_text = format_move_history(move_history or [])
    if moves_text:
        cv2.putText(
            panel, f"Ruchy: {moves_text}", (10, 46),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
        )
    if robot_suggestion:
        cv2.putText(
            panel, f"Robot (Stockfish): {robot_suggestion}", (10, 69),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 100), 1, cv2.LINE_AA,
        )
    if correction_mode:
        controls = "1/2=kolor p/n/b/r/q/k=figura x=puste Esc=koniec korekty"
        detail = "Kolor zachowuje pole; puste pole przyjmie kolor na ruchu."
    else:
        controls = "i=start   r=reset   u=cofnij   c=korekta   q=koniec"
        detail = "Wykonaj ruch Stockfisha na planszy; kamera sama wykryje ruch."
    cv2.putText(
        panel, controls, (10, 96), cv2.FONT_HERSHEY_SIMPLEX,
        0.38, (0, 255, 255), 1, cv2.LINE_AA,
    )
    cv2.putText(
        panel, detail, (10, 119), cv2.FONT_HERSHEY_SIMPLEX,
        0.38, (200, 200, 200), 1, cv2.LINE_AA,
    )
    return cv2.vconcat((image, panel))


def main():
    parser = argparse.ArgumentParser(
        description="Wykrywanie legalnych ruchow szachowych z kamerki"
    )
    parser.add_argument("--camera", type=int, default=0, help="Numer kamerki")
    parser.add_argument(
        "--model", default=str(DOMYSLNY_MODEL), help="Wytrenowany model YOLO",
    )
    parser.add_argument(
        "--orientation",
        choices=("white", "black"),
        default="white",
        help="Kolor gracza patrzacego na plansze od dolu obrazu (domyslnie white)",
    )
    parser.add_argument(
        "--stable-frames",
        type=int,
        default=5,
        help="Ile takich samych odczytow czekac przed sprawdzeniem ruchu",
    )
    parser.add_argument("--confidence", type=float, default=0.15)
    parser.add_argument(
        "--stockfish", help="Sciezka do pliku wykonywalnego Stockfish",
    )
    parser.add_argument(
        "--engine-time",
        type=float,
        default=1.0,
        help="Czas analizy Stockfisha na ruch w sekundach",
    )
    args = parser.parse_args()

    if args.stable_frames < 1:
        parser.error("--stable-frames musi wynosic co najmniej 1.")
    if args.engine_time <= 0:
        parser.error("--engine-time musi byc wiekszy od zera.")
    if not Path(args.model).is_file():
        raise SystemExit(f"Nie znaleziono modelu: {args.model}")

    model = YOLO(args.model)
    stockfish_path = find_stockfish_executable(args.stockfish)
    try:
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    except (OSError, chess.engine.EngineError) as error:
        raise SystemExit(f"Nie mozna uruchomic Stockfisha: {error}") from error
    print(f"Stockfish: {stockfish_path}")

    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        engine.quit()
        raise SystemExit(f"Nie mozna uruchomic kamerki nr {args.camera}.")
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    camera_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Rozdzielczosc kamerki: {camera_width}x{camera_height}")

    board = chess.Board()
    move_history = []
    robot_suggestion = None
    suggested_robot_move = None
    game_started = False
    last_attempted_changes = ()
    candidate_changes = None
    stable_count = 0
    status = "Ustaw pozycje startowa i nacisnij i. Ruchy wykrywam z obrazu."
    corners_set = False
    transform = None
    board_images = deque(maxlen=args.stable_frames)
    image_changes = deque(maxlen=args.stable_frames)
    reference_board = None
    stable_changes = set()
    correction_mode = False
    selected_square = None
    selected_color = None
    window_created = False
    frame_width = 0
    frame_height = 0

    def select_square(event, x, y, flags, parameter):
        nonlocal selected_square, selected_color, status
        if event == cv2.EVENT_LBUTTONDOWN and correction_mode:
            if not (0 <= x < frame_width and 0 <= y < frame_height):
                return
            selected_square = pole_szachowe(
                x, y, transform, args.orientation,
            )
            selected_color = None
            if selected_square is not None:
                status = (
                    f"Wybrano {selected_square}. Wybierz rodzaj figury."
                )

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise SystemExit("Nie udalo sie odczytac obrazu z kamerki.")
            frame_height, frame_width = frame.shape[:2]

            if not corners_set:
                transform = wybierz_narozniki(frame)
                corners_set = True

            if not window_created:
                cv2.namedWindow("Wykrywanie ruchow szachowych")
                cv2.setMouseCallback(
                    "Wykrywanie ruchow szachowych", select_square,
                )
                window_created = True

            result = next(iter(model.predict(
                frame,
                conf=args.confidence,
                agnostic_nms=True,
                verbose=False,
            )))
            board_image = wyprostuj_plansze(frame, transform)
            if not correction_mode:
                board_images.append(board_image)
            if correction_mode:
                stable_changes.clear()
                image_changes.clear()
                square_scores = None
            elif game_started and reference_board is not None:
                current_changes, square_scores = changed_image_squares(
                    reference_board, board_image, args.orientation,
                    include_scores=True,
                )
                image_changes.append(current_changes)
                stable_changes = stable_changed_squares(image_changes)
            elif game_started:
                square_scores = None
                stable_changes.clear()
                image_changes.clear()
                last_attempted_changes = ()
                if len(board_images) == args.stable_frames:
                    reference_board = np.median(
                        np.stack(board_images), axis=0,
                    ).astype(np.uint8)
                    status = "Obraz planszy zapisany. Czekam na ruch."
            else:
                square_scores = None
                stable_changes.clear()
                image_changes.clear()
                last_attempted_changes = ()

            signature = tuple(sorted(stable_changes))
            if signature == candidate_changes:
                stable_count += 1
            else:
                candidate_changes = signature
                stable_count = 1

            if game_started and stable_changes and (
                stable_count >= args.stable_frames
                and (
                    signature != last_attempted_changes
                    or stable_count % args.stable_frames == 0
                )
            ):
                found_move = find_move_from_changed_squares(
                    board, stable_changes, square_scores,
                )
                if found_move is None:
                    status = (
                        "Nie rozpoznano ruchu. Pola: "
                        f"{', '.join(sorted(stable_changes))}. "
                        "Odsun reke i poczekaj."
                    )
                    last_attempted_changes = signature
                else:
                    move, san = found_move
                    moving_color = board.turn
                    board.push(move)
                    move_history.append(san)
                    status = f"Wykryto ruch: {san} ({move.uci()})"
                    print(status)
                    if board.is_game_over():
                        robot_suggestion = None
                        suggested_robot_move = None
                        status += f" Wynik: {board.result()}."
                    elif moving_color == ROBOT_COLOR:
                        robot_suggestion = None
                        suggested_robot_move = None
                    elif board.turn == ROBOT_COLOR:
                        try:
                            suggestion = get_stockfish_move(
                                engine, board, args.engine_time,
                            )
                        except (chess.engine.EngineError, OSError) as error:
                            raise SystemExit(
                                f"Blad analizy Stockfisha: {error}"
                            ) from error
                        if suggestion is None:
                            robot_suggestion = None
                            suggested_robot_move = None
                            status = "Stockfish nie zwrocil ruchu."
                        else:
                            robot_move, robot_san = suggestion
                            suggested_robot_move = robot_move
                            robot_suggestion = (
                                f"{robot_san} ({robot_move.uci()})"
                            )
                            print(f"Robot (Stockfish): {robot_suggestion}")
                            status = (
                                f"Wykonaj ruch robota: {robot_suggestion}. "
                                "Kamera wykryje go automatycznie."
                            )
                    reference_board = np.median(
                        np.stack(board_images), axis=0,
                    ).astype(np.uint8)
                    image_changes.clear()
                    stable_changes.clear()
                    last_attempted_changes = ()
                    candidate_changes = None
                    stable_count = 0

            display = draw_piece_detections(
                frame.copy(), result, board, transform, args.orientation,
            )
            if correction_mode and selected_square is None:
                status = "Korekta: kliknij pole, potem wybierz rodzaj figury."
            draw_overlay(
                display, transform, args.orientation, status, stable_changes,
                move_history, selected_square, correction_mode,
                robot_suggestion,
            )
            cv2.imshow("Wykrywanie ruchow szachowych", display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("c") and game_started:
                correction_mode = not correction_mode
                selected_square = None
                selected_color = None
                image_changes.clear()
                stable_changes.clear()
                last_attempted_changes = ()
                candidate_changes = None
                stable_count = 0
                status = (
                    "Korekta wlaczona. Kliknij pole; wybierz rodzaj i kolor."
                    if correction_mode else "Korekta wylaczona."
                )
                continue
            if correction_mode:
                if key == 27:
                    correction_mode = False
                    selected_square = None
                    selected_color = None
                    image_changes.clear()
                    stable_changes.clear()
                    last_attempted_changes = ()
                    candidate_changes = None
                    stable_count = 0
                    status = "Korekta wylaczona."
                elif key in (ord("1"), ord("2")):
                    if selected_square is None:
                        status = "Najpierw kliknij pole."
                    else:
                        selected_color = key == ord("1")
                        side = "bialy" if selected_color else "czarny"
                        status = f"{selected_square}: wybrano kolor {side}."
                elif key == ord("x"):
                    if selected_square is None:
                        status = "Najpierw kliknij pole."
                    else:
                        override_piece(board, selected_square)
                        image_changes.clear()
                        stable_changes.clear()
                        last_attempted_changes = ()
                        candidate_changes = None
                        stable_count = 0
                        selected_color = None
                        robot_suggestion = None
                        suggested_robot_move = None
                        status = (
                            f"Usunieto figure z {selected_square}. "
                            "Kolej ruchu bez zmian; cofanie starszych ruchow niedostepne."
                        )
                        print(status)
                elif key in (
                    ord("p"), ord("n"), ord("b"), ord("r"), ord("q"), ord("k"),
                ):
                    if selected_square is None:
                        status = "Najpierw kliknij pole."
                    else:
                        piece_types = {
                            ord("p"): chess.PAWN,
                            ord("n"): chess.KNIGHT,
                            ord("b"): chess.BISHOP,
                            ord("r"): chess.ROOK,
                            ord("q"): chess.QUEEN,
                            ord("k"): chess.KING,
                        }
                        override_piece(
                            board, selected_square, piece_types[key],
                            selected_color,
                        )
                        image_changes.clear()
                        stable_changes.clear()
                        last_attempted_changes = ()
                        candidate_changes = None
                        stable_count = 0
                        selected_color = None
                        robot_suggestion = None
                        suggested_robot_move = None
                        status = (
                            f"Zmieniono figure na {selected_square}. "
                            "Kolej ruchu bez zmian; cofanie starszych ruchow niedostepne."
                        )
                        print(status)
                continue
            if key == ord("q"):
                break
            if key == ord("i") and not game_started:
                board.reset()
                move_history.clear()
                robot_suggestion = None
                suggested_robot_move = None
                reference_board = np.median(
                    np.stack(board_images), axis=0,
                ).astype(np.uint8)
                image_changes.clear()
                stable_changes.clear()
                last_attempted_changes = ()
                candidate_changes = None
                stable_count = 0
                game_started = True
                status = "Start! Biale zaczynaja. Cofnij reke po ruchu."
                print("Start. Zapisano obraz planszy; czekam na ruch bialych.")
            if key == ord("r"):
                board.reset()
                move_history.clear()
                robot_suggestion = None
                suggested_robot_move = None
                reference_board = np.median(
                    np.stack(board_images), axis=0,
                ).astype(np.uint8)
                image_changes.clear()
                stable_changes.clear()
                last_attempted_changes = ()
                candidate_changes = None
                stable_count = 0
                game_started = True
                status = "Zresetowano do pozycji startowej."
                print("Zresetowano gre do standardowej pozycji.")
            if key == ord("u") and game_started:
                if board.move_stack:
                    undone_move = board.pop()
                    move_history.pop()
                    robot_suggestion = None
                    suggested_robot_move = None
                    reference_board = None
                    board_images.clear()
                    image_changes.clear()
                    stable_changes.clear()
                    last_attempted_changes = ()
                    candidate_changes = None
                    stable_count = 0
                    status = (
                        f"Cofnieto ruch {undone_move.uci()}. "
                        "Ustaw pozycje i poczekaj na zapis obrazu."
                    )
                    print(status)
                else:
                    status = "Nie ma ruchu do cofniecia."
    finally:
        camera.release()
        engine.quit()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
