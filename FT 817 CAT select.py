import serial
import time
import tkinter as tk
from tkinter import messagebox


class FT817Controller:
    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Initialize the FT-817 Controller.
        
        :param port: The COM port to which the FT-817 is connected (e.g., COM3 or /dev/ttyUSB0).
        :param baudrate: Baud rate for the serial connection (default: 9600).
        :param timeout: Timeout for serial reads (default: 1 second).
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        """Establish a serial connection to the FT-817."""
        self.connection = serial.Serial(
            self.port,
            self.baudrate,
            timeout=self.timeout
        )

    def disconnect(self):
        """Close the serial connection."""
        if self.connection:
            self.connection.close()

    def send_command(self, command):
        """
        Send a CAT command to the FT-817.
        
        :param command: A bytes object representing the CAT command.
        :return: The response from the transceiver.
        """
        if not self.connection or not self.connection.is_open:
            raise Exception("Not connected to FT-817")
        self.connection.write(command)
        time.sleep(0.1)  # Wait for the transceiver to process
        return self.connection.read(5)  # CAT commands typically return 5 bytes


class FT817App:
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        :param root: The root window for the tkinter application.
        """
        self.root = root
        self.root.title("FT-817 Controller")
        self.controller = None

        # Create GUI elements
        self.port_label = tk.Label(root, text="COM Port:")
        self.port_label.grid(row=0, column=0, padx=10, pady=10)
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=0, column=1, padx=10, pady=10)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect)
        self.connect_button.grid(row=1, column=0, padx=10, pady=10)

        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(row=1, column=1, padx=10, pady=10)

        self.command_label = tk.Label(root, text="CAT Command:")
        self.command_label.grid(row=2, column=0, padx=10, pady=10)
        self.command_var = tk.StringVar(root)
        self.command_var.set("Get Frequency (0x03)")  # Default command

        self.command_menu = tk.OptionMenu(
            root, self.command_var, 
            "Get Frequency (0x03)", 
            "Set Mode (0x07)", 
            "Get Status (0xE7)"
        )
        self.command_menu.grid(row=2, column=1, padx=10, pady=10)

        self.param_label = tk.Label(root, text="Parameters (Hex):")
        self.param_label.grid(row=3, column=0, padx=10, pady=10)
        self.param_entry = tk.Entry(root)
        self.param_entry.grid(row=3, column=1, padx=10, pady=10)

        self.send_button = tk.Button(root, text="Send Command", command=self.send_command)
        self.send_button.grid(row=4, column=0, padx=10, pady=10)

        self.response_label = tk.Label(root, text="Response:")
        self.response_label.grid(row=4, column=1, padx=10, pady=10)
        self.response_var = tk.StringVar(root, value="N/A")
        self.response_value = tk.Label(root, textvariable=self.response_var)
        self.response_value.grid(row=5, column=1, padx=10, pady=10)

    def connect(self):
        """Connect to the FT-817."""
        port = self.port_entry.get()
        try:
            self.controller = FT817Controller(port)
            self.controller.connect()
            messagebox.showinfo("Connection", f"Connected to FT-817 on {port}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def disconnect(self):
        """Disconnect from the FT-817."""
        if self.controller:
            self.controller.disconnect()
            self.controller = None
            messagebox.showinfo("Connection", "Disconnected from FT-817")

    def send_command(self):
        """Send a CAT command based on user selection."""
        if not self.controller:
            messagebox.showerror("Error", "Not connected to FT-817")
            return

        command_str = self.command_var.get()
        param_str = self.param_entry.get()

        try:
            # Default commands in hex
            command_map = {
                "Get Frequency (0x03)": b"\x03",
                "Set Mode (0x07)": b"\x07",  # Example mode command
                "Get Status (0xE7)": b"\xE7"  # Example status command
            }

            command = command_map[command_str]

            # Append user-defined parameters if provided
            if param_str:
                command += bytes.fromhex(param_str)

            # Send the command and display the response
            response = self.controller.send_command(command)
            self.response_var.set(response.hex() if response else "No Response")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FT817App(root)
    root.mainloop()