# darknet

git clone https://github.com/pjreddie/darknet --depth 1
cd darknet
make -j 4
cd ..

cd data/vision
wget "https://pjreddie.com/media/files/densenet201.weights" -nc
wget "https://pjreddie.com/media/files/yolo.weights" -nc
