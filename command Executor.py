import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from netmiko import ConnectHandler
from datetime import datetime
import os
import json
from PIL import Image, ImageTk
import ipaddress
import threading
import time

# Global variable to hold the Netmiko connection
net_connect = None
saved_details_file = 'saved_details.json'

def get_interfaces(device):
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        output = net_connect.send_command('show ip interface brief')
        net_connect.disconnect()
        
        interfaces = ["None"]
        for line in output.splitlines()[1:]:
            interface = line.split()[0]
            interfaces.append(interface)
        return interfaces
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return ["None"]

def execute_command():
    global net_connect
    device = {
        "device_type": "cisco_ios",
        "host": host_entry.get(),
        "username": username_entry.get(),
        "password": password_entry.get(),
        "secret": secret_entry.get(),
    }
    
    command = command_type.get()
    selected_interface = interface_var.get()
    output_text.delete(1.0, tk.END)  # Clear previous output
    
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        connection_status.config(text="Connected", fg="green")
        
        if command == "show ip interface brief":
            output = net_connect.send_command('show ip interface brief')
        elif command == "show vlan":
            output = net_connect.send_command('show vlan')
        elif command == "show running-config":
            output = net_connect.send_command('show running-config')
        elif command == "show interfaces" and selected_interface != "None":
            output = net_connect.send_command(f'show interfaces {selected_interface}')
        elif command == "show ip interface" and selected_interface != "None":
            output = net_connect.send_command(f'show ip interface {selected_interface}')
        elif command == "show running-config interface" and selected_interface != "None":
            output = net_connect.send_command(f'show running-config interface {selected_interface}')
        elif command == "show routing":
            output = net_connect.send_command('show ip route')
        
        output_text.insert(tk.END, output)
        interface_status_label.grid_remove()
        download_button.config(state=tk.NORMAL)
        
    except Exception as e:
        output_text.insert(tk.END, f"An error occurred: {e}")
        connection_status.config(text="Not Connected", fg="red")

def disconnect():
    global net_connect
    if net_connect:
        net_connect.disconnect()
        net_connect = None
        connection_status.config(text="Disconnected", fg="red")
        output_text.insert(tk.END, "Disconnected from the device.\n")
    else:
        output_text.insert(tk.END, "No active connection to disconnect.\n")

def clear_output():
    output_text.delete(1.0, tk.END)
    download_button.config(state=tk.DISABLED)

def reboot_device():
    global net_connect
    password = simpledialog.askstring("Password", "Enter Cisco IOS password:", show='*')
    
    if password == password_entry.get():
        device = {
            "device_type": "cisco_ios",
            "host": host_entry.get(),
            "username": username_entry.get(),
            "password": password_entry.get(),
            "secret": secret_entry.get(),
        }
        
        try:
            net_connect = ConnectHandler(**device)
            net_connect.enable()
            net_connect.send_command_timing('reload', strip_prompt=False, strip_command=False)
            net_connect.send_command_timing('\n', strip_prompt=False, strip_command=False)
            output_text.delete(1.0, tk.END)  # Clear output after issuing reboot command
            output_text.insert(tk.END, "Reboot command issued. The device will reboot shortly.\n")
            connection_status.config(text="Connected", fg="green")
            
        except Exception as e:
            output_text.insert(tk.END, f"An error occurred: {e}")
            connection_status.config(text="Not Connected", fg="red")
        
        finally:
            net_connect.disconnect()
            net_connect = None
            connection_status.config(text="Disconnected", fg="red")
        
    else:
        output_text.insert(tk.END, "Incorrect password. Reboot aborted.\n")

def update_interfaces():
    device = {
        "device_type": "cisco_ios",
        "host": host_entry.get(),
        "username": username_entry.get(),
        "password": password_entry.get(),
        "secret": secret_entry.get(),
    }
    interfaces = get_interfaces(device)
    interface_combobox['values'] = interfaces
    interface_combobox.current(0)

def on_command_type_change(event):
    command = command_type.get()
    if command in ["show interfaces", "show ip interface", "show running-config interface"]:
        execute_button.config(state=tk.DISABLED)
        interface_status_label.config(text="* Select interface")
        interface_status_label.grid()
    else:
        execute_button.config(state=tk.NORMAL)
        interface_status_label.grid_remove()

