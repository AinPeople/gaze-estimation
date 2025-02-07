import numpy as np

from utils import cut_rois, resize_input
from ie_module import Module


class HeadPoseEstimator(Module):
    POINTS_NUMBER = 35

    def __init__(self, core, model):
        super(HeadPoseEstimator, self).__init__(core, model, 'Head Pose Estimation')

        if len(self.model.inputs) != 1:
            raise RuntimeError("The model expects 1 input layer")
        if len(self.model.outputs) != 1:
            raise RuntimeError("The model expects 1 output layer")

        self.input_tensor_name = self.model.inputs[0].get_any_name()
        self.input_shape = self.model.inputs[0].shape
        self.nchw_layout = self.input_shape[1] == 3
        output_shape = self.model.outputs[0].shape
        if not np.array_equal([1, self.POINTS_NUMBER * 2], output_shape):
            raise RuntimeError("The model expects output shape {}, got {}".format(
                [1, self.POINTS_NUMBER * 2], output_shape))

    def preprocess(self, frame, rois):
        inputs = cut_rois(frame, rois)
        inputs = [resize_input(input, self.input_shape, self.nchw_layout) for input in inputs]
        return inputs

    def enqueue(self, input):
        return super(HeadPoseEstimator, self).enqueue({self.input_tensor_name: input})

    def start_async(self, frame, rois):
        inputs = self.preprocess(frame, rois)
        for input in inputs:
            self.enqueue(input)

    def postprocess(self):
        # outputs shape is [1, self.POINTS_NUMBER * 2]
        #results = [out.reshape((-1, 2)).astype(np.float64) for out in self.get_outputs()]
        results = [out for out in self.get_outputs()]
        #results = [print(out) for out in self.get_outputs()]
        print(results)
        #exit()
        return results