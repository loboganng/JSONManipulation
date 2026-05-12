
import json
from pathlib import Path
import glob
import os

# Configurações
INPUT_DIR = Path(r'./')
OUTPUT_DIR = Path(r'./')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def split_via_single_objects(via_data):
    """Separa cada anotação em um arquivo individual mantendo a integridade VIA"""
    metadata = via_data['_via_img_metadata']
    total_files = 0

    for image_key, img_data in metadata.items():
        filename = img_data['filename']
        regions = img_data.get('regions', [])

        if not regions:
            print(f'⚠️  Imagem {filename}: sem regiões (pulando)')
            continue

        original_project_name = via_data['_via_settings']['project']['name']

        for region_idx, region in enumerate(regions):
            # Deep copy preservando TODA estrutura
            single_via = json.loads(json.dumps(via_data))

            # Mantém APENAS esta região
            single_via['_via_img_metadata'][image_key]['regions'] = [region]

            # Remove outras imagens do metadata (mantém integridade)
            single_via['_via_img_metadata'] = {image_key: single_via['_via_img_metadata'][image_key]}

            # Nome descritivo do projeto
            single_via['_via_settings']['project']['name'] = f"{original_project_name}_{filename}_obj{region_idx+1}"

            # Nome do arquivo: IMG_5022.JPG_obj1.json
            safe_filename = filename.replace('.', '_')
            output_filename = f"{safe_filename}_obj{region_idx+1}.json"
            output_path = OUTPUT_DIR / output_filename

            # Salva mantendo encoding UTF-8 e indentação
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(single_via, f, ensure_ascii=False, indent=2)

            label = region['region_attributes'].get('label', 'unknown')
            print(f'✅ {output_filename} <- {filename} [{label}] região {region_idx+1}/{len(regions)}')
            total_files += 1

    return total_files

def main():
    """Processa TODOS os arquivos VIA JSON na pasta atual"""  
    via_files = list(INPUT_DIR.glob('*.json')) + list(INPUT_DIR.glob('convertedFile*.json'))

    if not via_files:
        print('❌ Nenhum arquivo VIA JSON encontrado na pasta atual')
        print('Coloque este script na pasta com os arquivos convertedFileX.json')
        return

    total_processed = 0
    grand_total_files = 0

    for input_file in via_files:
        try:
            print(f'\n🔄 Processando: {input_file.name}')
            with open(input_file, 'r', encoding='utf-8') as f:
                via_data = json.load(f)

            if '_via_img_metadata' not in via_data:
                print(f'  ⏭️  {input_file.name}: não é arquivo VIA (pulando)')
                continue

            files_generated = split_via_single_objects(via_data)
            total_processed += 1
            grand_total_files += files_generated

        except Exception as e:
            print(f'  ❌ Erro em {input_file.name}: {e}')

    print(f'\n🎉 CONCLUÍDO!')
    print(f'📁 Arquivos salvos em: {OUTPUT_DIR}')
    print(f'📊 Processados: {total_processed} arquivos VIA')
    print(f'📊 Gerados: {grand_total_files} arquivos com 1 objeto cada')

if __name__ == '__main__':
    main()