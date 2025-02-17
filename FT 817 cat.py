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

    def set_frequency(self, frequency_hz):
        """
        Set the transceiver frequency.
        
        :param frequency_hz: Frequency in Hertz (e.g., 145000000 for 145 MHz).
        """
        freq_bcd = f"{frequency_hz:010d}"[::-1]  # Reverse the digits for BCD
        command = bytes.fromhex(freq_bcd + "01")
        self.send_command(command)

    def get_frequency(self):
        """
        Get the current frequency from the transceiver.
        
        :return: The frequency in Hertz.
        """
        response = self.send_command(b"\x03")
        freq_bcd = response[:4][::-1].hex()
        return int(freq_bcd)


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

        self.freq_label = tk.Label(root, text="Frequency (Hz):")
        self.freq_label.grid(row=1, column=0, padx=10, pady=10)
        self.freq_entry = tk.Entry(root)
        self.freq_entry.grid(row=1, column=1, padx=10, pady=10)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect)
        self.connect_button.grid(row=2, column=0, padx=10, pady=10)

        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.grid(row=2, column=1, padx=10, pady=10)

        self.set_button = tk.Button(root, text="Set Frequency", command=self.set_frequency)
        self.set_button.grid(row=3, column=0, padx=10, pady=10)

        self.get_button = tk.Button(root, text="Get Frequency", command=self.get_frequency)
        self.get_button.grid(row=3, column=1, padx=10, pady=10)

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

    def set_frequency(self):
        """Set the transceiver frequency."""
        if not self.controller:
            messagebox.showerror("Error", "Not connected to FT-817")
            return
        try:
            frequency = int(self.freq_entry.get())
            self.controller.set_frequency(frequency)
            messagebox.showinfo("Frequency", f"Frequency set to {frequency} Hz")
        except ValueError:
            messagebox.showerror("Error", "Invalid frequency value")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set frequency: {e}")

    def get_frequency(self):
        """Get the current frequency from the transceiver."""
        if not self.controller:
            messagebox.showerror("Error", "Not connected to FT-817")
            return
        try:
            frequency = self.controller.get_frequency()
            messagebox.showinfo("Frequency", f"Current frequency: {frequency} Hz")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get frequency: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FT817App(root)
    root.mainloop()