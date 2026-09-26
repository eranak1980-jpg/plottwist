# Portrait segmentation model

u2netp.onnx is the unmodified lightweight U²-Net model distributed by rembg:
https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx

Upstream: Xuebin Qin et al., U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection.
https://github.com/xuebinqin/U-2-Net
License: Apache-2.0, included in LICENSE-U2NET.
Expected upstream MD5: 8e83ca70e441ab06c318d82300c84806.

The model runs locally with ONNX Runtime, one thread, only when a new player photo is uploaded. It predicts an alpha mask; no face or body pixels are synthesized. The original RGB pixels are retained. Low-coverage/invalid masks fall back to a photographic portrait. No runtime model download is needed.
