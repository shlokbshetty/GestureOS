"""
Gesture Recognition Model Exporter and Optimizer.

Builds and exports an optimized ONNX model for high-speed (<10ms)
gesture inference on CPU and GPU (DirectML).

Requirements: 1.4, 17.0
"""

import os
from pathlib import Path
import numpy as np
import onnx
from onnx import helper, TensorProto


GESTURE_CLASSES = [
    'app_switch',
    'close_window',
    'nothing',
    'play_pause',
    'screenshot',
    'scroll_down',
    'scroll_up',
    'volume_down',
    'volume_up',
]


def create_onnx_gesture_model(output_path: str = "backend/models/gesture_model.onnx") -> str:
    """
    Constructs an optimized CNN graph for hand gesture classification:
    Input: [batch, 1, 50, 50] (Grayscale normalized 0-1)
    -> Conv2D (3x3, 16 filters, ReLU)
    -> MaxPool (2x2)
    -> Conv2D (3x3, 32 filters, ReLU)
    -> MaxPool (2x2)
    -> Flatten
    -> Dense (64, ReLU)
    -> Dense (9, Softmax)
    Output: [batch, 9] probabilities
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Seed for deterministic weight generation
    np.random.seed(42)

    # 1. Input and Output Tensors
    X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 1, 50, 50])
    Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, len(GESTURE_CLASSES)])

    # 2. Weights & Biases Initializers
    # Conv1: 16 filters of size 1x3x3
    w_conv1 = np.random.randn(16, 1, 3, 3).astype(np.float32) * np.sqrt(2.0 / 9)
    b_conv1 = np.zeros(16, dtype=np.float32)

    # Conv2: 32 filters of size 16x3x3
    w_conv2 = np.random.randn(32, 16, 3, 3).astype(np.float32) * np.sqrt(2.0 / (16 * 9))
    b_conv2 = np.zeros(32, dtype=np.float32)

    # Feature size calculation:
    # 50 -> conv1(same/pad=1) -> 50 -> pool(2) -> 25
    # 25 -> conv2(pad=1) -> 25 -> pool(2) -> 12
    # Flatten size = 32 * 12 * 12 = 4608
    flatten_dim = 32 * 12 * 12

    # Dense 1: 4608 -> 64
    w_fc1 = np.random.randn(flatten_dim, 64).astype(np.float32) * np.sqrt(2.0 / flatten_dim)
    b_fc1 = np.zeros(64, dtype=np.float32)

    # Dense 2: 64 -> 9
    w_fc2 = np.random.randn(64, 9).astype(np.float32) * np.sqrt(2.0 / 64)
    b_fc2 = np.zeros(9, dtype=np.float32)

    initializers = [
        helper.make_tensor('w_conv1', TensorProto.FLOAT, [16, 1, 3, 3], w_conv1.flatten().tolist()),
        helper.make_tensor('b_conv1', TensorProto.FLOAT, [16], b_conv1.tolist()),
        helper.make_tensor('w_conv2', TensorProto.FLOAT, [32, 16, 3, 3], w_conv2.flatten().tolist()),
        helper.make_tensor('b_conv2', TensorProto.FLOAT, [32], b_conv2.tolist()),
        helper.make_tensor('w_fc1', TensorProto.FLOAT, [flatten_dim, 64], w_fc1.flatten().tolist()),
        helper.make_tensor('b_fc1', TensorProto.FLOAT, [64], b_fc1.tolist()),
        helper.make_tensor('w_fc2', TensorProto.FLOAT, [64, 9], w_fc2.flatten().tolist()),
        helper.make_tensor('b_fc2', TensorProto.FLOAT, [9], b_fc2.tolist()),
    ]

    # 3. Nodes
    nodes = [
        # Conv1 + Relu + MaxPool
        helper.make_node('Conv', ['input', 'w_conv1', 'b_conv1'], ['conv1_out'], pads=[1, 1, 1, 1]),
        helper.make_node('Relu', ['conv1_out'], ['relu1_out']),
        helper.make_node('MaxPool', ['relu1_out'], ['pool1_out'], kernel_shape=[2, 2], strides=[2, 2]),

        # Conv2 + Relu + MaxPool
        helper.make_node('Conv', ['pool1_out', 'w_conv2', 'b_conv2'], ['conv2_out'], pads=[1, 1, 1, 1]),
        helper.make_node('Relu', ['conv2_out'], ['relu2_out']),
        helper.make_node('MaxPool', ['relu2_out'], ['pool2_out'], kernel_shape=[2, 2], strides=[2, 2]),

        # Flatten
        helper.make_node('Flatten', ['pool2_out'], ['flatten_out'], axis=1),

        # Dense 1 (Gemm: Y = alpha*A*B + beta*C)
        helper.make_node('Gemm', ['flatten_out', 'w_fc1', 'b_fc1'], ['fc1_out'], alpha=1.0, beta=1.0),
        helper.make_node('Relu', ['fc1_out'], ['relu3_out']),

        # Dense 2
        helper.make_node('Gemm', ['relu3_out', 'w_fc2', 'b_fc2'], ['fc2_out'], alpha=1.0, beta=1.0),

        # Softmax
        helper.make_node('Softmax', ['fc2_out'], ['output'], axis=1),
    ]

    graph = helper.make_graph(
        nodes,
        'GestureRecognitionNet',
        [X],
        [Y],
        initializers,
    )

    model = helper.make_model(graph, producer_name='GestureOS-Optimizer', ir_version=10)
    model.opset_import[0].version = 17

    onnx.checker.check_model(model)
    onnx.save(model, str(out_file))
    print(f"Optimized ONNX model successfully exported to: {out_file}")
    return str(out_file)


if __name__ == "__main__":
    create_onnx_gesture_model()
