
import cv2
import mediapipe as mp
import os
import time
import urllib.request
import threading
import sys

DISPLAY_WIDTH = 720
DISPLAY_HEIGHT = 405

CAMERA_INDEX = 0

WINDOW_NAME = "RETROLENS - Peace Sign Blur"

MODEL_FILENAME = "hand_landmarker.task"

# Official MediaPipe Hand Landmarker model
MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/"
    "hand_landmarker/"
    "hand_landmarker/"
    "float16/"
    "1/"
    "hand_landmarker.task"
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    MODEL_FILENAME
)


# ============================================================
# DOWNLOAD / VALIDATE MODEL
# ============================================================

def download_model():

    print()
    print("=" * 60)
    print("MEDIAPIPE MODEL CHECK")
    print("=" * 60)

    need_download = False

    if not os.path.isfile(MODEL_PATH):

        print(
            "[INFO] Model belum ditemukan."
        )

        need_download = True

    else:

        file_size = os.path.getsize(
            MODEL_PATH
        )

        print(
            f"[INFO] Model ditemukan: {MODEL_PATH}"
        )

        print(
            f"[INFO] Ukuran model: "
            f"{file_size:,} bytes"
        )

        # File task yang valid harus jauh lebih besar
        # daripada HTML/error response palsu.
        if file_size < 100_000:

            print(
                "[WARNING] Ukuran model terlalu kecil."
            )

            need_download = True


    if need_download:

        temp_path = MODEL_PATH + ".download"

        print(
            "[INFO] Mengunduh model resmi MediaPipe..."
        )

        try:

            if os.path.exists(temp_path):
                os.remove(temp_path)

            request = urllib.request.Request(
                MODEL_URL,
                headers={
                    "User-Agent":
                    "Mozilla/5.0"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                data = response.read()

            if len(data) < 100_000:

                raise RuntimeError(
                    "File model yang diterima terlalu kecil."
                )

            with open(
                temp_path,
                "wb"
            ) as f:

                f.write(data)

            os.replace(
                temp_path,
                MODEL_PATH
            )

            print(
                "[OK] Model berhasil diunduh."
            )

        except Exception as e:

            if os.path.exists(temp_path):

                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            raise RuntimeError(
                "\n[ERROR] Gagal mengunduh model.\n"
                f"Detail: {e}\n\n"
                "Pastikan koneksi internet tersedia."
            )


    final_size = os.path.getsize(
        MODEL_PATH
    )

    if final_size < 100_000:

        raise RuntimeError(
            "[ERROR] hand_landmarker.task "
            "tidak valid atau rusak."
        )

    print(
        f"[OK] Model siap: "
        f"{MODEL_PATH}"
    )

    print(
        f"[OK] Ukuran: "
        f"{final_size:,} bytes"
    )

    print("=" * 60)


download_model()


# ============================================================
# MEDIAPIPE IMPORT
# ============================================================

print(
    f"[INFO] MediaPipe version: "
    f"{mp.__version__}"
)


BaseOptions = mp.tasks.BaseOptions

HandLandmarker = (
    mp.tasks.vision.HandLandmarker
)

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)

RunningMode = (
    mp.tasks.vision.RunningMode
)


# ============================================================
# RESULT STATE
# ============================================================

result_lock = threading.Lock()

latest_result = None

latest_timestamp = -1


def result_callback(
    result,
    output_image,
    timestamp_ms
):

    global latest_result
    global latest_timestamp

    with result_lock:

        latest_result = result
        latest_timestamp = timestamp_ms


# ============================================================
# MEDIAPIPE OPTIONS
# ============================================================

options = HandLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=RunningMode.LIVE_STREAM,

    num_hands=2,

    min_hand_detection_confidence=0.5,

    min_hand_presence_confidence=0.5,

    min_tracking_confidence=0.5,

    result_callback=result_callback
)


# ============================================================
# GESTURE HELPERS
# ============================================================

def is_finger_up(
    landmarks,
    tip_id,
    pip_id
):

    return (
        landmarks[tip_id].y
        <
        landmarks[pip_id].y
    )


def is_finger_down(
    landmarks,
    tip_id,
    pip_id
):

    return (
        landmarks[tip_id].y
        >
        landmarks[pip_id].y
    )


def is_peace_sign(
    hand_landmarks
):

    index_up = is_finger_up(
        hand_landmarks,
        8,
        6
    )

    middle_up = is_finger_up(
        hand_landmarks,
        12,
        10
    )

    ring_down = is_finger_down(
        hand_landmarks,
        16,
        14
    )

    pinky_down = is_finger_down(
        hand_landmarks,
        20,
        18
    )

    return (
        index_up
        and middle_up
        and ring_down
        and pinky_down
    )


# ============================================================
# PEACE STABILIZER
# ============================================================

peace_frames = 0

normal_frames = 0

PEACE_REQUIRED_FRAMES = 3

NORMAL_REQUIRED_FRAMES = 3

peace_active = False


# ============================================================
# CAMERA
# ============================================================

