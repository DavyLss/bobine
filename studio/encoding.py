"""Probe real NVENC availability; work on CPU-only computers too."""
import os,subprocess
from functools import lru_cache
import imageio_ffmpeg
@lru_cache(maxsize=1)
def encoder():
    choice=os.getenv('STUDIO_VIDEO_CODEC','auto')
    if choice not in ['auto','h264_nvenc','libx264']:raise ValueError('STUDIO_VIDEO_CODEC: auto, h264_nvenc ou libx264')
    if choice=='auto':
        probe=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-f','lavfi','-i','color=size=128x128:rate=1','-frames:v','1','-c:v','h264_nvenc','-f','null','-'],capture_output=True,timeout=20,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        choice='h264_nvenc' if probe.returncode==0 else 'libx264'
    quality=['-cq','18'] if choice=='h264_nvenc' else ['-crf','18','-preset','medium']
    return choice,quality+['-pix_fmt','yuv420p','-movflags','+faststart']
