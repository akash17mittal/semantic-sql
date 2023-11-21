import numpy as np
import pickle
import faiss
from PIL import Image
import requests
import pandas as pd
from transformers import CLIPProcessor, CLIPModel
import matplotlib.pyplot as plt
from transformers import AutoTokenizer
import os
import torch
import requests
from io import BytesIO



def create_and_save_faiss_index_with_ids(embeddings_path, ids_path, use_gpu=False, index_path="index", ids_save_path="index_ids.npy"):
    """
    Create a FAISS index and add the embeddings from a dictionary to it, 
    keeping track of the ids.

    Parameters:
    - embedding_dict (dict): A dictionary where keys are ids and values are embeddings
    - use_gpu (bool): Whether to use GPU or not

    Returns:
    - faiss index object with embeddings added
    - id mapping list, mapping index positions in FAISS to ids
    """

    # load ids and embeddings from .pt files embeddings_path and ids_path
    embeddings = torch.load(embeddings_path).cpu().numpy()
    ids = torch.load(ids_path).cpu().numpy()

    # Number of dimensions
    d = embeddings.shape[1]

    # Normalize the embeddings
    faiss.normalize_L2(embeddings)

    # Create the index object
    index = faiss.IndexFlatL2(d)

    # If GPU usage is desired, convert the index to a GPU index
    if use_gpu:
        res = faiss.StandardGpuResources()
        index = faiss.index_cpu_to_gpu(res, 0, index)

    # Add embeddings to the index
    index.add(embeddings)
    # save the ids and the index
    faiss.write_index(index, index_path)
    np.save(ids_save_path, ids)

    # return index, ids

def save_ids_and_index(index, ids, index_path):
    """
    Save the ids and the index to disk.

    Parameters:
    - index: FAISS index object
    - ids: List of ids corresponding to the embeddings in the index
    - index_path: Path to save the index to
    """
    # Convert the ids to a numpy array
    ids = np.array(ids)
    # Save the ids and the index to disk
    faiss.write_index(index, index_path)
    np.save(index_path + "_ids", ids)

class TextToImageSemanticSearcher:
    def __init__(self, index_path='index', ids_path="index_ids.npy"):
        if not os.path.exists(index_path):
            raise ValueError("Index path does not exist!")
        self.index = faiss.read_index(index_path)
        self.ids = np.load(ids_path)

        self.tokenizer = AutoTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

        self.total_num_entries = self.index.ntotal

    def generate_query_embedding(self, query):
        inputs = self.tokenizer([query], padding=True, return_tensors="pt")
        text_features = self.model.get_text_features(**inputs)
        query_embedding = text_features.detach().numpy()  
        return query_embedding

    # generates the scores for all images in the index. returns all the image ids and the corresponding scores
    def generate_all_image_scores(self, query):
        query_embedding = self.generate_query_embedding(query)
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, self.total_num_entries)
        distances = distances.flatten()
        indices = indices.flatten()
        image_ids = [self.ids[idx] for idx in indices]
        return image_ids, distances
    
    def find_images_above_threshold(self, query, score_threshold):
        image_ids, scores = self.generate_all_image_scores(query)
        above_threshold = np.where(scores > score_threshold)
        return image_ids[above_threshold]
    
    def find_images_above_percentile(self, query, percentile):
        image_ids, scores = self.generate_all_image_scores(query)
        score_threshold = np.percentile(scores, percentile*100)
        above_threshold = np.where(scores > score_threshold)
        return image_ids[above_threshold]
    
    def sample_images_at_percentile(self, query, percentile=1, k=1):
        """
        Retrieves k sample images around the specified percentile from an embedding space.
        
        :param index: FAISS index containing the image embeddings.
        :param query: Embedding of the query image.
        :param percentile: The percentile (between 0 and 100) around which to sample images.
        :param k: The number of images to sample.
        :return: k images ids of the sampled images at that percentile.
        """
        # Normalize the query
        image_ids, _ = self.generate_all_image_scores(query)

        # Calculate the target index for the specified percentile
        target_index = int((1 - percentile) * self.total_num_entries)

        # Determine start and end indices for sampling
        start_index = max(0, target_index - k // 2)
        end_index = min(self.total_num_entries, start_index + k)

        # Adjust start_index if end_index exceeds total_num_entries
        if end_index == self.total_num_entries:
            start_index = max(0, end_index - k)

        # Sample k indices around the specified percentile
        sampled_image_ids = image_ids[start_index:end_index]

        # get the actual image ids from the sampled indices
        return sampled_image_ids

    def get_image(self, image_id, data_dir, index_size=12):
        # we need to append zeros to the image_id so it is equal to index_size
        image_id = str(image_id).zfill(index_size)
        # get the image path
        image_path = os.path.join(data_dir, "train2017", f"{image_id}.jpg")
        image = Image.open(image_path)
        return image
    
    
    def plot_images(self, images):
        # create a figure with subplots
        fig, axes = plt.subplots(nrows=1, ncols=len(images), figsize=(20, 20))
        # plot each image on its corresponding subplot
        for img, ax in zip(images, axes):
            ax.imshow(img)
            ax.axis("off")
        plt.show()

    # gets images corresponding to image ids using the COCO API
    def get_images_from_ids(self, image_ids, index_size=12):
        # we need to append zeros to the image_id so it is equal to index_size
        images = []
        for image_id in image_ids:
            image_id = str(image_id).zfill(index_size)
            # get the image path
            image_path = f'http://images.cocodataset.org/train2017/{image_id}.jpg'
            image = Image.open(BytesIO(requests.get(image_path).content))
            images.append(image)
        return images
    
    # plots the images in a grid
    def plot_images(self, images):
        # create a figure with subplots
        fig, axes = plt.subplots(nrows=1, ncols=len(images), figsize=(20, 20))
        # plot each image on its corresponding subplot
        for img, ax in zip(images, axes):
            ax.imshow(img)
            ax.axis("off")
        return plt 

