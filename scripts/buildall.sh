#! /bin/bash

python sitegen.py
python render.py -nv
python render.py -thesis
python python-sitemap-generator/python-sitemap-generator.py "https://focloir-riomheolaiochta.github.io/" focloir
python python-sitemap-generator/python-sitemap-generator.py "https://jeffrey-sardina.github.io/" jeffrey

