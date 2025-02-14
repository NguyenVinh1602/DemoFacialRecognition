import tkinter as tk
import uuid
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
        # List to store image ids and their paths
        self.image_objects = []  

        self.session_dir = None
        self.image_count = 0
        self.session_id = 0 # selected sessions_id
        self.current_session = 0 # current session - start a new session
        self.session_ls = self.reload_session()  # list of all sessions
        self.image_labels = []  # To hold image labels for gallery display

        # Title
        window.title("Project Name")
        # Background
        window['background'] = COLOR_BACKGROUND

        # HEADER
        header_frame = tk.Frame(window, bg=COLOR_COMPONENT, height=70)
        header_frame.pack(fill=tk.X)

        header_label = tk.Label(header_frame, text="PROJECT NAME", font=(TEXT_FONT, 24, "bold"), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        header_label.pack()

        # MAIN FRAME
        main_frame = tk.Frame(window, bg=COLOR_BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Camera frame
        self.camera_frame = tk.Frame(main_frame, bg=COLOR_DISABLED, width=810, height=240, relief="solid", borderwidth=2)
        self.camera_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=(10,0), sticky="nsew")
        self.camera_frame.pack_propagate(False)
        
        self.camera_label = tk.Label(self.camera_frame, text="Camera is not connected", font=(TEXT_FONT, 12), fg= COLOR_TEXT_DISABLED, bg=COLOR_DISABLED)
        self.camera_label.pack(expand=True)

        # Commands frame
        commands_frame = tk.Frame(main_frame, bg=COLOR_COMPONENT)
        commands_frame.grid(row=0, column=1, padx=10, pady=(10, 0) ,sticky="new")

        commands_title_label = tk.Label(commands_frame, text="Session Commands", font=(TEXT_FONT, 18, "bold"), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        commands_title_label.pack()

        # Button frame
        button_frame = tk.Frame(commands_frame, bg=COLOR_COMPONENT, width=650)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=180)

        self.button_start_session = tk.Button(button_frame, text="Start Session", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_TEXT, relief="flat", command=self.start_session, width= 20)
        self.button_capture_image = tk.Button(button_frame, text="Capture Image", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_TEXT, relief="flat", command=self.capture_image, width= 20)
        self.button_end_session = tk.Button(button_frame, text="End Session", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_TEXT, relief="flat", command=self.end_session, width= 20)
        self.button_upload_analyze = tk.Button(button_frame, text="Upload and Analyze", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_TEXT, relief="flat", width = 20)
        self.button_exit = tk.Button(button_frame, text="Exit", font=(TEXT_FONT, 10), bg=COLOR_BUTTON, fg=COLOR_TEXT, relief="flat", command=self.on_closing, width= 20)

        self.button_start_session.pack(fill= tk.X, pady= 5 )
        self.button_capture_image.pack(fill= tk.X, pady= 5 )
        self.button_end_session.pack(fill= tk.X, pady= 5 )
        self.button_upload_analyze.pack(fill= tk.X, pady= 5 )
        self.button_exit.pack(fill= tk.X, pady= 5 )

        self.button_capture_image.config(state = tk.DISABLED)
        self.button_upload_analyze.config(state = tk.DISABLED)
        self.button_end_session.config(state = tk.DISABLED)

        # Photo frame with scrollbar
        self.photo_frame = tk.Frame(main_frame, bg=COLOR_COMPONENT, width=650, height=260)
        self.photo_frame.grid(row=1, column=1, padx=10, pady=(10,0), sticky="nsew")
        self.photo_frame.pack_propagate(False)

        # Create the canvas for images
        self.photo_canvas = tk.Canvas(self.photo_frame, bg=COLOR_COMPONENT)
        self.photo_canvas.image_refs = []
        self.photo_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Create the scrollbar
        self.scrollbar = tk.Scrollbar(self.photo_frame, orient="vertical", command=self.photo_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.photo_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside canvas
        self.scrollable_frame = tk.Frame(self.photo_canvas, bg=COLOR_COMPONENT)
        self.photo_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Bind <Configure> to update scrollregion
        self.scrollable_frame.bind("<Configure>", lambda e: self.photo_canvas.configure(scrollregion=self.photo_canvas.bbox("all")))

        self.photo_label = tk.Label(self.photo_frame, text="", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        self.photo_label.pack(expand=True)
        self.photo_label.bind("<Button-1>", self.set_camera_image) 


        # Footer frame
        footer_frame = tk.Frame(window, bg=COLOR_BACKGROUND)
        footer_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Result frame
        result_frame = tk.Frame(footer_frame, bg=COLOR_COMPONENT)
        result_frame.grid(row=0, column=0, padx=10, pady=(0,10), sticky="nsew")

        result_title = tk.Label(result_frame, text="Result", font=(TEXT_FONT, 16, "bold"), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        result_title.pack(anchor="w", padx=10, pady= 5)

        self.result_labels = {}
        # actions = [
        #     ("Get ID", self.get_id),
        #     ("Get Cloth Color", self.get_cloth_color),
        #     ("Get Tie", self.get_tie),
        #     ("Get Glasses", self.get_glasses),
        #     ("Get Name Tag", self.get_name_tag),        
        # ]

        result_label = tk.Label(result_frame, height=5, bg=COLOR_COMPONENT, fg=COLOR_TEXT, font=(TEXT_FONT, 10), relief="flat", width=100)
        result_label.pack()

        # Session frame now
        session_frame_now = tk.Frame(footer_frame, bg=COLOR_COMPONENT)
        session_frame_now.grid(row=1, column=0, padx=10, sticky="new")

        self.current_session_label = tk.Label(session_frame_now, text="Current session: None", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        self.current_session_label.pack(anchor="w")
        self.selected_session_label = tk.Label(session_frame_now, text="Selected session: None", font=(TEXT_FONT, 12), fg=COLOR_TEXT, bg=COLOR_COMPONENT)
        self.selected_session_label.pack(anchor="w")

        # Session frame last
        session_frame_last = tk.Frame(footer_frame, bg=COLOR_COMPONENT, width=650, height=180)
        session_frame_last.grid(row=0, column=1, rowspan=2, padx=10, sticky="new")
        session_frame_last.pack_propagate(False)

        # Initialize Camera
        self.cap = None
        self.camera_active = False
        self.video_width = 810
        self.video_height = 500

    def start_session(self):
        self.session_id =uuid.uuid4()
        self.button_start_session.config(state=tk.DISABLED)
        if not self.camera_active:
            self.camera_active = True
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)  # Open camera
            if self.cap.isOpened():
                self.camera_label.config(text="")  # Clear text
                self.update_video_feed()
                self.current_session_label.config(text=f"Current session: {self.session_id}")
                self.image_count = 0
                self.button_end_session.config(state=tk.NORMAL)
                self.button_capture_image.config(state=tk.NORMAL)
                self.button_upload_analyze.config(state=tk.NORMAL)
            else:
                self.camera_label.config(text="Camera is not available")

    def off_cam(self):
        self.button_start_session.config(state=tk.NORMAL)
        self.button_end_session.config(state=tk.DISABLED)
        if self.camera_active:
            self.camera_active = False
            if self.cap is not None:
                self.cap.release()  # Release the camera
                self.cap = None
            self.camera_label.config(image="", text="Camera is not connected", bg=COLOR_DISABLED, fg=COLOR_TEXT_DISABLED)

    def end_session(self):
        self.button_capture_image.config(state=tk.DISABLED)
        self.button_upload_analyze.config(state=tk.DISABLED)
        self.off_cam()

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
    
    def update_photo_canvas(self):
        # Xóa toàn bộ nội dung cũ trên Canvas
        self.photo_canvas.delete("all")
        self.image_objects.clear()  # Clear the image objects list
        self.photo_canvas.image_refs.clear()

        for idx, image_path in enumerate(self.saved_images):
            # Load và resize ảnh
            image = Image.open(image_path).resize((140, 100))
            photo_img = ImageTk.PhotoImage(image)
            
            # Lưu tham chiếu để tránh bị giải phóng bộ nhớ
            self.photo_canvas.image_refs.append(photo_img)
            
            # Tính toán vị trí hiển thị ảnh
            x = (idx % 4) * 160 + 10  # Cách nhau 160px theo chiều ngang
            y = (idx // 4) * 110 + 10  # Cách nhau 110px theo chiều dọc

            # Vẽ ảnh lên Canvas
            img_id = self.photo_canvas.create_image(x, y, image=photo_img, anchor="nw", tags="image")

            # Save the ID and the path of the image in the image_objects list
            self.image_objects.append((img_id, image_path))
        # Cập nhật scrollregion
        self.photo_canvas.configure(scrollregion=self.photo_canvas.bbox("all"))

        # Bind click event on the canvas to handle image clicks
        self.photo_canvas.tag_bind("image", "<Button-1>", self.on_image_click)


    def on_image_click(self, event):
        # Get the ID of the clicked object
        clicked_item = self.photo_canvas.find_withtag("current")

        # Check if we clicked an image
        if clicked_item:
            # Retrieve the image ID from the list using the clicked item
            for img_id, image_path in self.image_objects:
                if img_id == clicked_item[0]:
                    self.off_cam()
                    # Open and display the clicked image
                    image = Image.open(image_path).resize((self.video_width, self.video_height))
                    photo_img = ImageTk.PhotoImage(image)

                    # Display the image in the camera label
                    self.camera_label.imgtk = photo_img  # Maintain reference to avoid garbage collection
                    self.camera_label.config(image=photo_img, text="")  # Set the image and clear the text
                    return
                
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
    # Get the coordinates of the mouse click
        x, y = self.photo_canvas.canvasx(event.x), self.photo_canvas.canvasy(event.y)
        
        # Identify which image was clicked
        for idx, image_path in enumerate(self.saved_images):
            img_x = (idx % 4) * 160 + 10
            img_y = (idx // 4) * 110 + 10
            img_width, img_height = 140, 100

            # Check if the click is within the bounds of an image
            if img_x <= x <= img_x + img_width and img_y <= y <= img_y + img_height:
                # Load and display the clicked image in the camera label
                image = Image.open(image_path).resize((self.video_width, self.video_height))
                photo_img = ImageTk.PhotoImage(image)
                
                self.camera_label.imgtk = photo_img  # Maintain reference to avoid garbage collection
                self.camera_label.config(image=photo_img, text="")  # Set the image and clear the text
                return
    def reload_session(self):
        #read all old folder from clients --> session_id
        # base_img_dir = Path("gallery")
        # Get a list of all folder names in the directory
        # return [folder.name for folder in base_img_dir.iterdir() if folder.is_dir()]
        return 

def create_main_window():
    window = tk.Tk()
    app = App(window)
    window.mainloop()

if __name__ == "__main__":
    create_main_window()
