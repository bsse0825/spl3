import sys
MAX_EPOCH_TRAIN = 150
BATCH_SIZE_TRAIN = 64
MAX_EPOCH_DEBUG = 2
BATCH_SIZE_DEBUG = 64
#MODEL_PATH = "./training_checkpoints"
training_dataset_path = "newData.txt"


def envionmrnt_mode(mode):
    if mode == 'RELEASE':
        return {"EPOCH": MAX_EPOCH_TRAIN, "BATCH": BATCH_SIZE_TRAIN, "MODEL_PATH": "/etc/training_checkpoints_1", "training_dataset_path": training_dataset_path}
    else:
        return {"EPOCH": MAX_EPOCH_DEBUG, "BATCH": BATCH_SIZE_DEBUG, "MODEL_PATH": "/etc/debug_checkpoints_1", "training_dataset_path": training_dataset_path}


'''
if sys.argv[1] == "RELEASE":
    if len(sys.argv)==4:
        MAX_EPOCH_TRAIN = sys.argv[2]
        BATCH_SIZE_TRAIN = sys.argv[3]
else:
        if len(sys.argv)==4:
        MAX_EPOCH_DEBUG = sys.argv[2]
        BATCH_SIZE_DEBUG = sys.argv[3]
'''
