import tkinter
import tkinter.messagebox
import asyncio
import threading
import customtkinter
from PIL import Image
from utils import lt200b, config
from utils.jobmanager import create_job
from bleak import exc as bleak_exc
from bleak import BleakScanner


class MainTabView(customtkinter.CTkTabview):
    def __init__(self, master, app_reference, **kwargs):
        super().__init__(master, **kwargs)

        # Tabs
        self.add("Text Label")
        self.add("Image Label")

        # Widgets on tabs
        # Text label
        self.textinput_label = customtkinter.CTkLabel(master=self.tab("Text Label"), text="Text Input")
        self.textinput_label.grid(row=0, column=0, padx=20, pady=10)
        self.textinput = customtkinter.CTkTextbox(master=self.tab("Text Label"), width=240, height=80, wrap="none")
        self.textinput.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        self.print_txt_button = customtkinter.CTkButton(
            master=self.tab("Text Label"),
            text="Print Label",
            command=lambda: app_reference.btn_print_txt_label(self.textinput.get())
        )
        self.print_txt_button.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

        # Image label
        self.load_img_button = customtkinter.CTkButton(
            master=self.tab("Image Label"),
            text="Load Image",
            command=app_reference.btn_load_image
        )
        self.load_img_button.grid(row=0, column=0, padx=20, pady=10)

        # Image preview label
        self.image_label = customtkinter.CTkLabel(
            master=self.tab("Image Label"),
            text="No Image",
            width=200,
            height=150
        )
        self.image_label.grid(row=1, column=0, padx=20, pady=10)

        self.print_img_button = customtkinter.CTkButton(
            master=self.tab("Image Label"),
            text="Print Label",
            command=app_reference.btn_print_image
        )
        self.print_img_button.grid(row=2, column=0, padx=20, pady=10)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # Window geometry and settings
        self.device_window = None
        self.device_frame = None
        self.scan_label = None
        self.geometry("320x500")
        self.title("LT200B Label Maker")
        self.grid_columnconfigure(0, weight=1)

        # Printer MAC Address label
        self.mac_addr_label = customtkinter.CTkLabel(master=self, text="Printer MAC Address:")
        self.mac_addr_label.grid(row=0, column=0, padx=20, pady=0)
        self.mac_addr_input = customtkinter.CTkEntry(master=self)
        self.mac_addr_input.grid(row=1, column=0, padx=0, pady=0)

        # Scan for printer label
        self.scan_button = customtkinter.CTkButton(
            master=self,
            text="Scan for Printer",
            command=self.btn_scan_for_printer
        )
        self.scan_button.grid(row=2, column=0, padx=20, pady=(10, 0))

        # Tab (MainTabView class)
        self.tab_view = MainTabView(self, app_reference=self)
        self.tab_view.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

        # Config helper
        stored_cfg = config.load_config()
        if "last_printer" in stored_cfg:
            self.mac_addr_input.insert(0, stored_cfg["last_printer"])

    # Messagebox helper
    def safe_alert(self, title: str, message: str, level="error"):
        if level == "error":
            self.after(0, lambda: tkinter.messagebox.showerror(title, message))
        elif level == "info":
            self.after(0, lambda: tkinter.messagebox.showinfo(title, message))
        elif level == "warning":
            self.after(0, lambda: tkinter.messagebox.showwarning(title, message))

    def btn_print_txt_label(self, text_value: str):
        threading.Thread(target=lambda: asyncio.run(self._async_print_txt_label(text_value))).start()

    def btn_load_image(self):
        file_path = tkinter.filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not file_path:
            return

        # Load image and create thumbnail
        img = Image.open(file_path)
        img.thumbnail((200, 150))  # resize for preview

        self.loaded_image = img
        self.ctk_preview_image = customtkinter.CTkImage(light_image=img, size=(200, 150))

        # Update the image label in tab
        self.tab_view.image_label.configure(image=self.ctk_preview_image, text="")

    def btn_print_image(self):
        threading.Thread(target=lambda: asyncio.run(self._async_print_image())).start()

    def btn_scan_for_printer(self):
        self.device_window = customtkinter.CTkToplevel(self)
        self.device_window.title("Scanning for Printers")
        self.device_window.geometry("360x400")

        self.scan_label = customtkinter.CTkLabel(self.device_window, text="Scanning for devices...")
        self.scan_label.pack(pady=10)

        self.device_frame = customtkinter.CTkScrollableFrame(self.device_window, width=280, height=300)
        self.device_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Bring the window to the top immediately after creation
        self.device_window.lift()

        # Schedule grab_set after the window becomes viewable
        self.after(100, lambda: self.device_window.grab_set())

        # Start the asynchronous scan in a separate thread
        threading.Thread(target=lambda: asyncio.run(self._async_scan_for_printer())).start()


    def select_device(self, address, name, window):
        self.mac_addr_input.delete(0, "end")
        self.mac_addr_input.insert(0, address)
        config.save_config({"last_printer": address})
        self.safe_alert("Device Selected", f"{name} selected.", level="info")
        window.destroy()

    def populate_device_window(self, devices):
        if not hasattr(self, "device_window") or not self.device_window.winfo_exists():
            return  # the window was closed or destroyed

        if not hasattr(self, "scan_label") or not self.scan_label.winfo_exists():
            return  # label was destroyed

        self.scan_label.configure(text="Select a device:")

        for device in devices:
            name = device.name or "Unknown"
            addr = device.address

            btn_text = f"{name} ({addr})"
            button = customtkinter.CTkButton(
                master=self.device_frame,
                text=btn_text,
                command=lambda a=addr, n=name, w=self.device_window: self.select_device(a, n, w)
            )
            button.pack(pady=5, fill="x", padx=10)

    async def _async_print_image(self):
        mac_addr = self.mac_addr_input.get()
        if not mac_addr:
            self.safe_alert("No MAC Address", "Please provide the MAC Address of the printer.", level="info")
            return

        if not hasattr(self, "loaded_image") or self.loaded_image is None:
            self.safe_alert("No Image", "Please load an image to print.", level="info")
            return

        try:
            request = create_job(self.loaded_image)
            await lt200b.print_image(mac_addr, request)
        except bleak_exc.BleakDeviceNotFoundError:
            self.safe_alert("Error", f"The device with MAC Address {mac_addr} is not found. Is the device powered on?", level="error")
        except Exception as e:
            self.safe_alert("Error", f"Unexpected error:\n{str(e)}", level="error")

    async def _async_print_txt_label(self, text_value: str):
        mac_addr = self.mac_addr_input.get()
        if not mac_addr:
            self.safe_alert("No MAC Address", "Please provide the MAC Address of the printer.", level="info")
            return

        if not text_value:
            self.safe_alert("Label empty", "The label text is empty. Please provide a label text", level="info")
            return

        try:
            with lt200b.create_text_image(text_value, None, 64) as img:
                request = create_job(img)
                await lt200b.print_image(mac_addr, request)
        except bleak_exc.BleakDeviceNotFoundError:
            self.safe_alert("Error", f"The device with MAC Address {mac_addr} is not found. Is the device powered on?", level="error")
        except Exception as e:
            self.safe_alert("Error", f"Unexpected error:\n{str(e)}", level="error")

    async def _async_scan_for_printer(self):
        try:
            self.device_window.lift()

            devices = await BleakScanner.discover(timeout=5.0)

            filtered = [d for d in devices if d.name]  # Only show named devices

            if not filtered:
                self.safe_alert("Scan Complete", "No devices found.")
                return

            self.after(0, lambda: self.populate_device_window(filtered))
            self.after(0, lambda: self.device_window.lift())


        except Exception as e:
            self.safe_alert("Scan Error", str(e))


app = App()
app.mainloop()