def on_interface_select(event):
    if interface_var.get() != "None":
        execute_button.config(state=tk.NORMAL)

def download_output():
    command = command_type.get()
    now = datetime.now().strftime("%H_%M_%d_%m")
    filename = f"{command}_{now}.txt"
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, "w") as file:
        file.write(output_text.get(1.0, tk.END))
    
    messagebox.showinfo("Download Complete", f"Output has been saved as {filepath}")

def save_details():
    details = {
        "host": host_entry.get(),
        "username": username_entry.get(),
        "password": password_entry.get(),
        "secret": secret_entry.get(),
    }
    
    if not os.path.exists(saved_details_file):
        with open(saved_details_file, 'w') as file:
            json.dump([details], file, indent=4)
    else:
        with open(saved_details_file, 'r') as file:
            data = json.load(file)
        
        data.append(details)
        
        with open(saved_details_file, 'w') as file:
            json.dump(data, file, indent=4)
    
    messagebox.showinfo("Save Complete", "Details have been saved.")

def load_details():
    if os.path.exists(saved_details_file):
        with open(saved_details_file, 'r') as file:
            data = json.load(file)
        
        if data:
            def on_host_select(event):
                selected_host = event.widget.cget("text")
                for entry in data:
                    if entry['host'] == selected_host:
                        host_entry.delete(0, tk.END)
                        host_entry.insert(0, entry['host'])
                        username_entry.delete(0, tk.END)
                        username_entry.insert(0, entry['username'])
                        password_entry.delete(0, tk.END)
                        password_entry.insert(0, entry['password'])
                        secret_entry.delete(0, tk.END)
                        secret_entry.insert(0, entry['secret'])
                        break
                select_host_dialog.destroy()

            def delete_host(host):
                for entry in data:
                    if entry['host'] == host:
                        data.remove(entry)
                        with open(saved_details_file, 'w') as file:
                            json.dump(data, file, indent=4)
                        refresh_host_list()
                        if not data:
                            select_host_dialog.destroy()
                        break

            def refresh_host_list():
                for widget in host_frame.winfo_children():
                    widget.destroy()
                for idx, entry in enumerate(data, 1):
                    row_frame = tk.Frame(host_frame)
                    row_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(row_frame, text=f"{idx}.").pack(side=tk.LEFT, padx=5)
                    host_label = tk.Label(row_frame, text=entry['host'], cursor="hand2")
                    host_label.pack(side=tk.LEFT, padx=5)
                    host_label.bind("<Button-1>", on_host_select)
                    delete_button = tk.Button(row_frame, text="Delete", command=lambda h=entry['host']: delete_host(h), bd=0, fg="red")
                    delete_button.pack(side=tk.RIGHT, padx=5)
                    tk.Frame(host_frame, height=1, bd=1, relief=tk.SUNKEN, bg="black").pack(fill=tk.X, pady=2)

            select_host_dialog = tk.Toplevel(root)
            select_host_dialog.title("Select Host")
            
            tk.Label(select_host_dialog, text="Select a host:").pack(padx=10, pady=10)
            host_frame = tk.Frame(select_host_dialog)
            host_frame.pack(padx=10, pady=10)
            refresh_host_list()
    else:
        messagebox.showwarning("Load Failed", "No saved details found.")

