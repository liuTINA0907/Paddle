# Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
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

from __future__ import print_function

import numpy as np
import paddle.fluid as fluid

from paddle.fluid import FC
from paddle.fluid.dygraph import FC
from paddle.fluid.dygraph.base import to_variable

import unittest


class Test_Detach(unittest.TestCase):
    def generate_Data(self):
        data = np.array(
            [[1, 8, 3, 9], [7, 20, 9, 6], [4, 6, 8, 10]]).astype('float32')
        return data

    def no_detach_multi(self):
        data = self.generate_Data()
        with fluid.dygraph.guard():
            fc_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(5.0))
            fc_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(6.0))
            fc = FC("fc",
                    10,
                    num_flatten_dims=1,
                    param_attr=fc_w_param_attrs,
                    bias_attr=fc_b_param_attrs)
            fc1_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(7.0))
            fc1_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(8.0))
            fc1 = FC("fc",
                     1,
                     num_flatten_dims=1,
                     param_attr=fc1_w_param_attrs,
                     bias_attr=fc1_b_param_attrs)
            fc2_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(9.0))
            fc2_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(10.0))
            fc2 = FC("fc",
                     1,
                     num_flatten_dims=1,
                     param_attr=fc2_w_param_attrs,
                     bias_attr=fc2_b_param_attrs)
            data = to_variable(data)
            x = fc(data)
            x1 = fc1(x)
            x2 = fc2(x)
            loss = x1 + x2
            # print(loss, loss.shape)
            loss.backward()
            return x.gradient()

    def no_detach_single(self):
        data = self.generate_Data()
        with fluid.dygraph.guard():
            fc_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(5.0))
            fc_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(6.0))
            fc = FC("fc",
                    10,
                    num_flatten_dims=1,
                    param_attr=fc_w_param_attrs,
                    bias_attr=fc_b_param_attrs)
            fc1_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(7.0))
            fc1_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(8.0))
            fc1 = FC("fc",
                     1,
                     num_flatten_dims=1,
                     param_attr=fc1_w_param_attrs,
                     bias_attr=fc1_b_param_attrs)
            data = to_variable(data)
            x = fc(data)
            x1 = fc1(x)
            loss = x1
            # print(loss, loss.shape)
            loss.backward()
            return x.gradient()

    def detach_multi(self):
        data = self.generate_Data()
        with fluid.dygraph.guard():
            fc_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(5.0))
            fc_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(6.0))
            fc = FC("fc",
                    10,
                    num_flatten_dims=1,
                    param_attr=fc_w_param_attrs,
                    bias_attr=fc_b_param_attrs)
            fc1_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(7.0))
            fc1_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(8.0))
            fc1 = FC("fc",
                     1,
                     num_flatten_dims=1,
                     param_attr=fc1_w_param_attrs,
                     bias_attr=fc1_b_param_attrs)
            fc2_w_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(9.0))
            fc2_b_param_attrs = fluid.ParamAttr(
                initializer=fluid.initializer.Constant(10.0))
            fc2 = FC("fc",
                     1,
                     num_flatten_dims=1,
                     param_attr=fc2_w_param_attrs,
                     bias_attr=fc2_b_param_attrs)
            data = to_variable(data)
            x = fc(data)
            x_detach = x.detach()
            x1 = fc1(x)
            x2 = fc2(x_detach)
            loss = x1 + x2
            # print(loss, loss.shape)
            loss.backward()
            return x.gradient()

    def test_NoDetachMulti_DetachMulti(self):
        array_no_detach_multi = self.no_detach_multi()
        array_detach_multi = self.detach_multi()

        assert not np.array_equal(array_no_detach_multi, array_detach_multi)

    def test_NoDetachSingle_DetachMulti(self):
        array_no_detach_single = self.no_detach_single()
        array_detach_multi = self.detach_multi()
        assert np.array_equal(array_no_detach_single, array_detach_multi)

    def test_detach_exception(self):
        x = fluid.layers.data(name="a", shape=[3, 4], dtype='float32')
        y = fluid.layers.fc(input=x, size=10, bias_attr=True)
        try:
            y_detach = y.detach()
        except Exception as e:
            assert type(e) == AttributeError
            assert str(e) == 'static graph model DO NOT supprt detach'


if __name__ == '__main__':
    unittest.main()