def open_camera():

    print()
    print("=" * 60)
    print("CAMERA CHECK")
    print("=" * 60)

    # Coba beberapa backend Windows
    candidates = [

        (
            CAMERA_INDEX,
            cv2.CAP_DSHOW,
            "DirectShow"
        ),

        (
            CAMERA_INDEX,
            cv2.CAP_MSMF,
            "Media Foundation"
        ),

        (
            CAMERA_INDEX,
            cv2.CAP_ANY,
            "Auto"
        ),
    ]

    for (
        index,
        backend,
        backend_name
    ) in candidates:

        print(
            f"[INFO] Mencoba camera "
            f"{index} / {backend_name}"
        )

        camera = cv2.VideoCapture(
            index,
            backend
        )

        if not camera.isOpened():

            camera.release()
            continue


        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            DISPLAY_WIDTH
        )

        camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            DISPLAY_HEIGHT
        )


        # Test frame

        for _ in range(10):

            ret, frame = (
                camera.read()
            )

            if (
                ret
                and frame is not None
                and frame.size > 0
            ):

                width = int(
                    camera.get(
                        cv2.CAP_PROP_FRAME_WIDTH
                    )
                )

                height = int(
                    camera.get(
                        cv2.CAP_PROP_FRAME_HEIGHT
                    )
                )

                print(
                    f"[OK] Kamera berhasil!"
                )

                print(
                    f"[OK] Backend : "
                    f"{backend_name}"
                )

                print(
                    f"[OK] Resolusi: "
                    f"{width}x{height}"
                )

                print("=" * 60)

                return camera

            time.sleep(0.05)


        camera.release()


    return None


cap = open_camera()


if cap is None:

    raise RuntimeError(
        "\n[ERROR] Webcam tidak bisa dibuka.\n\n"
        "Periksa:\n"
        "1. Windows Camera Permission\n"
        "2. Aplikasi Camera/Zoom/Meet yang sedang menggunakan webcam\n"
        "3. CAMERA_INDEX = 0 / 1"
    )


# ============================================================
# WINDOW
# ============================================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_AUTOSIZE
)


print()
print("=" * 55)
print(
    "        RETROLENS - PEACE SIGN BLUR"
)
print("=" * 55)
print(
    "✌️  Peace Sign  → Blur"
)
print(
    "🤚 Normal      → Normal"
)
print(
    "Q             → Quit"
)
print("=" * 55)


# ============================================================
# MAIN PROGRAM
# ============================================================

try:

    with HandLandmarker.create_from_options(
        options
    ) as landmarker:

        frame_counter = 0

        while True:

            # ------------------------------------------------
            # READ CAMERA
            # ------------------------------------------------

            ret, frame = cap.read()

            if not ret or frame is None:

                print(
                    "[ERROR] Frame webcam gagal."
                )

                time.sleep(0.05)

                continue


            # ------------------------------------------------
            # MIRROR
            # ------------------------------------------------

            frame = cv2.flip(
                frame,
                1
            )


            # ------------------------------------------------
            # RESIZE
            # ------------------------------------------------

            frame = cv2.resize(
                frame,
                (
                    DISPLAY_WIDTH,
                    DISPLAY_HEIGHT
                ),
                interpolation=cv2.INTER_AREA
            )


            # ------------------------------------------------
            # BGR → RGB
            # ------------------------------------------------

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )


            # ------------------------------------------------
            # MEDIAPIPE IMAGE
            # ------------------------------------------------

            mp_image = mp.Image(
                image_format=(
                    mp.ImageFormat.SRGB
                ),
                data=rgb_frame
            )


            # ------------------------------------------------
            # MONOTONIC TIMESTAMP
            # ------------------------------------------------

            timestamp_ms = (
                time.monotonic_ns()
                // 1_000_000
            )

            # Safety:
            # timestamp harus selalu meningkat

            if timestamp_ms <= latest_timestamp:

                timestamp_ms = (
                    latest_timestamp + 1
                )


            # ------------------------------------------------
            # DETECTION
            # ------------------------------------------------

            landmarker.detect_async(
                mp_image,
                timestamp_ms
            )


            # ------------------------------------------------
            # COPY RESULT SAFELY
            # ------------------------------------------------

            with result_lock:

                result = latest_result


            # ------------------------------------------------
            # PEACE DETECTION
            # ------------------------------------------------

            detected_peace = False


            if (
                result is not None
                and result.hand_landmarks
            ):

                for hand_landmarks in (
                    result.hand_landmarks
                ):

                    if is_peace_sign(
                        hand_landmarks
                    ):

                        detected_peace = True

                        break


            # ------------------------------------------------
            # STABILIZE
            # ------------------------------------------------

            if detected_peace:

                peace_frames += 1
                normal_frames = 0

                if (
                    peace_frames
                    >= PEACE_REQUIRED_FRAMES
                ):

                    peace_active = True

            else:

                normal_frames += 1
                peace_frames = 0

                if (
                    normal_frames
                    >= NORMAL_REQUIRED_FRAMES
                ):

                    peace_active = False


            # ------------------------------------------------
            # EFFECT
            # ------------------------------------------------

            if peace_active:

                blurred = cv2.GaussianBlur(
                    frame,
                    (
                        35,
                        35
                    ),
                    10
                )

                frame = blurred


                cv2.putText(
                    frame,
                    "PEACE SIGN DETECTED",
                    (
                        20,
                        40
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (
                        0,
                        255,
                        0
                    ),
                    2,
                    cv2.LINE_AA
                )

            else:

                cv2.putText(
                    frame,
                    "NORMAL",
                    (
                        20,
                        40
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (
                        255,
                        255,
                        255
                    ),
                    2,
                    cv2.LINE_AA
                )


            cv2.putText(
                frame,
                "Q = QUIT",
                (
                    20,
                    DISPLAY_HEIGHT - 15
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (
                    255,
                    255,
                    255
                ),
                1,
                cv2.LINE_AA
            )

            cv2.imshow(
                WINDOW_NAME,
                frame
            )


            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):

                break


            frame_counter += 1


finally:

    try:

        cap.release()

    except Exception:

        pass


    try:

        cv2.destroyAllWindows()

    except Exception:

        pass


    print(
        "[INFO] Program selesai."
    )

