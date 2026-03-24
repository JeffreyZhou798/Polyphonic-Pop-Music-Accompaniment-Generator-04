"""
MusicXML 处理工具
支持 .musicxml 和 .mxl 格式
"""

import numpy as np
import tempfile
import os
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

from config import (
    N_BARS, N_STEPS, N_PITCHES, N_TRACKS,
    LOWEST_PITCH, DEFAULT_TEMPO, DEFAULT_VELOCITY, TRACK_CONFIG
)


def parse_musicxml_file(file_bytes: bytes, filename: str) -> Tuple[np.ndarray, Dict]:
    """解析 MusicXML 文件"""
    if filename.lower().endswith('.mxl'):
        xml_content = extract_xml_from_mxl(file_bytes)
    else:
        xml_content = file_bytes
    
    root = ET.fromstring(xml_content.decode('utf-8'))
    notes = extract_notes_from_xml(root)
    pianoroll = notes_to_pianoroll(notes)
    info = get_musicxml_info(root, notes)
    
    return pianoroll, info


def extract_xml_from_mxl(mxl_bytes: bytes) -> bytes:
    """从 .mxl 压缩文件中提取 MusicXML
    
    正确处理 .mxl 标准结构：
    - META-INF/container.xml 指向根文件路径
    - *.xml 或 *.musicxml 是主文件
    """
    with zipfile.ZipFile(BytesIO(mxl_bytes), 'r') as zf:
        namelist = zf.namelist()
        print(f"[DEBUG] .mxl contains: {namelist}")
        
        # 方案1：尝试读取 container.xml 获取根文件路径
        if 'META-INF/container.xml' in namelist:
            container_xml = zf.read('META-INF/container.xml')
            container_root = ET.fromstring(container_xml)
            # 查找 rootfile 元素的 full-path 属性
            rootfile = container_root.find('.//rootfile')
            if rootfile is not None:
                root_path = rootfile.get('full-path')
                if root_path:
                    print(f"[DEBUG] Reading root file from container.xml: {root_path}")
                    return zf.read(root_path)
        
        # 方案2：直接查找 .xml 或 .musicxml 文件
        for name in namelist:
            if name.endswith('.xml') or name.endswith('.musicxml'):
                # 跳过 META-INF/container.xml
                if 'META-INF' not in name:
                    print(f"[DEBUG] Reading XML file: {name}")
                    return zf.read(name)
    
    raise ValueError("No MusicXML file found in .mxl archive")


