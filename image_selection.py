import glob
from pathlib import Path
import random


class ImageSelection:

  def __init__(self):
    self.data_path = "data/image_data_store"

  def reset(self, semantic_predicate):
    self.start_thresh = 0.0
    self.end_thresh = 1.0

  def update_user_feedback(self):
    pass

  def get_next_image(self):
    imageDataDir = Path(self.data_path)
    imageDataFiles = [str(f) for f in list(imageDataDir.glob('**/*.jpg'))]
    return imageDataFiles[random.randint(0, len(imageDataFiles) - 1)]
