from data.dataset import Dataset
from itertools import chain
from torch import nn


class Model:
    def __init__(self, classification: bool = False):
        self.output_nodes = None
        self.input_nodes = None
        self.model = None
        self.classification = classification

    def parameters(self):
        return self.model.parameters()

    def get_model_for(self, dataset: Dataset) -> None:
        Dataset.validate(dataset)
        self.input_nodes = len(dataset.data_x[0])
        self.output_nodes = len(dataset.data_y[0])
        self.model = nn.Sequential(
            nn.Linear(self.input_nodes, 128),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(128),
            nn.Dropout(p=0.2),
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.BatchNorm1d(128),
            nn.Dropout(p=0.2),
            nn.Linear(128, self.output_nodes),
        )
        if self.classification is True:
            self.model = nn.Sequential(
                self.model, nn.Softmax(dim=1))

    def test(self, dataset: Dataset):
        data_x_indices = list(
            chain(*[obs.entries_indices for obs in dataset.observations]))
        x = dataset.data_x[data_x_indices]
        return [x, self.model(x)]
