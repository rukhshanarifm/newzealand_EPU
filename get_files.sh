#!/bin/sh

echo "Getting data files and creating directories..."

mkdir data

mkdir data/clean

mkdir data/raw

mkdir figures

wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=1eGQAD_YNKRFrpOq1ZgO-HpvPmhSvwm8C' -O data/clean/tvnz_clean_data.pkl

wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=1XqkKgysUvGFCxbdXe2_s7Ck2Fh0r6WY6' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1XqkKgysUvGFCxbdXe2_s7Ck2Fh0r6WY6" -O data/clean/herald_clean_data.pkl && rm -rf /tmp/cookies.txt

wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/uc?export=download&id=185OQD13ayg5uNeYu_u_NS3MfqgLWu6V6' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=185OQD13ayg5uNeYu_u_NS3MfqgLWu6V6" -O data/clean/stuff_clean_data.pkl && rm -rf /tmp/cookies.txt
