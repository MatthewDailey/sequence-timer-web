source .venv-timer-3.10/bin/activate

# TODO: look at git for all files with changes in public and run this logic

python generate_audio.py -s $1

git add .
git commit -m "Add audio {$1}"
git push

firebase deploy