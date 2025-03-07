#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This example is adapted from
# https://machinelearningmastery.com/pytorch-tutorial-develop-deep-learning-models/

from torch.nn import Linear
from torch.nn import ReLU
from torch.nn import Sigmoid
from torch.nn import Module
from torch.optim import SGD
from torch.nn import BCELoss
from torch.nn.init import kaiming_uniform_
from torch.nn.init import xavier_uniform_

import bigdl.orca.data.pandas
from bigdl.orca import init_orca_context, stop_orca_context
from bigdl.orca.learn.pytorch import Estimator
from bigdl.orca.learn.metrics import Accuracy
from bigdl.orca.data.transformer import StringIndexer
from bigdl.orca.data.utils import *

class MLP(Module):
    # define model elements
    def __init__(self, n_inputs):
        super(MLP, self).__init__()
        # input to first hidden layer
        self.hidden1 = Linear(n_inputs, 10)
        kaiming_uniform_(self.hidden1.weight, nonlinearity='relu')
        self.act1 = ReLU()
        # second hidden layer
        self.hidden2 = Linear(10, 8)
        kaiming_uniform_(self.hidden2.weight, nonlinearity='relu')
        self.act2 = ReLU()
        # third hidden layer and output
        self.hidden3 = Linear(8, 1)
        xavier_uniform_(self.hidden3.weight)
        self.act3 = Sigmoid()

    # forward propagate input
    def forward(self, X):
        # input to first hidden layer
        X = self.hidden1(X)
        X = self.act1(X)
         # second hidden layer
        X = self.hidden2(X)
        X = self.act2(X)
        # third hidden layer and output
        X = self.hidden3(X)
        X = self.act3(X)
        return X

init_orca_context(memory="4g")

path = 'new_ionosphere.csv'
data_shard = bigdl.orca.data.pandas.read_csv(path)

def getSchema(iter):
    for pdf in iter:
        return [pdf.columns.values]

column = data_shard.rdd.mapPartitions(getSchema).first()

label_encoder = StringIndexer(inputCol=column[-1])
data_shard = label_encoder.fit_transform(data_shard)

model = MLP(34)
criterion = BCELoss()
optimizer = SGD(model.parameters(), lr=0.01, momentum=0.9)

orca_estimator = Estimator.from_torch(model=model,
                                      optimizer=optimizer,
                                      loss=criterion,
                                      metrics=[Accuracy()],
                                      backend="bigdl")

data_shard = transform_to_shard_dict(data_shard,
                                     featureCols=list(column[:-1]),
                                     labelCol=column[-1])

orca_estimator.fit(data=data_shard, epochs=8, batch_size=4)
