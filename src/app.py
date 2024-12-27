import tkinter as tk
from var import * 
from PIL import Image, ImageTk
import cv2
import os


class App():
    def __init__(self, window) -> None:
        self.window = window
        window.geometry("{}x{}+{}+{}".format(WINDOWN_WIDTH, WINDOWN_HEIGHT, WINDOWN_POSITION_RIGHT, WINDOWN_POSITION_DOWN))

        # Initialize saved images list
        self.saved_images = []

        # Title
        window.title("Project Name")
        # Background
        window['background'] = COLOR_BACKGROUND

        # HEADER
        header_frame = tk.Frame(window, bg=COLOR_COMPONENT, height=70)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(header_frame, text="PROJECT NAME", font=(TEXT_FONT, 24, "bold"), fg=COLOR_HEADER, bg=COLOR_COMPONENT)
        header_label.pack()

        # MAIN FRAME
        main_frame = tk.Frame(window, bg=COLOR_BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Camera frame
        self.camera_frame = tk.Frame(main_frame, bg=COLOR_NOT_USER, width=760, height=300, relief="solid", borderwidth=2)
        self.camera_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.camera_frame.pack_propagate(False)
        
        self.camera_label = tk.Label(self.camera_frame, text="Camera is not connected", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_NOT_USER)
        self.camera_label.pack(expand=True)

        # Commands frame
        commands_frame = tk.Frame(main_frame, bg=COLOR_COMPONENT)
        commands_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        commands_title_label = tk.Label(commands_frame, text="Session Commands", font=(TEXT_FONT, 18, "bold"), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        commands_title_label.pack()

        # Button frame
        button_frame = tk.Frame(commands_frame, bg=COLOR_COMPONENT, width=500)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=180)

        self.button_start_session = tk.Button(button_frame, text="Start Session", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_COMPONENT, relief="flat", command=self.start_session)
        self.button_capture_image = tk.Button(button_frame, text="Capture Image", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_COMPONENT, relief="flat", command=self.capture_image)
        self.button_end_session = tk.Button(button_frame, text="End Session", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_COMPONENT, relief="flat", command=self.end_session)
        self.button_upload_analyze = tk.Button(button_frame, text="Upload and Analyze", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_COMPONENT, relief="flat")
        self.button_chose_image = tk.Button(button_frame, text="Choose Image", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_COMPONENT, relief="flat")
        self.button_exit = tk.Button(button_frame, text="Exit", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_COMPONENT, relief="flat", command=self.on_closing)

        self.button_start_session.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.button_capture_image.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.button_end_session.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.button_upload_analyze.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.button_chose_image.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.button_exit.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # Photo frame with scrollbar
        self.photo_frame = tk.Frame(main_frame, bg=COLOR_COMPONENT, width=600, height=300)
        self.photo_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.photo_frame.pack_propagate(False)

        # Create the canvas for images
        self.photo_canvas = tk.Canvas(self.photo_frame, bg=COLOR_COMPONENT)
        self.photo_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Create the scrollbar
        self.scrollbar = tk.Scrollbar(self.photo_frame, orient="vertical", command=self.photo_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")

        # Link the scrollbar with the canvas
        self.photo_canvas.config(yscrollcommand=self.scrollbar.set)

        self.photo_label = tk.Label(self.photo_frame, text="", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        self.photo_label.pack(expand=True)
        self.photo_label.bind("<Button-1>", self.set_camera_image) 


        # Footer frame
        footer_frame = tk.Frame(window, bg=COLOR_BACKGROUND)
        footer_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Result frame
        result_frame = tk.Frame(footer_frame, bg=COLOR_COMPONENT)
        result_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        result_label = tk.Label(result_frame, text="Result", font=(TEXT_FONT, 16, "bold"), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        result_label.pack(anchor="w")

        result_text = tk.Text(result_frame, height=4, bg=COLOR_COMPONENT, fg=COLOR_TEXT, font=(TEXT_FONT, 10), relief="flat", width=108)
        result_text.insert("1.0", "Họ và tên: Dinh Viet Hoang\nGiới tính: Nam\nÁo: Đen")
        result_text.configure(state="disabled")
        result_text.pack(fill=tk.X, pady=5)

        # Session frame now
        session_frame_now = tk.Frame(footer_frame, bg=COLOR_COMPONENT)
        session_frame_now.grid(row=1, column=0, padx=10, sticky="nsew")

        current_session_label = tk.Label(session_frame_now, text="Current session:", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        current_session_label.pack(anchor="w")
        selected_session_label = tk.Label(session_frame_now, text="Selected session:", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        selected_session_label.pack(anchor="w")

        # Session frame last
        session_frame_last = tk.Frame(footer_frame, bg=COLOR_COMPONENT, width=622, height=190)
        session_frame_last.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        session_frame_last.pack_propagate(False)

        # Initialize Camera
        self.cap = None
        self.camera_active = False
        self.video_width = 640
        self.video_height = 480

    def start_session(self):
        if not self.camera_active:
            self.camera_active = True
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)  # Open camera
            if self.cap.isOpened():
                self.camera_label.config(text="")  # Clear text
                self.update_video_feed()
            else:
                self.camera_label.config(text="Camera is not available")

    def end_session(self):
        if self.camera_active:
            self.camera_active = False
            if self.cap is not None:
                self.cap.release()  # Release the camera
                self.cap = None
            self.camera_label.config(image="", text="Camera is not connected", bg="black", fg="white")

    def capture_image(self):
        if self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                # Đường dẫn thư mục lưu ảnh
                save_dir = "./public/saved_img"
                # Tạo thư mục nếu chưa tồn tại
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                image_path = f"{save_dir}/captured_image_{len(self.saved_images) + 1}.jpg"
                cv2.imwrite(image_path, frame)
                self.saved_images.append(image_path)  # Lưu đường dẫn ảnh vào danh sách
                self.update_photo_canvas()  # Cập nhật hiển thị ảnh
    
    # def update_photo_frame(self):
    # # Xóa nội dung cũ trong Canvas
    #     for widget in self.photo_canvas.winfo_children():
    #         widget.destroy()

    # # Tạo và hiển thị các ảnh từ danh sách
    #     for idx, image_path in enumerate(self.saved_images):
    #         image = Image.open(image_path)
    #         image = image.resize((150, 100))  # Resize nhỏ hơn để hiển thị nhiều ảnh
    #         photo_img = ImageTk.PhotoImage(image)

    #         # Tạo một nhãn cho mỗi ảnh
    #         image_label = tk.Label(self.photo_canvas, image=photo_img, bg=COLOR_COMPONENT)
    #         image_label.photo = photo_img  # Lưu tham chiếu để tránh bị xóa
    #         image_label.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)  # Hiển thị theo lưới

    def update_photo_canvas(self):
        # Xóa toàn bộ nội dung cũ trên Canvas
        self.photo_canvas.delete("all")
        
        # Lưu tham chiếu ảnh trong danh sách
        self.photo_canvas.image_refs = []  

        for idx, image_path in enumerate(self.saved_images):
            # Load và resize ảnh
            image = Image.open(image_path).resize((150, 100))
            photo_img = ImageTk.PhotoImage(image)
            
            # Lưu tham chiếu để tránh bị giải phóng bộ nhớ
            self.photo_canvas.image_refs.append(photo_img)
            
            # Tính toán vị trí hiển thị ảnh
            x = (idx % 4) * 160 + 10  # Cách nhau 160px theo chiều ngang
            y = (idx // 4) * 110 + 10  # Cách nhau 110px theo chiều dọc

            # Vẽ ảnh lên Canvas
            self.photo_canvas.create_image(x, y, image=photo_img, anchor="nw")


    def update_video_feed(self):
        if self.camera_active and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.video_width, self.video_height))

                img = ImageTk.PhotoImage(image=Image.fromarray(frame))

                self.camera_label.imgtk = img
                self.camera_label.config(image=img)

        if self.camera_active:
            self.window.after(10, self.update_video_feed)

    def show_image(self, image_path):
        image = Image.open(image_path)
        image = image.resize((600, 300))  # Resize to fit the photo frame
        photo_img = ImageTk.PhotoImage(image)

        # Update photo label to display the image
        self.photo_label.config(image=photo_img, text="")
        self.photo_label.photo = photo_img

    def on_closing(self):
        self.end_session()  # Ensure camera is turned off before closing
        self.window.destroy()

    def set_camera_image(self, event):
        # Check if photo_label has an image
        if hasattr(self.photo_label, "photo") and self.photo_label.photo is not None:
            self.camera_active = False
            self.camera_label.config(image=self.photo_label.photo)  # Set the camera label to show the image clicked
            self.camera_label.imgtk = self.photo_label.photo  # Maintain a reference to the image object
            self.camera_label.config(text="")  # Clear the text
        else:
            self.start_session()  # If no image, restart the camera session to show the feed