"""Accurate zero-based video frame extraction for ComfyUI."""
import random as random_module
from pathlib import Path


def resolve_video(video_path):
    text = video_path.strip().strip('"').strip("'")
    if not text:
        raise ValueError("Magik Frame Extract: enter a video file path.")
    path = Path(text).expanduser()
    if not path.is_absolute():
        import folder_paths
        path = Path(folder_paths.get_input_directory()) / path
    if not path.is_file():
        raise ValueError(f"Magik Frame Extract: video file does not exist: {path}")
    return path


def select_frame(container, frame_index, random, check_interrupt):
    """Decode in presentation order; reservoir sampling needs no frame-count metadata."""
    if not container.streams.video:
        raise ValueError("Magik Frame Extract: file has no video stream.")
    selected = None
    selected_index = -1
    count = 0
    rng = random_module.SystemRandom() if random else None
    for index, frame in enumerate(container.decode(container.streams.video[0])):
        check_interrupt()
        count = index + 1
        if random:
            if rng.randrange(count) == 0:
                selected, selected_index = frame, index
        elif index == frame_index:
            return frame, index
    if selected is not None:
        return selected, selected_index
    if count == 0:
        raise ValueError("Magik Frame Extract: video contains no decodable frames.")
    raise ValueError(
        f"Magik Frame Extract: frame {frame_index} is outside this video. "
        f"Valid indices: 0 to {count - 1} ({count} frames)."
    )


class MagikFrameExtract:
    CATEGORY = "Magik/Video"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract"
    DESCRIPTION = "Extract a zero-based frame from a local video, or choose a random frame."

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "video_path": ("STRING", {"default": "", "tooltip": "Absolute local path, or a path relative to ComfyUI/input."}),
            "frame_index": ("INT", {"default": 0, "min": 0, "max": 2147483647, "step": 1, "tooltip": "Zero-based index: 0 is the first frame. Ignored when Random is enabled."}),
            "random": ("BOOLEAN", {"default": False, "label_on": "Random", "label_off": "Index", "tooltip": "Choose a fresh random frame on each execution. Scans the video once."}),
        }}

    @classmethod
    def IS_CHANGED(cls, video_path, frame_index, random):
        if random:
            return float("nan")
        try:
            stat = resolve_video(video_path).stat()
            return (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size)
        except (OSError, ValueError):
            return float("nan")

    def extract(self, video_path, frame_index, random):
        if not isinstance(frame_index, int) or frame_index < 0:
            raise ValueError("Magik Frame Extract: frame_index must be a nonnegative integer.")
        path = resolve_video(video_path)
        try:
            import av
        except ImportError as exc:
            raise RuntimeError("Magik Frame Extract requires PyAV. Install requirements.txt using ComfyUI's Python environment.") from exc
        import torch
        import comfy.model_management

        comfy.model_management.throw_exception_if_processing_interrupted()
        with av.open(str(path), mode="r") as container:
            frame, _ = select_frame(
                container, frame_index, random,
                comfy.model_management.throw_exception_if_processing_interrupted,
            )
            image = frame.to_ndarray(format="rgb24")
        # ComfyUI IMAGE: float32 RGB, batch/height/width/channels, range 0..1.
        return (torch.from_numpy(image.copy()).to(dtype=torch.float32).div_(255).unsqueeze(0),)
