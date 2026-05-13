# COCO to VGG Utilities

Scripts em Python para conversão e reorganização de anotações de datasets no formato **COCO JSON** e **VGG Image Annotator (VIA) JSON**.

## Arquivos do projeto

### 1. `coco_to_vgg_converter.py`
Converte arquivos no formato **COCO JSON** para **VGG/VIA JSON**.

#### O que faz
- Lê arquivos `.json` com estrutura COCO.
- Converte `images` e `annotations` para a estrutura `_via_img_metadata`.
- Usa `segmentation` como `polygon` no VIA quando disponível.
- Usa `bbox` como `rect` quando não houver segmentação válida.
- Cria arquivos de saída com nomes incrementais, como:
  - `convertedFile1.json`
  - `convertedFile2.json`
  - `convertedFile3.json`

#### Observações
- Se o arquivo COCO não tiver `categories`, o script usa a label padrão `object`.
- Os arquivos convertidos são salvos no diretório configurado dentro do script.

#### Como usar
```bash
python3 coco_to_vgg_converter.py
```

> Coloque o script na mesma pasta dos arquivos COCO `.json` que deseja converter.

---

### 2. `via_split_single_objects.py`
Separa cada anotação de um arquivo **VGG/VIA JSON** em um novo arquivo contendo **apenas 1 objeto**.

#### O que faz
- Lê arquivos VIA JSON.
- Percorre cada imagem e cada região anotada.
- Gera um novo arquivo para cada objeto individual.
- Mantém a estrutura original do VIA, incluindo:
  - `_via_settings`
  - `_via_attributes`
  - `file_attributes`
  - `shape_attributes`
  - `region_attributes`

#### Exemplo de saída
Se uma imagem tiver 3 objetos anotados, serão gerados arquivos como:
- `IMG_5022_JPG_obj1.json`
- `IMG_5022_JPG_obj2.json`
- `IMG_5022_JPG_obj3.json`

#### Como usar
```bash
python3 via_split_single_objects.py
```

> Coloque o script na mesma pasta dos arquivos VIA `.json` que deseja processar.

---

## Fluxo sugerido

1. Converter arquivos COCO para VGG/VIA com `coco_to_vgg_converter.py`
2. Separar cada objeto individual com `via_split_single_objects.py`

---

## Requisitos

- Python 3.8+
- Biblioteca padrão do Python apenas

Não é necessário instalar dependências externas.

---

## Estrutura esperada

### Entrada COCO
Arquivo JSON com campos como:
- `images`
- `annotations`
- `categories` (opcional)

### Saída VIA
Arquivo JSON com campos como:
- `_via_settings`
- `_via_img_metadata`
- `_via_attributes`

---

## Ajustes recomendados

Antes de executar, revise nos scripts:
- Pasta de saída (`OUTPUT_DIR`)
- Nome padrão de label, se necessário
- Pasta de entrada, caso queira adaptar para um caminho fixo

---

## Casos de uso

Esses scripts são úteis para:
- preparação de datasets para visão computacional;
- reorganização de anotações para treino com 1 objeto por arquivo;
- conversão entre ferramentas de anotação;
- padronização de datasets para etapas de treinamento e validação.
