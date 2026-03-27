#!/usr/bin/env python3
"""End-to-end test: remember a memory item and verify it syncs to LM Studio."""
import sys
import json
from pathlib import Path

sys.path.insert(0, "src")

import importlib.util, types

# Import instruction_manager directly to bypass __init__.py (which needs tiktoken)
spec = importlib.util.spec_from_file_location(
    "mode_manager_mcp.instruction_manager",
    "src/mode_manager_mcp/instruction_manager.py",
    submodule_search_locations=[]
)
# We need a minimal package stub so relative imports resolve
pkg = types.ModuleType("mode_manager_mcp")
pkg.__path__ = ["src/mode_manager_mcp"]
pkg.__package__ = "mode_manager_mcp"
sys.modules["mode_manager_mcp"] = pkg

# Import path_utils first
import importlib.util as ilu
for mod_name in ["path_utils", "simple_file_ops", "types"]:
    s = ilu.spec_from_file_location(
        f"mode_manager_mcp.{mod_name}",
        f"src/mode_manager_mcp/{mod_name}.py"
    )
    m = ilu.module_from_spec(s)
    sys.modules[f"mode_manager_mcp.{mod_name}"] = m
    s.loader.exec_module(m)

spec = ilu.spec_from_file_location(
    "mode_manager_mcp.instruction_manager",
    "src/mode_manager_mcp/instruction_manager.py"
)
im_module = ilu.module_from_spec(spec)
sys.modules["mode_manager_mcp.instruction_manager"] = im_module
spec.loader.exec_module(im_module)

InstructionManager = im_module.InstructionManager
MemoryScope = sys.modules["mode_manager_mcp.types"].MemoryScope

manager = InstructionManager()

print("=== Testing LM Studio sync ===\n")

# Show LM Studio paths
lmstudio_dir = Path.home() / ".lmstudio"
memories_dir = lmstudio_dir / "memories"
config_path  = lmstudio_dir / ".internal" / "conversation-config.json"

print(f"LM Studio dir exists: {lmstudio_dir.exists()}")
print(f"Memories dir before: {memories_dir} (exists={memories_dir.exists()})")
print(f"Config path:         {config_path} (exists={config_path.exists()})")

# Save current config so we can restore it
config_backup = None
if config_path.exists():
    config_backup = config_path.read_text(encoding="utf-8")
    print(f"\nCurrent config (relevant part):")
    cfg = json.loads(config_backup)
    fields = cfg.get("globalPredictionConfig", {}).get("fields", [])
    print(f"  globalPredictionConfig.fields: {fields}")

print("\n--- Calling create_memory() ---")
result = manager.create_memory(
    memory_item="Test memory: the sky is blue and LM Studio sync works",
    scope=MemoryScope.user,
)
print(f"Result: {result}")

print("\n--- Checking LM Studio output ---")
print(f"Memories dir after: {memories_dir} (exists={memories_dir.exists()})")
memory_md = memories_dir / "memory.md"
if memory_md.exists():
    print(f"memory.md content:\n{memory_md.read_text()[:400]}")
else:
    print("memory.md NOT created")

if config_path.exists():
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    fields = cfg.get("globalPredictionConfig", {}).get("fields", [])
    print(f"\nconversation-config.json globalPredictionConfig.fields:")
    for f in fields:
        print(f"  key={f.get('key')}")
        if f.get("key") == "llm.prediction.systemPrompt":
            print(f"  value (first 200 chars):\n    {f['value'][:200]}")

print("\nDone.")
