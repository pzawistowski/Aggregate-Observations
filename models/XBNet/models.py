from typing import Dict
import torch
import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from collections import OrderedDict
from models.XBNet.Seq import Seq
from data.data_utils import observation_subset_for
from data.dataset import Dataset


class XBNETClassifier(torch.nn.Module):
    '''
    XBNetClassifier is a model for classification tasks that tries to combine tree-based models with
    neural networks to create a robust architecture.
         :param X_values(numpy array): Features on which model has to be trained
         :param y_values(numpy array): Labels of the features i.e target variable
         :param num_layers(int): Number of layers in the neural network
         :param num_layers_boosted(int,optional): Number of layers to be boosted in the neural network. Default value: 1
    '''

    def __init__(self, dataset: Dataset, layers_raw: list[dict], num_layers_boosted=3):
        super(XBNETClassifier, self).__init__()
        self.name = "Classification"
        self.layers = OrderedDict()
        self.boosted_layers = {}
        self.num_layers_boosted = num_layers_boosted
        self.layers_raw = layers_raw

        self.X = observation_subset_for(data=dataset.data_x, dataset=dataset)
        self.y = observation_subset_for(data=dataset.data_y, dataset=dataset)
        self.prepare_model(dataset)
        self.base_tree()

        self.layers[str(0)].weight = torch.nn.Parameter(
            torch.from_numpy(self.temp.T))

        self.xg = XGBClassifier()

        self.sequential = Seq(self.layers)
        self.sequential.give(self.xg, self.num_layers_boosted)
        self.feature_importances_ = None

    def get(self, l):
        '''
        Gets the set of current actual outputs of the inputs
        :param l(tensor): Labels of the current set of inputs that are getting processed.
        '''
        self.l = l

    def prepare_model(self, dataset):
        self.input_nodes = len(dataset.data_x[0])
        self.output_nodes = len(dataset.data_y[0])
        print(f"input_nodes: {self.input_nodes}")
        print(f"output_nodes: {self.output_nodes}")
        layers = []
        for index, layer in enumerate(self.layers_raw):
            currlayer = layer
            prevlayer = self.layers_raw[index - 1]
            if not index:
                layers.append(torch.nn.Linear(
                    self.input_nodes, currlayer['nodes'], bias=currlayer['bias']))
            else:
                layers.append(torch.nn.Linear(
                    prevlayer['nodes'], currlayer['nodes'], bias=currlayer['bias']))
            if currlayer['nlin']:
                layers.append(currlayer['nlin'])
            if currlayer['norm']:
                layers.append(torch.nn.BatchNorm1d(currlayer['nodes']))
            if currlayer['drop']:
                layers.append(torch.nn.Dropout(0.2))
        layers.append(torch.nn.Linear(
            self.layers_raw[len(self.layers_raw) - 1]['nodes'], self.output_nodes, bias=True))
        for index, layer in enumerate(layers):
            self.layers[str(index)] = layer
        self.layers[str(len(layers))] = torch.nn.Softmax(dim=1)

    def base_tree(self):
        '''
        Instantiates and trains a XGBRegressor on the first layer of the neural network to set its feature importances
         as the weights of the layer
        '''
        self.temp1 = XGBClassifier().fit(self.X, self.y).feature_importances_
        self.temp = self.temp1
        for i in range(1, self.layers_raw[0]['nodes']):
            self.temp = np.column_stack((self.temp, self.temp1))

    def forward(self, x, train=True):
        x = self.sequential(x, self.l, train)
        return x

    def save(self, path):
        '''
        Saves the entire model in the provided path
        :param path(string): Path where model should be saved
        '''
        torch.save(self, path)


class XBNETRegressor(torch.nn.Module):
    '''
    XBNETRegressor is a model for regression tasks that tries to combine tree-based models with
    neural networks to create a robust architecture.
         :param X_values(numpy array): Features on which model has to be trained
         :param y_values(numpy array): Labels of the features i.e target variable
         :param num_layers(int): Number of layers in the neural network
         :param num_layers_boosted(int,optional): Number of layers to be boosted in the neural network. Default value: 1
    '''

    def __init__(self, dataset: Dataset, layers_raw: list[dict], num_layers_boosted=1):
        super(XBNETRegressor, self).__init__()
        self.name = "Regression"
        self.layers = OrderedDict()
        self.boosted_layers = {}
        self.num_layers_boosted = num_layers_boosted
        self.layers_raw = layers_raw

        self.X = observation_subset_for(data=dataset.data_x, dataset=dataset)
        self.y = observation_subset_for(data=dataset.data_y, dataset=dataset)
        self.prepare_model(dataset)
        self.base_tree()

        self.layers[str(0)].weight = torch.nn.Parameter(
            torch.from_numpy(self.temp.T))

        self.xg = XGBRegressor()

        self.sequential = Seq(self.layers)
        self.sequential.give(self.xg, self.num_layers_boosted)
        self.sigmoid = torch.nn.Sigmoid()
        self.feature_importances_ = None

    def get(self, l):
        '''
        Gets the set of current actual outputs of the inputs
        :param l(tensor): Labels of the current set of inputs that are getting processed.
        '''
        self.l = l

    def prepare_model(self, dataset):
        self.input_nodes = len(dataset.data_x[0])
        self.output_nodes = len(dataset.data_y[0])
        print(f"input_nodes: {self.input_nodes}")
        print(f"output_nodes: {self.output_nodes}")
        layers = []
        for index, layer in enumerate(self.layers_raw):
            currlayer = layer
            prevlayer = self.layers_raw[index - 1]
            if not index:
                layers.append(torch.nn.Linear(
                    self.input_nodes, currlayer['nodes'], bias=currlayer['bias']))
            else:
                layers.append(torch.nn.Linear(
                    prevlayer['nodes'], currlayer['nodes'], bias=currlayer['bias']))
            if currlayer['nlin']:
                layers.append(currlayer['nlin'])
            if currlayer['norm']:
                layers.append(torch.nn.BatchNorm1d(currlayer['nodes']))
            if currlayer['drop']:
                layers.append(torch.nn.Dropout(0.2))
        layers.append(torch.nn.Linear(
            self.layers_raw[len(self.layers_raw) - 1]['nodes'], self.output_nodes, bias=True))
        for index, layer in enumerate(layers):
            self.layers[str(index)] = layer
        self.layers[str(len(layers))] = torch.nn.Softmax(dim=1)

    def base_tree(self):
        '''
        Instantiates and trains a XGBRegressor on the first layer of the neural network to set its feature importances
         as the weights of the layer
        '''
        self.temp1 = XGBRegressor().fit(self.X, self.y).feature_importances_
        self.temp = self.temp1
        for i in range(1, self.layers_raw[0]['nodes']):
            self.temp = np.column_stack((self.temp, self.temp1))

    def forward(self, x, train=True):
        x = self.sequential(x, self.l, train)
        return x

    def save(self, path):
        '''
        Saves the entire model in the provided path
        :param path(string): Path where model should be saved
        '''
        torch.save(self, path)
