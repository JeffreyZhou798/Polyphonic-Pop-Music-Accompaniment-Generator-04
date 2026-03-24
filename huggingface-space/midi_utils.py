"""
MIDI 处理工具
"""

import numpy as np
import pretty_midi
from io import BytesIO
from typing import Dict, Any, Optional
import tempfile

from config import (
    N_BARS, N_STEPS, N_PITCHES, N_TRACKS,
    TRACK_CONFIG, LOWEST_PITCH, DEFAULT_TEMPO, DEFAULT_VELOCITY
)


def pianoroll_to_midi(pianoroll: np.ndarray, tempo: int = DEFAULT_TEMPO, n_bars: int = None) -> bytes:
    """将 piano roll 转换为 MIDI 文件
    
    Args:
        pianoroll: shape (n_bars, N_STEPS, N_PITCHES, N_TRACKS)
        tempo: 节拍速度
        n_bars: 小节数，如果为 None 则从 pianoroll.shape[0] 获取
    """
    if n_bars is None:
        n_bars = pianoroll.shape[0]
    
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    seconds_per_beat = 60.0 / tempo
    seconds_per_step = seconds_per_beat / 12
    
    for track_idx in range(N_TRACKS):
        config = TRACK_CONFIG[track_idx]
        instrument = pretty_midi.Instrument(
            program=config["program"],
            is_drum=config["is_drum"],
            name=config["name"]
        )
        
        track_pianoroll = pianoroll[..., track_idx]
        
        for bar in range(n_bars):
            for pitch_idx in range(N_PITCHES):
                step = 0
                while step < N_STEPS:
                    if track_pianoroll[bar, step, pitch_idx] > 0.5:
                        start_step = step
                        while step < N_STEPS and track_pianoroll[bar, step, pitch_idx] > 0.5:
                            step += 1
                        end_step = step
                        
                        start_time = bar * 4 * seconds_per_beat + start_step * seconds_per_step
                        end_time = bar * 4 * seconds_per_beat + end_step * seconds_per_step
                        
                        note = pretty_midi.Note(
                            velocity=DEFAULT_VELOCITY,
                            pitch=pitch_idx + LOWEST_PITCH,
                            start=start_time,
                            end=end_time
                        )
                        instrument.notes.append(note)
                    else:
                        step += 1
        
        midi.instruments.append(instrument)
    
    midi_bytes = BytesIO()
    midi.write(midi_bytes)
    return midi_bytes.getvalue()


def midi_to_pianoroll(midi_bytes: bytes, track_idx: int = 0, n_bars: int = None) -> np.ndarray:
    """将 MIDI 文件转换为 piano roll
    
    Args:
        midi_bytes: MIDI 文件字节
        track_idx: 轨道索引
        n_bars: 目标小节数，如果为 None 则根据 MIDI 长度自动计算
    """
    midi = pretty_midi.PrettyMIDI(BytesIO(midi_bytes))
    
    # 计算 MIDI 需要的小节数
    if n_bars is None:
        duration_seconds = midi.get_end_time()
        beats_per_bar = 4
        beats = duration_seconds / (60.0 / 120)  # 假设 120 BPM
        n_bars = max(N_BARS, int(np.ceil(beats / beats_per_bar)))
    
    pianoroll = np.zeros((n_bars, N_STEPS, N_PITCHES), dtype=np.float32)
    
    if track_idx < len(midi.instruments):
        instrument = midi.instruments[track_idx]
        seconds_per_step = 60.0 / 120 / 12
        
        for note in instrument.notes:
            start_step = int(note.start / seconds_per_step)
            end_step = int(note.end / seconds_per_step)
            
            for step in range(start_step, min(end_step, n_bars * N_STEPS)):
                bar = step // N_STEPS
                step_in_bar = step % N_STEPS
                pitch = note.pitch - LOWEST_PITCH
                
                if 0 <= pitch < N_PITCHES and bar < n_bars:
                    pianoroll[bar, step_in_bar, pitch] = 1.0
    
    return pianoroll


def get_midi_info(midi_bytes: bytes) -> Dict[str, Any]:
    """获取 MIDI 文件信息"""
    midi = pretty_midi.PrettyMIDI(BytesIO(midi_bytes))
    return {
        "num_tracks": len(midi.instruments),
        "duration": midi.get_end_time(),
        "tempo": midi.estimate_tempo(),
        "tracks": [
            {"name": inst.name or f"Track {i}", "num_notes": len(inst.notes)}
            for i, inst in enumerate(midi.instruments)
        ]
    }


def create_multi_track_preview(pianoroll: np.ndarray, n_bars: int = None) -> str:
    """创建多轨预览图像
    
    Args:
        pianoroll: shape (n_bars, N_STEPS, N_PITCHES, N_TRACKS)
        n_bars: 小节数，如果为 None 则从 pianoroll.shape[0] 获取
    """
    if n_bars is None:
        n_bars = pianoroll.shape[0]
    
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(N_TRACKS, 1, figsize=(14, 10))
    
    for track_idx in range(N_TRACKS):
        track = pianoroll[..., track_idx]
        merged = track.reshape(-1, N_PITCHES)
        axes[track_idx].imshow(merged.T, aspect='auto', origin='lower', cmap='Blues')
        axes[track_idx].set_ylabel(TRACK_CONFIG[track_idx]["name"])
        axes[track_idx].set_yticks([])
    
    axes[-1].set_xlabel('Time Steps')
    fig.suptitle(f'Multi-Track Piano Roll ({n_bars} bars)')
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    plt.savefig(temp_file.name, dpi=100, bbox_inches='tight')
    plt.close()
    
    return temp_file.name
