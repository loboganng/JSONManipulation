import json
from pathlib import Path

INPUT_EXTENSIONS = {'.json'}
INPUT_DIR = Path('./')
OUTPUT_DIR = Path('./')
DEFAULT_LABEL = 'object'


def sanitize_points(segmentation):
    if not segmentation or not isinstance(segmentation, list):
        return [], []
    points = segmentation[0] if segmentation and isinstance(segmentation[0], list) else segmentation
    if not isinstance(points, list) or len(points) < 6:
        return [], []
    xs = [int(round(points[i])) for i in range(0, len(points), 2)]
    ys = [int(round(points[i])) for i in range(1, len(points), 2)]
    return xs, ys


def bbox_to_rect(bbox):
    if not bbox or len(bbox) != 4:
        return None
    x, y, w, h = bbox
    return {
        'name': 'rect',
        'x': int(round(x)),
        'y': int(round(y)),
        'width': int(round(w)),
        'height': int(round(h)),
    }


def build_category_map(coco):
    return {cat.get('id'): cat.get('name', DEFAULT_LABEL) for cat in coco.get('categories', [])}


def convert_coco_to_via(coco_data, project_name='Converted from COCO'):
    category_map = build_category_map(coco_data)
    images = coco_data.get('images', [])
    annotations = coco_data.get('annotations', [])

    annotations_by_image = {}
    for ann in annotations:
        annotations_by_image.setdefault(ann.get('image_id'), []).append(ann)

    via = {
        '_via_settings': {
            'ui': {
                'annotation_editor_height': 25,
                'annotation_editor_fontsize': 0.8,
                'leftsidebar_width': 18,
                'image_grid': {
                    'img_height': 80,
                    'rshape_fill': 'none',
                    'rshape_fill_opacity': 0.3,
                    'rshape_stroke': 'yellow',
                    'rshape_stroke_width': 2,
                    'show_region_shape': True,
                    'show_image_policy': 'all'
                },
                'image': {
                    'region_label': '__via_region_id__',
                    'region_color': '__via_default_region_color__',
                    'region_label_font': '10px Sans',
                    'on_image_annotation_editor_placement': 'NEAR_REGION'
                }
            },
            'core': {
                'buffer_size': 18,
                'filepath': {},
                'default_filepath': ''
            },
            'project': {
                'name': project_name
            }
        },
        '_via_img_metadata': {},
        '_via_attributes': {
            'region': {
                'label': {
                    'type': 'text',
                    'description': 'Object class label',
                    'default_value': DEFAULT_LABEL
                }
            },
            'file': {}
        }
    }

    for img in images:
        filename = img.get('file_name', 'unknown.jpg')
        width = img.get('width', 0)
        height = img.get('height', 0)
        size = img.get('size', width * height)
        file_key = f"{filename}{size}"
        regions = []

        for ann in annotations_by_image.get(img.get('id'), []):
            label = category_map.get(ann.get('category_id'), DEFAULT_LABEL)
            xs, ys = sanitize_points(ann.get('segmentation'))
            if xs and ys:
                shape_attributes = {
                    'name': 'polygon',
                    'all_points_x': xs,
                    'all_points_y': ys,
                }
            else:
                rect = bbox_to_rect(ann.get('bbox'))
                if rect is None:
                    continue
                shape_attributes = rect

            regions.append({
                'shape_attributes': shape_attributes,
                'region_attributes': {
                    'label': label
                }
            })

        via['_via_img_metadata'][file_key] = {
            'filename': filename,
            'size': size,
            'regions': regions,
            'file_attributes': {}
        }

    return via


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    input_files = sorted([
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in INPUT_EXTENSIONS and not p.name.startswith('convertedFile')
    ])

    counter = 1
    converted = 0
    for input_file in input_files:
        try:
            with input_file.open('r', encoding='utf-8') as f:
                coco_data = json.load(f)

            if 'images' not in coco_data or 'annotations' not in coco_data:
                continue

            project_name = coco_data.get('info', {}).get('description', f'Converted from {input_file.name}')
            via_data = convert_coco_to_via(coco_data, project_name=project_name)
            output_file = OUTPUT_DIR / f'convertedFile{counter}.json'

            with output_file.open('w', encoding='utf-8') as f:
                json.dump(via_data, f, ensure_ascii=False, indent=2)

            print(f'Convertido: {input_file.name} -> {output_file}')
            counter += 1
            converted += 1
        except Exception as e:
            print(f'Erro ao processar {input_file.name}: {e}')

    print(f'Total de arquivos convertidos: {converted}')


if __name__ == '__main__':
    main()
