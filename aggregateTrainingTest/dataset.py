import torch


class Observation:
    def __init__(self, entries_indices: list[int], value_vec_index: int):
        self.length = len(entries_indices)
        self.entries_indices = entries_indices
        self.value_vec_index = value_vec_index


class Dataset:
    def __init__(self, data_x: torch.Tensor, data_y: torch.Tensor, observations: list[Observation]):
        # data_x has shape (entries, features)
        # data_y has shape (aggregate_index, values)
        # observations is a metadata which points aggregate to entries indices
        self.data_x = data_x
        self.data_y = data_y
        self.observations = observations

    def validate(dataset) -> bool:
        if (dataset == None):
            raise ValueError("Model: No dataset provided")
        if (len(dataset.data_x) == 0):
            raise ValueError("Model: No entries in dataset")
        if (len(dataset.data_y) == 0):
            raise ValueError("Model: No values in dataset")
        if (len(dataset.observations) == 0):
            raise ValueError("Model: No observations in dataset")
        return True


Dataset.validate = staticmethod(Dataset.validate)