def calculate_network_address():
    try:
        ip = ipaddress.ip_interface(f"{ip_entry.get()}/{subnet_mask_entry.get()}")
        network = ip.network
        
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Network Address: {network.network_address}\n")
        result_text.insert(tk.END, f"Broadcast Address: {network.broadcast_address}\n")
        result_text.insert(tk.END, f"Subnet Mask: {network.netmask}\n")
        result_text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def show_range():
    try:
        ip = ipaddress.ip_interface(f"{ip_entry.get()}/{subnet_mask_entry.get()}")
        nhosts = int(nhosts_entry.get())
        required_hosts = nhosts + 2  # Add 2 for network and broadcast addresses
        subnet_mask = (32 - (required_hosts - 1).bit_length())  # Calculate the required subnet mask
        network_address = ipaddress.ip_interface(f"{ip_entry.get()}/{subnet_mask}").network
        
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Network Address: {network_address.network_address}\n")
        result_text.insert(tk.END, f"Broadcast Address: {network_address.broadcast_address}\n")
        result_text.insert(tk.END, f"Number of Hosts: {network_address.num_addresses - 2}\n")
        result_text.insert(tk.END, f"Subnet Mask: {network_address.netmask}\n")
        result_text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def show_subnet_mask():
    try:
        prefix_length = int(subnet_mask_entry.get())
        net = ipaddress.IPv4Network(f'0.0.0.0/{prefix_length}')
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Subnet Mask: {net.netmask}\n")
        result_text.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def connect_watchdog():
    global net_connect
    device = {
        "device_type": "cisco_ios",
        "host": watchdog_host_entry.get(),
        "username": watchdog_username_entry.get(),
        "password": watchdog_password_entry.get(),
        "secret": watchdog_secret_entry.get(),
    }

    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        watchdog_connect_button.config(bg="green", state=tk.DISABLED)
        watchdog_disconnect_button.config(state=tk.NORMAL)
        watchdog_connection_status.config(text="Connected", fg="green")
        
        # Start the watchdog monitoring in a new thread
        threading.Thread(target=watchdog_monitor, daemon=True).start()
        
    except Exception as e:
        watchdog_connection_status.config(text="Not Connected", fg="red")
        messagebox.showerror("Connection Failed", f"An error occurred: {e}")

def disconnect_watchdog():
    global net_connect
    if net_connect:
        net_connect.disconnect()
        net_connect = None
        watchdog_connect_button.config(bg="red", state=tk.NORMAL)
        watchdog_disconnect_button.config(state=tk.DISABLED)
        watchdog_connection_status.config(text="Disconnected", fg="red")
        watchdog_output_text.insert(tk.END, "Disconnected from the device.\n")
    else:
        watchdog_output_text.insert(tk.END, "No active connection to disconnect.\n")

def clear_watchdog_output():
    watchdog_output_text.delete(1.0, tk.END)

def watchdog_monitor():
    global net_connect, previous_status
    try:
        previous_status = {}
        while net_connect:
            output = net_connect.send_command('show ip interface brief')
            current_status = {}
            for line in output.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 6:
                    interface, ip_address, _, _, _, status = parts[:6]
                    current_status[interface] = (status, ip_address)
                    
            for interface, (status, ip_address) in current_status.items():
                if interface not in previous_status:
                    log_message = f"New interface detected: {interface} - Status: {status}, IP: {ip_address}\n"
                elif previous_status[interface][0] != status:
                    log_message = f"Interface {interface} changed status: {previous_status[interface][0]} -> {status}, IP: {ip_address}\n"
                else:
                    continue
                
                watchdog_output_text.insert(tk.END, log_message)
                watchdog_output_text.see(tk.END)
            
            previous_status.update(current_status)
            time.sleep(5)  # Adjust the sleep time as needed

    except Exception as e:
        watchdog_output_text.insert(tk.END, f"An error occurred: {e}\n")
        watchdog_output_text.see(tk.END)
        watchdog_connect_button.config(bg="red", state=tk.NORMAL)
        watchdog_disconnect_button.config(state=tk.DISABLED)
        watchdog_connection_status.config(text="Not Connected", fg="red")

def traffic_monitor():
    global net_connect
    try:
        clear_watchdog_output()  # Clear previous results when the Traffic button is clicked
        while net_connect:
            output = net_connect.send_command('show interfaces')
            watchdog_output_text.insert(tk.END, output + "\n")
            watchdog_output_text.see(tk.END)
            time.sleep(5)  # Adjust the sleep time as needed

    except Exception as e:
        watchdog_output_text.insert(tk.END, f"An error occurred while monitoring traffic: {e}\n")
        watchdog_output_text.see(tk.END)
        watchdog_connect_button.config(bg="red", state=tk.NORMAL)
        watchdog_disconnect_button.config(state=tk.DISABLED)
        watchdog_connection_status.config(text="Not Connected", fg="red")

