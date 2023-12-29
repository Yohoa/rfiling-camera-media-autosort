# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 00:07:26 2023

@author: Raph
"""


all=[
    "MediaRenamer",
    # todo: add logging to file
    # todo: add undo rename
]

import os
import xml.etree.ElementTree as ET
from pymediainfo import MediaInfo



def get_media_info_from_mp4(mp4_file):
    """Extract media information from MP4 using pymediainfo."""
    media_info = MediaInfo.parse(mp4_file)
    for track in media_info.tracks:
        if track.track_type == "Video":
            match track.height:
                case 3840:
                    resolution = "2160p"
                case 1080:
                    resolution = "1080p"
                case 4320:
                    resolution = "8K"
                case _:
                    resolution = str(track.height) + "p"
            # replacing resolution = "2160p" if track.width == 3840 else "1080p"
            fps_raw = track.frame_rate.split()[0]
            import math
            fps = str(math.ceil(float(fps_raw)))
            # NOTE: pymediainfo may not have the exact equivalent fields as your XML,
            # you might have to adjust these fields or the logic accordingly.
            gamma_equation = "rec2100-hlg" if track.transfer_characteristics == "HLG" else "xvycc" if track.transfer_characteristics == "xvYCC" else track.transfer_characteristics  # Placeholder since I don't know the exact field
            color_primaries = "rec2020" if track.color_primaries == "BT.2020" else "rec709" if track.color_primaries == "BT.709" else track.color_primaries  # Placeholder for the same reason

            filename = os.path.basename(mp4_file).rsplit('.', 1)[0]
            result_string = f"{filename}-{resolution}{fps}-{gamma_equation}_{color_primaries}"
            return result_string


def find_mp4_and_xml_pairs(source_dir):
    mp4_files = {}
    xml_files = {}

    for subdir, dirs, files in os.walk(source_dir):
        if '.nomedia' in files or '@Recycle' in subdir:
            continue
        for file in files:
            # print(file)
            if file.endswith('MP4'):
                mp4_files[file] = os.path.join(subdir, file)
                # print(file)
            elif file.endswith('XML'):
                xml_files[file] = os.path.join(subdir, file)

    paired_files = {}
    for key in mp4_files:
        xml_key = key.rsplit('.', 1)[0] + 'M01.XML'
        # print(xml_key)
        if xml_key in xml_files:
            paired_files[mp4_files[key]] = xml_files[xml_key]

    return paired_files


def extract_properties_from_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Get the default namespace
        ns = {'default': root.tag.split('}')[0].strip('{')}

        # Extract the properties using the namespace
        video_codec = root.find(".//default:VideoFrame", ns).get("videoCodec")
        capture_fps = root.find(".//default:VideoFrame", ns).get("captureFps")
        format_fps = root.find(".//default:VideoFrame", ns).get("formatFps")
        gamma_equation = root.find(".//default:Item[@name='CaptureGammaEquation']", ns).get("value")
        color_primaries = root.find(".//default:Item[@name='CaptureColorPrimaries']", ns).get("value")

        return {
            "videoCodec": video_codec,
            "CaptureGammaEquation": gamma_equation,
            "CaptureColorPrimaries": color_primaries,
            "captureFps": capture_fps,
            "formatFps": format_fps
        }
    except Exception as e:
        print(f"Error processing XML file {xml_file}: {e}")
        return None


def extract_name_from_xml(xml_file):
    # Handle namespace in XML
    namespaces = {
        'nrt': 'urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.20'
    }

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        video_frame = root.find('.//nrt:VideoFrame', namespaces=namespaces)
        video_codec = video_frame.get('videoCodec')
        capture_fps = video_frame.get('captureFps')
        format_fps = video_frame.get('formatFps')

        camera_unit_metadata_set = root.find('.//nrt:Group[@name="CameraUnitMetadataSet"]', namespaces=namespaces)
        capture_gamma_equation = camera_unit_metadata_set.find('.//nrt:Item[@name="CaptureGammaEquation"]',
                                                               namespaces=namespaces).get('value')
        capture_color_primaries = camera_unit_metadata_set.find('.//nrt:Item[@name="CaptureColorPrimaries"]',
                                                                namespaces=namespaces).get('value')

        # Construct the desired string format
        filename = os.path.basename(xml_file).rsplit('.', 1)[0][:-3]
        resolution = "2160p" if (video_codec == "AVC_3840_2160_HP@L51") else "1080p"
        # fps = "30" if (capture_fps=="29.97p") else "60" if(capture_fps=="59.94p") else "120" if (capture_fps == "119.88p") else capture_fps
        from math import ceil
        fps_value = float(capture_fps.rstrip('p'))
        rounded_fps = ceil(fps_value)

        fps = str(rounded_fps)
        result_string = f"{filename}-{resolution}{fps}-{capture_gamma_equation}_{capture_color_primaries}"
        return result_string

    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        return None


def rename_file(original_path, new_name):
    """Rename a file with a new name in the same directory."""
    directory = os.path.dirname(original_path)
    new_path = os.path.join(directory, new_name)
    if not os.path.exists(new_path):
        os.rename(original_path, new_path)
        return True
    else:
        print(f"File {new_name} already exists in directory!")
        return False


def MediaRenamer(SOURCE_DIR):
    print(f"Searching the following directory for MP4 and XML files... \n{SOURCE_DIR}")
    paired_files = find_mp4_and_xml_pairs(SOURCE_DIR)

    # Check all MP4 files to determine if they have corresponding XML
    orphaned_mp4_files = []
    for subdir, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith('mp4'):
                xml_file_name = file.rsplit('.', 1)[0] + 'M01.XML'
                xml_path = os.path.join(subdir, xml_file_name)
                if not os.path.exists(xml_path):
                    orphaned_mp4_files.append(os.path.join(subdir, file))
            if file.lower().endswith('mov'):
                xml_file_name = file.rsplit('.', 1)[0] + 'M01.XML'
                xml_path = os.path.join(subdir, xml_file_name)
                if not os.path.exists(xml_path):
                    orphaned_mp4_files.append(os.path.join(subdir, file))
    if not paired_files and not orphaned_mp4_files:
        print("Looks like the directory is incorrect since no MP4 files found.")
        return

    import datetime
    now = datetime.datetime.now()

    now_str = now.strftime('%Y_%m_%d_%H_%M_%S')
    LOG_FILE = f".\\LOG_FILE_{now_str}.txt"

    def log_renaming(original, renamed):
        """Log the renaming operation for potential undoing."""
        with open(LOG_FILE, 'a') as log:
            log.write(f"{original} -> {renamed}\n")

    for mp4, xml in paired_files.items():
        properties = extract_properties_from_xml(xml)
        desired_name = extract_name_from_xml(xml)

        if properties and desired_name:
            print(f"Properties for {mp4}:")
            for key, value in properties.items():
                print(f"{key}: {value}")
            print('-' * 30)


            prompt = 'y'  # overwrite it
            if prompt == 'y':
                success = rename_file(mp4, f"{desired_name}.MP4")
                if success:
                    print(f"Renamed {mp4} to {desired_name}.MP4")
                    # log_renaming(mp4, f"{desired_name}.MP4")
                else:
                    print(f"Failed to rename {mp4}")
            else:
                print(f"Skipped renaming {mp4}")

    # print(orphaned_mp4_files)
    for mp4 in orphaned_mp4_files:
        base_name = os.path.basename(mp4)
        if len(base_name) > 23:
            continue
        desired_name = get_media_info_from_mp4(mp4)
        if desired_name:
            # Rename the MP4 file
            prompt = 'y'  # overwrite it
            if prompt == 'y':
                success = rename_file(mp4, f"{desired_name}.MP4")
                if success:
                # if True:
                    print(f"Renamed {mp4} to {desired_name}.MP4")
                else:
                    print(f"Failed to rename {mp4}")
            else:
                print(f"Skipped renaming {mp4}")


if __name__ == '__main__':
    TARGET_DIR = r"DIR_TO_RENAME"
    MediaRenamer(TARGET_DIR)