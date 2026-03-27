#!/usr/bin/env python3
"""Fix the corrupted create_memory() return block in instruction_manager.py"""

target = "src/mode_manager_mcp/instruction_manager.py"

with open(target, "r") as f:
    lines = f.readlines()

print(f"Total lines before fix: {len(lines)}")

# Print lines around the broken section
print("\nLines 196-232 before fix:")
for i, line in enumerate(lines[195:232], start=196):
    print(f"  {i:3d}: {repr(line)}")

# The broken section is lines 197-230 (1-indexed), i.e. indices 196-229 (0-indexed)
# Find the exact indices by searching for the start of the broken block
start_idx = None
for i, line in enumerate(lines):
    if i >= 195 and line.strip() == "return {":
        start_idx = i
        print(f"\nFound 'return {{' at 0-indexed line {i} (1-indexed {i+1})")
        break

if start_idx is None:
    print("ERROR: Could not find broken return block")
    exit(1)

# Find the end of all the broken duplicates
# We need to find where the last duplicate ends and the next method begins
end_idx = None
for i in range(start_idx, len(lines)):
    if lines[i].strip().startswith("async def create_memory_with_optimization"):
        end_idx = i
        print(f"Found end of broken section at 0-indexed line {i} (1-indexed {i+1})")
        break

if end_idx is None:
    print("ERROR: Could not find end of broken section")
    exit(1)

print(f"\nWill replace lines {start_idx+1}-{end_idx} (1-indexed) with correct code")

replacement = [
    "        # Mirror memory to LM Studio (no-op if LM Studio not installed)\n",
    "        self._sync_to_lmstudio(file_path)\n",
    "\n",
    "        return {\n",
    '            "status": "success",\n',
    '            "filename": filename,\n',
    '            "scope": scope,\n',
    '            "language": language,\n',
    '            "path": str(file_path),\n',
    '            "apply_to": apply_to_pattern,\n',
    "        }\n",
    "\n",
]

new_lines = lines[:start_idx] + replacement + lines[end_idx:]

print(f"\nTotal lines after fix: {len(new_lines)}")
print("\nNew lines at the replacement zone:")
for i, line in enumerate(new_lines[start_idx:start_idx+14], start=start_idx+1):
    print(f"  {i:3d}: {repr(line)}")

with open(target, "w") as f:
    f.writelines(new_lines)

print("\nFile written successfully.")

# Verify syntax
import ast
with open(target, "r") as f:
    src = f.read()
try:
    ast.parse(src)
    print("Syntax check: OK")
except SyntaxError as e:
    print(f"Syntax check: FAILED - {e}")
