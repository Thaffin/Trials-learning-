OSError: Can't load the model for 'sentence-transformers/all-MiniLM-L6-v2'. If you were trying to load it from 'https://huggingface.co/models', make sure you don't have a local directory with the same name. Otherwise, make sure 'sentence-transformers/all-MiniLM-L6-v2' is the correct path to a directory containing a file named pytorch_model.bin.
2026-10-23 17:58:21,471 | INFO | Embedding pipeline started.
2026-10-23 17:58:21,472 | INFO | Input file: C:\Users\2000211016\Documents\lawbot2\data\chunked\indian_law_chunks.json
2026-10-23 17:58:21,472 | INFO | Selected model: sentence-transformers/all-MiniLM-L6-v2
2026-10-23 17:58:21,523 | INFO | Loaded 14524 chunks.
2026-10-23 17:58:21,525 | INFO | No device provided, using cpu
2026-10-23 17:58:22,013 | INFO | HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2 "HTTP/1.1 200 OK"
2026-10-23 17:58:22,036 | INFO | Loading SentenceTransformer model from sentence-transformers/all-MiniLM-L6-v2.
2026-10-23 17:58:22,423 | INFO | HTTP Request: HEAD https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/model.safetensors "HTTP/1.1 302 Found"
2026-10-23 17:58:22,424 | WARNING | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
2026-10-23 17:58:23,140 | INFO | HTTP Request: GET https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2/xet-read-token/1110a243fdf4706b3f48f1d95db1a4f5529b4d41 "HTTP/1.1 200 OK"
