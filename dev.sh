#!/bin/sh
# Démarre le serveur de développement Hugo en partant d'un état propre.
rm -rf public resources
hugo server --disableFastRender --buildDrafts
