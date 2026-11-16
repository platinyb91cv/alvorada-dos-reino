# $1 entrada $2 saída $3 variante
case $3 in
 conselheiro) F="asetrate=22050*0.88,aresample=44100,atempo=1.0227,equalizer=f=140:t=q:w=1:g=4,equalizer=f=3200:t=q:w=1.2:g=2,aecho=0.8:0.6:38|74:0.18|0.10,loudnorm=I=-16:TP=-1.5";;
 arauto)      F="asetrate=22050*0.84,aresample=44100,atempo=1.0,equalizer=f=120:t=q:w=1:g=5,equalizer=f=2500:t=q:w=1:g=2,aecho=0.8:0.7:60|130|210:0.30|0.20|0.12,loudnorm=I=-16:TP=-1.5";;
 rei)         F="asetrate=22050*0.80,aresample=44100,atempo=1.08,equalizer=f=100:t=q:w=1:g=6,lowpass=f=7000,aecho=0.8:0.75:90|180|300:0.32|0.22|0.14,loudnorm=I=-16:TP=-1.5";;
esac
ffmpeg -loglevel error -y -i "$1" -af "apad=pad_dur=0.6,$F" -ar 24000 -ac 1 -b:a 48k "$2"
