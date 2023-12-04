import worldvision as wv
import cv2
from ultralytics import YOLO
import time

# ultralytics
model = YOLO('yolov8n.pt')
class_names = model.names

cap = cv2.VideoCapture("highway.webm")
video_fps = cap.get(cv2.CAP_PROP_FPS)
frame_width, frame_height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
cursor_location = (0, 0)

camera = wv.Camera(
    altitude=5,
    pitch=8,
    h_fov=90,
    v_fov=60,
    frame_dimensions=(frame_width, frame_height)
)

def mouse_callback_function(event, x, y, flags, params):
    global cursor_location
    cursor_location = (x, y)

cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_callback_function)
while True:
    start_time = time.time()
    ret, frame = cap.read()
    if not ret:
        break
    cv2.circle(frame, cursor_location, 5, (0, 0, 255), -1)
    three_d_coords = wv.get_3d_coords(camera, cursor_location, 10)
    two_d_coords = wv.get_2d_coords(camera, three_d_coords)
    # convert to int
    two_d_coords = (int(two_d_coords[0]), int(two_d_coords[1]))
    # draw a black circle at the 2D coordinates
    cv2.circle(frame, two_d_coords, 10, (0, 0, 0), 1)
    # write the 3D coordinates
    cv2.putText(frame, f"({three_d_coords[0]:.2f}, {three_d_coords[1]:.2f}, {three_d_coords[2]:.2f})", (cursor_location[0] + 10, cursor_location[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    # draw a circle at center
    cv2.circle(frame, (320, 240), 5, (0, 255, 255), -1)
    # draw a vertical and horizontal line at center
    cv2.line(frame, (320, 0), (320, 480), (0, 255, 255), 1)
    cv2.line(frame, (0, 240), (640, 240), (0, 255, 255), 1)

    results = model.track(frame, persist=True)

    for result in results:
        # draw bounding boxes
        for box, class_id, tracker_ID in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.id):
            # get class name
            class_name = class_names[int(class_id)]

            # continue if not car | truck | bus
            if class_name not in ["car", "truck", "bus"]:
                continue

            # draw bounding box
            cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (200, 200, 200), 1)
            # draw a filled rectangle on top of bounding box
            cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[1]) - 15), (200, 200, 200), -1)

            # bottom center point
            bottom_center_point = (int((box[0] + box[2]) / 2), int(box[3]))

            # get 3D coordinates
            three_d_coords = wv.get_3d_coords(camera, bottom_center_point)

            # calculate distance from x-axis
            obj_dist = wv.calc_distance(three_d_coords, (three_d_coords[0], 0, 0))

            # draw distance text
            cv2.putText(frame, f"{obj_dist:.2f}m", (int(box[0]), int(box[1]) - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # calculate fps
    fps = 1.0 / (time.time() - start_time)
    # draw fps text
    cv2.putText(frame, f"{fps:.2f}fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
