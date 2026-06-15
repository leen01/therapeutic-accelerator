import cudf

file_path = 'data/fulltext-zipped/20240426_112600_00075_xski5_0a1cf703-227b-490a-9f3a-31e0bc8d873c.json.gz'

chunk_count = 10
chunk_size = 10000


data = []
for x in range(chunk_count): 
    d = cudf.read_json(
        file_path, 
        byte_range=(chunk_size * x, chunk_size)
    )
    data.append(d)
    
df = cudf.concat(data)