import json
from copy import deepcopy
from pathlib import Path

INPUT_DIR = Path('./')
OUTPUT_DIR = Path(r'./')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)


def detect_format(data):
    if isinstance(data, dict):
        if '_via_img_metadata' in data:
            return 'via_project'
        sample_value = next(iter(data.values()), None)
        if isinstance(sample_value, dict) and 'filename' in sample_value and 'regions' in sample_value:
            return 'vgg_classic'
    return None


def split_via_project(via_data, source_name):
    total_files = 0
    metadata = via_data.get('_via_img_metadata', {})
    project_name = via_data.get('_via_settings', {}).get('project', {}).get('name', 'project')

    for image_key, img_data in metadata.items():
        filename = img_data.get('filename', 'unknown')
        regions = img_data.get('regions', [])

        if not regions:
            print(f'⚠️  {filename}: sem regiões (pulando)')
            continue

        for region_idx, region in enumerate(regions, start=1):
            single_file = deepcopy(via_data)
            single_file['_via_img_metadata'] = {
                image_key: {
                    **deepcopy(img_data),
                    'regions': [deepcopy(region)]
                }
            }
            single_file.setdefault('_via_settings', {}).setdefault('project', {})['name'] = f'{project_name}_{filename}_obj{region_idx}'

            output_name = f'{sanitize_filename(Path(filename).stem)}_obj{region_idx}.json'
            output_path = OUTPUT_DIR / output_name
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(single_file, f, ensure_ascii=False, indent=2)

            label = region.get('region_attributes', {}).get('label', 'unknown')
            print(f'✅ {output_name} <- {source_name} [{label}]')
            total_files += 1

    return total_files


def split_vgg_classic(vgg_data, source_name):
    total_files = 0

    for image_key, img_data in vgg_data.items():
        if not isinstance(img_data, dict):
            continue

        filename = img_data.get('filename', 'unknown')
        regions = img_data.get('regions', [])

        if isinstance(regions, dict):
            regions = list(regions.values())

        if not regions:
            print(f'⚠️  {filename}: sem regiões (pulando)')
            continue

        for region_idx, region in enumerate(regions, start=1):
            single_entry = deepcopy(img_data)
            single_entry['regions'] = [deepcopy(region)]
            single_file = {image_key: single_entry}

            output_name = f'{sanitize_filename(Path(filename).stem)}_obj{region_idx}.json'
            output_path = OUTPUT_DIR / output_name
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(single_file, f, ensure_ascii=False, indent=2)

            label = region.get('region_attributes', {}).get('label', 'unknown')
            print(f'✅ {output_name} <- {source_name} [{label}]')
            total_files += 1

    return total_files


def process_file(input_file: Path):
    with input_file.open('r', encoding='utf-8') as f:
        data = json.load(f)

    detected = detect_format(data)

    if detected == 'via_project':
        return split_via_project(data, input_file.name)
    if detected == 'vgg_classic':
        return split_vgg_classic(data, input_file.name)

    print(f'⏭️  {input_file.name}: formato não reconhecido como VIA/VGG')
    return 0


def main():
    json_files = sorted(INPUT_DIR.glob('*.json'))

    if not json_files:
        print('❌ Nenhum arquivo JSON encontrado na pasta atual.')
        return

    processed = 0
    generated = 0

    for input_file in json_files:
        try:
            print(f'\n🔄 Processando: {input_file.name}')
            count = process_file(input_file)
            if count > 0:
                processed += 1
                generated += count
        except Exception as e:
            print(f'❌ Erro em {input_file.name}: {e}')

    print(f'\n🎉 CONCLUÍDO!')
    print(f'📁 Arquivos salvos em: {OUTPUT_DIR}')
    print(f'📊 Arquivos processados: {processed}')
    print(f'📊 Arquivos gerados: {generated}')


if __name__ == '__main__':
    main()