# Create the main window
root = tk.Tk()
root.title("Command Executor")

# Create a notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create the execution tab
execution_frame = tk.Frame(notebook)
notebook.add(execution_frame, text="Execution")

# Host entry
tk.Label(execution_frame, text="Host:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
host_entry = tk.Entry(execution_frame)
host_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

# Username entry
tk.Label(execution_frame, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
username_entry = tk.Entry(execution_frame)
username_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

# Password entry
tk.Label(execution_frame, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
password_entry = tk.Entry(execution_frame, show='*')
password_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

# Secret entry
tk.Label(execution_frame, text="Secret:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
secret_entry = tk.Entry(execution_frame, show='*')
secret_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

# Command type dropdown
tk.Label(execution_frame, text="Command Type:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
command_type = ttk.Combobox(execution_frame, values=["show ip interface brief", "show vlan", "show running-config", "show interfaces", "show ip interface", "show running-config interface", "show routing"], state="readonly")
command_type.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
command_type.current(0)
command_type.bind("<<ComboboxSelected>>", on_command_type_change)

# Interface selection dropdown
tk.Label(execution_frame, text="Select Interface:").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
interface_var = tk.StringVar()
interface_combobox = ttk.Combobox(execution_frame, textvariable=interface_var)
interface_combobox.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
interface_combobox.bind("<<ComboboxSelected>>", on_interface_select)

# Interface status label
interface_status_label = tk.Label(execution_frame, text="* Select interface", fg="red")
interface_status_label.grid(row=1, column=2, padx=10, pady=5, columnspan=2, sticky=tk.W)
interface_status_label.grid_remove()  # Hide initially

# Execute, Clear, Disconnect, Reboot, and Download buttons
button_frame = tk.Frame(execution_frame)
button_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky=tk.W)
execute_button = tk.Button(button_frame, text="Execute", command=execute_command)
execute_button.pack(side=tk.LEFT, padx=5)
disconnect_button = tk.Button(button_frame, text="Disconnect", command=disconnect, bg="yellow")
disconnect_button.pack(side=tk.LEFT, padx=5)
clear_button = tk.Button(button_frame, text="Clear", command=clear_output)
clear_button.pack(side=tk.LEFT, padx=5)
reboot_button = tk.Button(button_frame, text="Reboot", command=reboot_device, fg="red")
reboot_button.pack(side=tk.LEFT, padx=5)
download_button = tk.Button(button_frame, text="Download", command=download_output, state=tk.DISABLED)
download_button.pack(side=tk.LEFT, padx=5)

# Load, Save buttons and Connection status label
status_frame = tk.Frame(execution_frame)
status_frame.grid(row=5, column=4, pady=10, sticky=tk.W)
load_button = tk.Button(status_frame, text="Load", command=load_details)
load_button.pack(side=tk.LEFT, padx=5)
save_button = tk.Button(status_frame, text="Save", command=save_details)
save_button.pack(side=tk.LEFT, padx=5)
connection_status = tk.Label(status_frame, text="Not Connected", fg="red")
connection_status.pack(side=tk.LEFT, padx=5)

# Output text box
output_text = tk.Text(execution_frame, width=80, height=20, wrap='none', borderwidth=1, relief="solid")
output_text.grid(row=6, column=0, columnspan=5, padx=0, pady=0, sticky="nsew")

# Add vertical and horizontal scrollbars to the output_text
scrollbar_y = tk.Scrollbar(execution_frame, orient='vertical', command=output_text.yview)
scrollbar_y.grid(row=6, column=5, sticky='ns')
scrollbar_x = tk.Scrollbar(execution_frame, orient='horizontal', command=output_text.xview)
scrollbar_x.grid(row=7, column=0, columnspan=5, sticky='ew')
output_text['yscrollcommand'] = scrollbar_y.set
output_text['xscrollcommand'] = scrollbar_x.set

# Button to update interfaces
update_interfaces_button = tk.Button(execution_frame, text="Update Interfaces", command=update_interfaces)
update_interfaces_button.grid(row=4, column=3, padx=10, pady=5, sticky=tk.W)

# Adjust column weights to ensure the text box expands properly
execution_frame.grid_columnconfigure(0, weight=1)
execution_frame.grid_columnconfigure(1, weight=1)
execution_frame.grid_columnconfigure(2, weight=1)
execution_frame.grid_columnconfigure(3, weight=1)
execution_frame.grid_columnconfigure(4, weight=1)
execution_frame.grid_rowconfigure(6, weight=1)

# Create the subnetting tab
subnetting_frame = tk.Frame(notebook)
notebook.add(subnetting_frame, text="Subnetting")

# Subnetting tab content
tk.Label(subnetting_frame, text="IP Address:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
ip_entry = tk.Entry(subnetting_frame)
ip_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

tk.Label(subnetting_frame, text="Subnet Mask:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
subnet_mask_entry = tk.Entry(subnetting_frame)
subnet_mask_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

tk.Label(subnetting_frame, text="No. of Hosts Needed:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
nhosts_entry = tk.Entry(subnetting_frame)
nhosts_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

# Button frame for the subnetting tab
button_frame_subnetting = tk.Frame(subnetting_frame)
button_frame_subnetting.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

# Calculate buttons
show_range_button = tk.Button(button_frame_subnetting, text="Show Range", command=show_range, bg="lightblue")
show_range_button.pack(side=tk.LEFT, padx=5)

calculate_button = tk.Button(button_frame_subnetting, text="Show NwAd", command=calculate_network_address, bg="lightgreen")
calculate_button.pack(side=tk.LEFT, padx=5)

show_subnet_mask_button = tk.Button(button_frame_subnetting, text="Show Subnet Mask", command=show_subnet_mask, bg="lightcoral")
show_subnet_mask_button.pack(side=tk.LEFT, padx=5)

# Result text box
result_text = tk.Text(subnetting_frame, width=80, height=10, wrap='none', borderwidth=0, relief="flat")
result_text.grid(row=4, column=0, columnspan=5, padx=10, pady=(5, 5), sticky="nsew")

# Create the watchdog tab
watchdog_frame = tk.Frame(notebook)
notebook.add(watchdog_frame, text="Watchdog")

# Watchdog tab content
tk.Label(watchdog_frame, text="Host:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
watchdog_host_entry = tk.Entry(watchdog_frame)
watchdog_host_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

tk.Label(watchdog_frame, text="Username:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
watchdog_username_entry = tk.Entry(watchdog_frame)
watchdog_username_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

tk.Label(watchdog_frame, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
watchdog_password_entry = tk.Entry(watchdog_frame, show='*')
watchdog_password_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

tk.Label(watchdog_frame, text="Secret:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
watchdog_secret_entry = tk.Entry(watchdog_frame, show='*')
watchdog_secret_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

watchdog_button_frame = tk.Frame(watchdog_frame)
watchdog_button_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

watchdog_connect_button = tk.Button(watchdog_button_frame, text="Connect", command=connect_watchdog, bg="red")
watchdog_connect_button.pack(side=tk.LEFT, padx=5)

watchdog_disconnect_button = tk.Button(watchdog_button_frame, text="Disconnect", command=disconnect_watchdog, bg="yellow", state=tk.DISABLED)
watchdog_disconnect_button.pack(side=tk.LEFT, padx=5)

watchdog_clear_button = tk.Button(watchdog_button_frame, text="Clear", command=clear_watchdog_output, bg="lightblue")
watchdog_clear_button.pack(side=tk.LEFT, padx=5)

watchdog_traffic_button = tk.Button(watchdog_button_frame, text="Traffic", command=lambda: threading.Thread(target=traffic_monitor, daemon=True).start(), bg="lightgreen")
watchdog_traffic_button.pack(side=tk.LEFT, padx=5)

watchdog_connection_status = tk.Label(watchdog_frame, text="Not Connected", fg="red")
watchdog_connection_status.grid(row=4, column=2, padx=10, pady=5, sticky=tk.W)

# Watchdog output text box
watchdog_output_text = tk.Text(watchdog_frame, width=80, height=20, wrap='none', borderwidth=1, relief="solid")
watchdog_output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Variables to store the previous port status
previous_status = {}

# Start the Tkinter main loop
root.mainloop()
