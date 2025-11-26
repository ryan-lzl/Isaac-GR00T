"""Custom data config for dual camera datasets with front + top views."""

from gr00t.experiment.data_config import So100DualCamDataConfig


class So100DualCamTopFrontDataConfig(So100DualCamDataConfig):
    # Match datasets that expose front and top camera streams
    video_keys = ["video.front", "video.top"]
