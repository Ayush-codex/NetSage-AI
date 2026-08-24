from checker import run_checks


show_output = """
R1# show ip route

C    192.168.10.0/24 is directly connected
C    192.168.20.0/24 is directly connected
"""


result = run_checks(
    show_output,
    required_network="192.168.20.0/24"
)

print(result)