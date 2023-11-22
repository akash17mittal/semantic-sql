import pandas as pd
from text_to_image_semantic_search import TextToImageSemanticSearcher


class ImageSelection:

  def __init__(self, filtered_df: pd.DataFrame, semantic_predicate: str):
    self.filtered_df = filtered_df
    self.searcher = TextToImageSemanticSearcher(index_path='data/index', ids_path="data/index_ids.npy")
    image_ids, scores = self.searcher.generate_all_image_scores(semantic_predicate)
    image_scores = pd.DataFrame({"id": image_ids, "score": scores})
    self.image_scores = image_scores.loc[image_scores["id"].isin(set(self.filtered_df["id"].values))].sort_values(
      by="score", ascending=False)
    self.satisfied_ids = pd.DataFrame()
    self.curr_image = 0

  def update_user_feedback(self, passes_criterion):
    print("Total Images to Decide - ", len(self.image_scores))
    print("Total Satisfied - ", len(self.satisfied_ids))
    print("*" * 15)
    if passes_criterion:
      self.satisfied_ids = pd.concat([self.satisfied_ids, self.image_scores.iloc[self.curr_image_index:]])
      self.image_scores = self.image_scores.iloc[:self.curr_image_index]
    else:
      self.image_scores = self.image_scores.iloc[self.curr_image_index:]
    print("Total Images to Decide - ", len(self.image_scores))
    print("Total Satisfied - ", len(self.satisfied_ids))

  def _get_image_path_from_id(self, id):
    return self.searcher.get_images_from_ids([int(id)])[0]

  def get_next_image(self):
    self.curr_image_index = int(self.image_scores.shape[0] * 0.5)
    image_to_choose = self.image_scores.iloc[self.curr_image_index]["id"]
    return self._get_image_path_from_id(image_to_choose)
