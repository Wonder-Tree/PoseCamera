# Training on your own data

## Prerequisites
* Download COCO dataset 2017 [http://cocodataset.org/#download](http://cocodataset.org/#download) (train, val, annotations) and unpack it to <COCO_HOME> directory.
* You can use your dataset but make sure it's in COCO annotations format [more info](https://www.immersivelimit.com/tutorials/create-coco-annotations-from-scratch#:~:text=The%20COCO%20bounding%20box%20format,other%20annotations%20in%20the%20dataset). 
* Install requirements ```pip install -r requirements.txt```
* Download pre-trained MobileNet v1 weights mobilenet_sgd_68.848.pth.tar from: [GoogleDrive](https://drive.google.com/file/d/18Ya27IAhILvBHqV_tDp0QjDFvsNNy-hv/view?usp=sharing)
* Convert train annotations in internal format. Run ```python scripts/prepare_train_labels.py --labels <COCO_HOME>/annotations/person_keypoints_train2017.json```. It will produce ```prepared_train_annotation.pkl``` with converted in internal format annotations.
* Run ```python scripts/make_val_subset.py --labels <COCO_HOME>/annotations/person_keypoints_val2017.json```. It will produce ```val_subset.json``` with annotations just for 250 random images (out of 5000).

## Start Training
Training consists of 3 steps.
1. Training from MobileNet weights.
```sh
python train.py --train-images-folder <COCO_HOME>/train2017/ --prepared-train-labels prepared_train_annotation.pkl --val-labels val_subset.json --val-images-folder <COCO_HOME>/val2017/ --checkpoint-path <path_to>/mobilenet_sgd_68.848.pth.tar --from-mobilenet
```
2. Training from weights, obtained from previous step.
```sh
python train.py --train-images-folder <COCO_HOME>/train2017/ --prepared-train-labels prepared_train_annotation.pkl --val-labels val_subset.json --val-images-folder <COCO_HOME>/val2017/ --checkpoint-path <path_to>/checkpoint_iter_420000.pth --weights-only
```
3. Training from weights, obtained from previous step and increased number of refinement stages to 3 in network.
```sh
python train.py --train-images-folder <COCO_HOME>/train2017/ --prepared-train-labels prepared_train_annotation.pkl --val-labels val_subset.json --val-images-folder <COCO_HOME>/val2017/ --checkpoint-path <path_to>/checkpoint_iter_280000.pth --weights-only --num-refinement-stages 3
```

## Validation
```sh
python val.py --labels <COCO_HOME>/annotations/person_keypoints_val2017.json --images-folder <COCO_HOME>/val2017 --checkpoint-path <CHECKPOINT>
```