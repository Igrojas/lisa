# darknet

git clone https://github.com/pjreddie/darknet --depth 1
cd darknet
make -j 4
cd ..

cd data/vision
wget "https://pjreddie.com/media/files/densenet201.weights" -nc
wget "https://pjreddie.com/media/files/yolo.weights" -nc
cd -

# spanish pre-trained model

wget "https://github.com/neuromancer/lisa/releases/download/v0.1/spanish.tar.xz"
tar -xf spanish.tar.xz
rm -f spanish.tar.xz