def extract_notes_from_xml(root: ET.Element) -> list:
    """从 XML 中提取音符
    
    只解析第一个 part（通常是主旋律轨道），避免多轨道混在一起
    支持带命名空间的 MusicXML
    """
    notes = []
    divisions = 480
    
    # 处理命名空间
    ns_uri = ''
    if root.tag.startswith('{'):
        ns_uri = root.tag.split('}', 1)[0][1:]
        print(f"[DEBUG] Detected XML namespace: {ns_uri}")
    
    ns_prefix = '{' + ns_uri + '}' if ns_uri else ''
    
    # 查找 divisions（支持带命名空间）
    divisions_elem = root.find('.//' + ns_prefix + 'divisions')
    if divisions_elem is not None and divisions_elem.text:
        divisions = int(divisions_elem.text)
        print(f"[DEBUG] divisions: {divisions}")
    
    # 只解析第一个 part
    parts = root.findall('.//' + ns_prefix + 'part')
    print(f"[DEBUG] extract_notes_from_xml: found {len(parts)} parts")
    
    if not parts:
        # 打印 XML 结构用于调试
        print(f"[DEBUG] Root tag: {root.tag}")
        print(f"[DEBUG] Root attributes: {root.attrib}")
        print(f"[DEBUG] First 500 chars of XML: {ET.tostring(root, encoding='unicode')[:500]}")
        return notes
    
    # 只处理第一个 part（主旋律）
    part = parts[0]
    measure_num = 0
    
    measures = part.findall('./' + ns_prefix + 'measure')
    print(f"[DEBUG] Found {len(measures)} measures in first part")
    
    for measure in measures:
        measure_num += 1
        current_time = 0.0
        
        for element in measure:
            # 处理带命名空间的 tag
            tag_name = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            
            if tag_name == 'note':
                # 检查是否为休止符
                rest_elem = element.find('./' + ns_prefix + 'rest')
                if rest_elem is not None:
                    duration_elem = element.find('./' + ns_prefix + 'duration')
                    if duration_elem is not None:
                        current_time += float(duration_elem.text) / divisions
                    continue
                
                pitch_elem = element.find('./' + ns_prefix + 'pitch')
                if pitch_elem is not None:
                    step_elem = pitch_elem.find('./' + ns_prefix + 'step')
                    octave_elem = pitch_elem.find('./' + ns_prefix + 'octave')
                    alter_elem = pitch_elem.find('./' + ns_prefix + 'alter')
                    
                    if step_elem is not None and octave_elem is not None:
                        step = step_elem.text
                        octave = int(octave_elem.text)
                        alter = int(alter_elem.text) if alter_elem is not None and alter_elem.text else 0
                        midi_pitch = step_to_midi(step, octave, alter)
                        
                        duration_elem = element.find('./' + ns_prefix + 'duration')
                        duration = float(duration_elem.text) / divisions if duration_elem is not None and duration_elem.text else 1.0
                        
                        # 检查是否为 chord 音符（与前一个音符同时演奏）
                        chord_elem = element.find('./' + ns_prefix + 'chord')
                        is_chord = chord_elem is not None
                        
                        notes.append({
                            'measure': measure_num,
                            'time': current_time,
                            'pitch': midi_pitch,
                            'duration': duration,
                            'is_chord': is_chord
                        })
                        
                        # 只有非 chord 音符才增加 current_time
                        if not is_chord:
                            current_time += duration
            
            elif tag_name == 'backup':
                duration_elem = element.find('./' + ns_prefix + 'duration')
                if duration_elem is not None:
                    current_time -= float(duration_elem.text) / divisions
            
            elif tag_name == 'forward':
                duration_elem = element.find('./' + ns_prefix + 'duration')
                if duration_elem is not None:
                    current_time += float(duration_elem.text) / divisions
    
    print(f"[DEBUG] extract_notes_from_xml: extracted {len(notes)} notes from first part")
    if notes:
        print(f"[DEBUG] First 3 notes: {notes[:3]}")
    return notes


def step_to_midi(step: str, octave: int, alter: int = 0) -> int:
    """将音名转换为 MIDI 音高"""
    step_map = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    return step_map.get(step.upper(), 0) + alter + (octave + 1) * 12


def midi_to_step(midi_pitch: int) -> Tuple[str, int, int]:
    """将 MIDI 音高转换为音名"""
    steps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_pitch // 12) - 1
    step_index = midi_pitch % 12
    step = steps[step_index]
    alter = 1 if '#' in step else 0
    step = step.replace('#', '')
    return step, octave, alter


def notes_to_pianoroll(notes: list, n_bars: int = None) -> np.ndarray:
    """将音符列表转换为 piano roll
    
    Args:
        notes: 音符列表
        n_bars: 目标小节数，如果为 None 则根据实际音符自动计算
    
    Returns:
        pianoroll: shape (n_bars, N_STEPS, N_PITCHES)
    """
    # 计算实际需要的最小小节数
    if notes:
        actual_measures = max(n['measure'] for n in notes)
        if n_bars is None or actual_measures > n_bars:
            n_bars = actual_measures
    else:
        n_bars = n_bars or N_BARS
    
    pianoroll = np.zeros((n_bars, N_STEPS, N_PITCHES), dtype=np.float32)
    steps_per_beat = 12
    
    print(f"[DEBUG] notes_to_pianoroll: {len(notes)} notes, n_bars={n_bars}")
    if notes:
        print(f"[DEBUG] First 5 notes: {notes[:5]}")
    
    for note in notes:
        measure = note['measure'] - 1
        if measure >= n_bars:
            print(f"[DEBUG] Skipping note in measure {note['measure']} (>= n_bars={n_bars})")
            continue
        
        start_step = int(note['time'] * steps_per_beat)
        duration_steps = int(note['duration'] * steps_per_beat)
        pitch = note['pitch'] - LOWEST_PITCH
        
        if 0 <= pitch < N_PITCHES:
            for s in range(duration_steps):
                if start_step + s < N_STEPS:
                    pianoroll[measure, start_step + s, pitch] = 1.0
        else:
            print(f"[DEBUG] Pitch {note['pitch']} out of range (LOWEST_PITCH={LOWEST_PITCH}, N_PITCHES={N_PITCHES})")
    
    total_notes = int(np.sum(pianoroll > 0))
    print(f"[DEBUG] Pianoroll shape: {pianoroll.shape}, total notes: {total_notes}")
    
    return pianoroll


