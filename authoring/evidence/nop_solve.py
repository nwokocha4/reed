"""Empty program for the Nop leg of the evidence. Exits zero but writes no
compliance tables, so the verifier must reward 0."""
import os

os.makedirs(os.path.join(os.environ.get("LCR_BASE", "/app"), "output"),
            exist_ok=True)
