source .venv-timer-3.10/bin/activate

python generate_audio.py -s $1

git add .
git commit -m "Add audio {$1}"
git push

firebase deploy