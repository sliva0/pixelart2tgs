from pathlib import Path
import json, gzip

name = Path(__file__).parent / 'example'

with open(name.with_suffix(".json"), encoding='utf-8') as json_file:
    with gzip.open(name.with_suffix(".tgs"), 'wb', compresslevel=9) as out:

        compressed_json = json.dumps(
            json.load(json_file),
            ensure_ascii=False,
            separators=(',', ':'),
        )

        out.write(compressed_json.encode('utf-8'))
