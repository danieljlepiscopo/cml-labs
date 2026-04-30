from netmiko import ConnectHandler

R1 = {
        "device_type": "cisco_ios",
        "host": "10.0.0.12",
        "username": "cisco",
        "password": "cisco",
    }

connection = ConnectHandler(**R1)

output = connection.send_command("show ip interface brief")

print("\n--- R1 OUTPUT ---\n")
print(output)

connection.disconnect()