def get_musicxml_info(root: ET.Element, notes: list) -> Dict[str, Any]:
    """获取 MusicXML 文件信息"""
    # 处理命名空间
    ns_uri = ''
    if root.tag.startswith('{'):
        ns_uri = root.tag.split('}', 1)[0][1:]
    ns_prefix = '{' + ns_uri + '}' if ns_uri else ''
    
    title_elem = root.find('.//' + ns_prefix + 'work-title')
    title = title_elem.text if title_elem is not None and title_elem.text else "Unknown"
    
    return {
        "title": title,
        "num_notes": len(notes),
        "num_measures": max(n['measure'] for n in notes) if notes else 0
    }


def validate_musicxml(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """验证 MusicXML 文件"""
    try:
        ext = os.path.splitext(filename.lower())[1]
        if ext not in ['.musicxml', '.xml', '.mxl']:
            return False, f"Unsupported format: {ext}"
        
        if ext == '.mxl':
            xml_content = extract_xml_from_mxl(file_bytes)
        else:
            xml_content = file_bytes
        
        root = ET.fromstring(xml_content.decode('utf-8'))
        notes = extract_notes_from_xml(root)
        
        if not notes:
            return False, "No notes found in the file"
        
        return True, f"Valid file with {len(notes)} notes"
    
    except Exception as e:
        return False, str(e)


def pianoroll_to_musicxml(pianoroll: np.ndarray, tempo: int = DEFAULT_TEMPO, title: str = "Generated by MuseGAN", n_bars: int = None) -> bytes:
    """将 piano roll 转换为 MusicXML
    
    Args:
        pianoroll: shape (n_bars, N_STEPS, N_PITCHES, N_TRACKS)
        tempo: 节拍速度
        title: 乐曲标题
        n_bars: 小节数，如果为 None 则从 pianoroll.shape[0] 获取
    """
    if n_bars is None:
        n_bars = pianoroll.shape[0]
    
    date = datetime.now().strftime("%Y-%m-%d")
    
    part_list = []
    parts = []
    
    for track_idx in range(N_TRACKS):
        track_name = TRACK_CONFIG[track_idx]['name']
        part_id = f"P{track_idx + 1}"
        
        part_list.append(f'''    <score-part id="{part_id}">
      <part-name>{track_name}</part-name>
    </score-part>''')
        
        measures_xml = generate_measures_xml(pianoroll[..., track_idx], track_idx, n_bars)
        
        parts.append(f'''  <part id="{part_id}">
{measures_xml}
  </part>''')
    
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <work>
    <work-title>{title}</work-title>
  </work>
  <identification>
    <creator type="composer">MuseGAN AI</creator>
    <encoding>
      <software>MuseGAN Music Generator</software>
      <encoding-date>{date}</encoding-date>
    </encoding>
  </identification>
  <part-list>
{chr(10).join(part_list)}
  </part-list>
{chr(10).join(parts)}
</score-partwise>'''
    
    return xml_content.encode('utf-8')


def duration_steps_to_type(duration_steps: int) -> Tuple[str, bool]:
    """将 duration_steps 转换为 MusicXML 音符类型
    
    Args:
        duration_steps: 音符持续步数 (12 = 四分音符 = 1拍)
    
    Returns:
        (type_str, dotted): 音符类型字符串和是否附点
    """
    # steps_per_beat = 12, 所以 12步 = 1拍 = 四分音符
    # 音符类型映射 (步数 -> 类型)
    type_map = {
        48: 'whole',    # 4拍 = 全音符
        24: 'half',     # 2拍 = 二分音符
        12: 'quarter',  # 1拍 = 四分音符
        6: 'eighth',    # 1/2拍 = 八分音符
        3: '16th',      # 1/4拍 = 十六分音符
        1: '32nd',      # 1/12拍 = 三十二分音符
        2: '32nd',      # 1/6拍
    }
    
    # 检查是否为附点音符 (如附点四分音符 = 18步 = 12 + 6)
    dotted_types = {
        36: ('half', True),      # 附点二分 = 3拍
        18: ('quarter', True),   # 附点四分 = 1.5拍
        9: ('eighth', True),     # 附点八分 = 0.75拍
    }
    
    if duration_steps in dotted_types:
        return dotted_types[duration_steps]
    
    # 查找最近的类型
    best_type = 'quarter'
    for steps, note_type in sorted(type_map.items(), key=lambda x: abs(x[0] - duration_steps)):
        best_type = note_type
        if steps <= duration_steps:
            break
    
    return best_type, False


def generate_measures_xml(track_pianoroll: np.ndarray, track_idx: int, n_bars: int = None) -> str:
    """生成小节 XML
    
    按时间顺序生成音符，支持和弦检测，正确计算音符类型
    
    Args:
        track_pianoroll: shape (n_bars, N_STEPS, N_PITCHES)
        track_idx: 轨道索引
        n_bars: 小节数，如果为 None 则从 track_pianoroll.shape[0] 获取
    """
    if n_bars is None:
        n_bars = track_pianoroll.shape[0]
    
    measures = []
    divisions = 480  # MusicXML 标准值
    
    for bar in range(n_bars):
        # 收集本小节所有音符事件
        note_events = []
        
        for pitch_idx in range(N_PITCHES):
            step = 0
            while step < N_STEPS:
                if track_pianoroll[bar, step, pitch_idx] > 0.5:
                    start_step = step
                    while step < N_STEPS and track_pianoroll[bar, step, pitch_idx] > 0.5:
                        step += 1
                    duration_steps = step - start_step
                    
                    midi_pitch = pitch_idx + LOWEST_PITCH
                    
                    note_events.append({
                        'start_step': start_step,
                        'duration_steps': duration_steps,
                        'pitch': midi_pitch
                    })
                else:
                    step += 1
        
        # 按开始时间排序
        note_events.sort(key=lambda x: (x['start_step'], -x['pitch']))
        
        # 检测和弦（同一时刻开始的多个音符）
        if note_events:
            for i, event in enumerate(note_events):
                # 检查是否与上一个音符同时开始（和弦）
                is_chord = (i > 0 and 
                           note_events[i-1]['start_step'] == event['start_step'])
                event['is_chord'] = is_chord
        
        # 生成 XML
        notes_xml = []
        for event in note_events:
            step_name, octave, alter = midi_to_step(event['pitch'])
            duration = event['duration_steps'] * divisions // 12
            note_type, dotted = duration_steps_to_type(event['duration_steps'])
            
            alter_xml = f"<alter>{alter}</alter>" if alter != 0 else ""
            chord_xml = "<chord/>" if event['is_chord'] else ""
            dot_xml = "<dot/>" if dotted else ""
            
            notes_xml.append(f'''      <note>
        {chord_xml}<pitch>
          <step>{step_name}</step>{alter_xml}
          <octave>{octave}</octave>
        </pitch>
        <duration>{duration}</duration>
        <voice>1</voice>
        <type>{note_type}</type>{dot_xml}
      </note>''')
        
        # 如果小节为空，生成休止符
        if not notes_xml:
            notes_xml = ['      <note><rest/><duration>1920</duration></note>']
        
        measures.append(f'''    <measure number="{bar + 1}">
{chr(10).join(notes_xml)}
    </measure>''')
    
    return chr(10).join(measures)
