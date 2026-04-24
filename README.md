# aiProject
our AI project rah

To run the app in dev:

First, start the backend server.

1. From the root directory, cd backend

2. Create preferred python virtual env and run pip install -r requirements.txt to install dependences

3. Run fastpi dev to start the backend server

Next, start the front end server.

1. From the root directory, cd frontend

2. Run npm run dev to start the frontend server

3. Click on the localhost link provided


====================================================
INSTALL OLLAMA ON RIVANNA
====================================================

--- TERMINAL 1: Install & Start the Server ---

# Step 1: Create directory
cd ~
mkdir ollama
cd ollama

# Step 2: Download Ollama
wget https://ollama.com/download/ollama-linux-amd64.tar.zst

# Step 3: Extract
unzstd ollama-linux-amd64.tar.zst
tar -xvf ollama-linux-amd64.tar

# Step 4: Start the server
cd ~/ollama/bin
./ollama serve

# Will default to port 11434. If it is occupied, use a custom port (choose one between 1024-49151):
OLLAMA_HOST=127.0.0.1:10086 ./ollama serve

# Keep this terminal open. You should see 200 responses
# once requests are being processed.

====================================================

--- TERMINAL 2: Pull Model & Build Vector DB ---

# Step 5: Pull the embedding model
cd ~/ollama/bin
./ollama pull nomic-embed-text

# If using a custom port OPTIONAL:
OLLAMA_HOST=127.0.0.1:10086 ./ollama pull nomic-embed-text

# Step 6: Run the vector DB script
python create_vector_db.py

# If using a custom port OPTIONAL:
OLLAMA_HOST=127.0.0.1:10086 python create_vector_db.py

# Switch back to Terminal 1 — you should see 200 HTTP
# responses confirming successful embedding requests.

