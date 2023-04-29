#!/bin/bash
start=$(date +%s)

python manganelo_scraper.py
python postprocessing.py
python final_post.py

end=$(date +%s)
runtime=$((end-start))

echo "Total time taken: $runtime seconds"
