# coverage.py
import subprocess

commands = [
    ["coverage", "erase"],
    ["coverage", "run", "--source=tamu_id_minter", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
    ["coverage", "report"],
    ["coverage", "html"],
]

for cmd in commands:
    subprocess.run(cmd, check=True)
