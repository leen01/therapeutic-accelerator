#!/user/bin/env bash
jupyter notebook --NotebookApp.allow_origin='https://colab.research.google.com' --port=8080   --NotebookApp.port_retries=0  --no-browser
