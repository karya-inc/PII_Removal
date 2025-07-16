import pandas as pd
import os

def export_audio_summary_to_csv(audio_info_list, entity_count_per_audio, entity_category_map, csv_path="audio_file_summary.csv"):
    file_exists = os.path.isfile(csv_path)
    if not audio_info_list:
        print("No audio info to export.")
        return

    last_index = len(audio_info_list) - 1
    info = audio_info_list[last_index]
    duration_min = round(float(info['duration_sec']) / 60, 2) if isinstance(info['duration_sec'], (float, int)) else info['duration_sec']
    has_16k = "✅" if info['sample_rate'] == 16000 else "❌"
    has_8k  = "✅" if info['sample_rate'] == 8000 else "❌"
    has_4k  = "✅" if info['sample_rate'] == 4000 else "❌"
    dual_channel = "✅" if info['channels'] == 2 else "❌"
    mono_channel = "✅" if info['channels'] == 1 else "❌"
    mixed_channel = "❌"
    mixed_samp = "❌"
    pii_count = entity_count_per_audio[last_index] if last_index < len(entity_count_per_audio) else 0

    # Gather all PII categories seen so far
    all_categories = set(entity_category_map.keys())
    if 'pii_category_counts' in info:
        all_categories.update(info['pii_category_counts'].keys())

    row = {
        "Folder Path": info['audio_path'],
        "Duration": duration_min,
        "16kHz": has_16k,
        "8kHz": has_8k,
        "4kHz": has_4k,
        "Mixed Samp Rate": mixed_samp,
        "Dual Channel": dual_channel,
        "Mono Channel": mono_channel,
        "Mixed Channel": mixed_channel,
        "PII Entities Count": pii_count
    }
    # Ensure all categories are present
    for category in sorted(all_categories):
        if 'pii_category_counts' in info and category in info['pii_category_counts']:
            row[category] = info['pii_category_counts'][category]
        else:
            row[category] = 0

    df = pd.DataFrame([row])
    df.to_csv(csv_path, mode='a', header=not file_exists, index=False)
    print(f"CSV summary for {info['audio_path']} saved as: {csv_path}")
