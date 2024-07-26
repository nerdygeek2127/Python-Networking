# Cisco IOS Device Management GUI

This project is a graphical user interface (GUI) application built using Tkinter, designed to manage Cisco IOS devices through network commands. The application allows users to execute various network commands, monitor device interfaces, calculate subnetting details, and maintain saved connection details.

## Features

### Main Interface
- **Connection Details**:
  - **Host**: IP address or hostname of the Cisco device.
  - **Username**: Username for device login.
  - **Password**: Password for device login.
  - **Secret**: Enable secret for privileged EXEC mode.

- **Command Execution**:
  - **Command Type**: Dropdown menu to select commands like `show ip interface brief`, `show vlan`, `show running-config`, `show interfaces`, etc.
  - **Interface Selection**: Dropdown to select specific interfaces for interface-related commands.
  - **Execute Button**: Executes the selected command on the device and displays the output.
  - **Disconnect Button**: Disconnects from the device.
  - **Clear Button**: Clears the command output.
  - **Reboot Button**: Reboots the device.
  - **Download Button**: Downloads the command output to a file.

- **Connection Management**:
  - **Load and Save Buttons**: Load and save connection details.
  - **Connection Status**: Displays the current connection status.
  - **Update Interfaces Button**: Updates the list of interfaces on the device.

### Subnetting Tab
- **Subnetting Calculations**:
  - **IP Address, Subnet Mask, No. of Hosts Needed**: Fields to enter subnetting details.
  - **Show Range Button**: Displays the network range based on the number of hosts needed.
  - **Show NwAd Button**: Calculates and displays the network address and other details.
  - **Show Subnet Mask Button**: Displays the subnet mask for a given prefix length.
  - **Result Text Box**: Displays the subnetting results.

### Watchdog Tab
- **Device Monitoring**:
  - **Host, Username, Password, Secret**: Fields to enter the connection details for the Cisco device to be monitored.
  - **Connect Button**: Connects to the device and starts monitoring.
  - **Disconnect Button**: Disconnects from the device.
  - **Clear Button**: Clears the monitoring output.
  - **Traffic Button**: Monitors and displays traffic details.
  - **Connection Status**: Displays the current connection status.
  - **Watchdog Output Text Box**: Displays the monitoring output.

## Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/nerdygeek2127/Python-Networking.git
    cd cisco-ios-management-gui
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    ```sh
    python "command Executor.py"
    ```

## Dependencies

- `tkinter`: For building the GUI.
- `netmiko`: For connecting and executing commands on Cisco devices.
- `datetime`, `os`, `json`, `ipaddress`, `threading`, `time`: Standard libraries for various functionalities.
- `Pillow`: For image handling (if needed).

## Usage

1. **Main Interface**:
   - Enter the connection details (Host, Username, Password, Secret).
   - Select a command type and interface (if required).
   - Click "Execute" to run the command and see the output.
   - Use "Disconnect" to terminate the connection.
   - Click "Clear" to clear the output.
   - Use "Reboot" to reboot the device (requires confirmation).
   - Click "Download" to save the output to a file.
   - Use "Load" to load saved connection details and "Save" to save current details.
   - Click "Update Interfaces" to refresh the list of interfaces.

2. **Subnetting Tab**:
   - Enter IP Address, Subnet Mask, and Number of Hosts Needed.
   - Use "Show Range" to display the network range.
   - Click "Show NwAd" to calculate and display network address details.
   - Use "Show Subnet Mask" to display the subnet mask for a given prefix length.

3. **Watchdog Tab**:
   - Enter the connection details (Host, Username, Password, Secret).
   - Click "Connect" to start monitoring the device.
   - Use "Disconnect" to terminate the monitoring session.
   - Click "Clear" to clear the monitoring output.
   - Use "Traffic" to monitor and display traffic details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) guidelines before submitting a pull request.

## Acknowledgements

Special thanks to the developers of the libraries used in this project.

## Contact

For any questions or issues, please open an issue on GitHub or contact the maintainer.
