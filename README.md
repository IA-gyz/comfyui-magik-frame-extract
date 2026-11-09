# Magik Frame Extract

Extract one video frame as a standard ComfyUI IMAGE.

## Install

1. Extract `Magik_Frame_Extract` into `ComfyUI/custom_nodes/`.
2. Using your ComfyUI Python environment, run `python -m pip install -r custom_nodes/Magik_Frame_Extract/requirements.txt`.
3. Restart ComfyUI. Find **Magik Frame Extract** under **Magik/Video**.

## Inputs

- **video_path**: absolute path on the ComfyUI server, or a path relative to `ComfyUI/input`. Quoted paths and `~` are supported.
- **frame_index**: zero-based frame number; 0 selects the first frame. An out-of-range index reports the valid range.
- **random**: ignores the index and selects uniformly among decoded frames. Each execution makes a fresh draw; repeats are possible.

Connect **image** to Preview Image, Save Image, or any IMAGE input.

The first video stream is used; audio is ignored. Frames are decoded in presentation order for accurate indexing, including variable frame rate video. Index mode decodes up to the requested frame. Random mode scans the entire video once using constant frame storage, so long videos take longer. ComfyUI interruption is checked between frames. No GPU video decoder is required.

Output is one RGB float32 image with shape `[1, height, width, 3]`. Encoded pixel dimensions/orientation are retained; rotation metadata and HDR tone mapping are not applied. Codec support depends on the installed PyAV/FFmpeg build.
