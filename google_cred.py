import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

json_content = os.environ["GOOGLE_CRED"]
temp_file = tempfile.NamedTemporaryFile(suffix=".json")
with open(temp_file, "w") as f:
    f.write(json_content)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file.name
