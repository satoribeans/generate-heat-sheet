import re

def safe_text(text):
  if not text:
        return ""

  replacements = { "★": "*", "–": "-", "—": "-", "'": "'", """: '"', """: '"' } 
  for k, v in replacements.items(): text = text.replace(k, v)  
  
  return text.encode("latin-1", "ignore").decode("latin-1")


def time_to_seconds(t):
  if not t or t == "NT":
    return 9999
  try:
    if ":" in t:
      m, s = t.split(":")
      return int(m) * 60 + float(s)
    return float(t)
  except:
    return 9999


def clean_line(line):
    return (
        line.replace("Butter7ly", "Butterfly")
            .replace("Butterﬂy", "Butterfly")
            .replace("CrutchEield", "Crutchfield")
            .replace("Crutchﬁeld", "Crutchfield")
            .replace("-NC", "")
            .strip()
    )


def is_long_event(name):
    name = name.lower()
    return any(x in name for x in ["400", "500", "800", "1500"])
