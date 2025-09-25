import io

input_file = "fresh_dump.sql"
output_file = "cleaned_dump2.sql"

# Open file in binary mode to remove NULL bytes safely
with open(input_file, "rb") as f:
    raw = f.read()

# Remove all NULL bytes
raw = raw.replace(b"\x00", b"")

# Decode cleaned bytes to text
text = raw.decode("utf-8", errors="ignore")

lines = text.splitlines()

cleaned = []
for line in lines:
    if line.startswith("PRAGMA"):
        continue
    if "BEGIN TRANSACTION" in line or "COMMIT" in line:
        continue
    cleaned.append(line.replace("AUTOINCREMENT", ""))

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(cleaned))

print(f"✅ Cleaned dump written to {output_file} with {len(cleaned)} lines (NULL bytes removed).")
