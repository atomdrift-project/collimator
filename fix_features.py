import re

with open("src/collimator/features.py") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.strip()
    # Skip the definition
    if stripped.startswith("def _safe_assign"):
        new_lines.append(line)
        continue
    
    if "_safe_assign" in stripped:
        # If it doesn't end with a closing paren, add one.
        if not stripped.endswith(")"):
            # Count opening and closing parens to be safe
            open_p = stripped.count("(")
            close_p = stripped.count(")")
            if open_p > close_p:
                line = line.rstrip() + ")" * (open_p - close_p) + "\n"
    
    new_lines.append(line)

with open("src/collimator/features.py", "w") as f:
    f.writelines(new_lines)
