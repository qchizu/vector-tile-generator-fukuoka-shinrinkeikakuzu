import yaml
import json
import os

def generate_style_json(config_path, timestamp, output_dir):
    # 設定ファイルの読み込み
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # スタイル設定の取得
    style_config = config.get('style', {})
    colors = style_config.get('color', {})
    
    # ベースとなるスタイル定義
    style = {
        "version": 8,
        "name": style_config.get('name', 'vector-tiles'),
        "glyphs": "https://glyphs.geolonia.com/{fontstack}/{range}.pbf",
        "sources": {
            "base": {
                "type": "vector",
                "tiles": [f"{{host}}/{timestamp}-tiles/{{z}}/{{x}}/{{y}}.pbf"],
                "maxzoom": max(layer['zoom_levels']['max'] for layer in config['layers']),
                "attribution": ""
            }
        },
        "layers": []
    }

    # 各レイヤーのスタイル定義を生成
    for layer in config['layers']:
        layer_name = layer['name']
        min_zoom = layer['zoom_levels']['min']
        max_zoom = layer['zoom_levels']['max']
        
        # ラベルフィールドの決定
        label_field = layer.get('label_field', layer['name'])
        if layer_name == 'detail':
            label_field = style_config.get('detail_field', 'name')

        # 塗りつぶしレイヤー
        style['layers'].append({
            "id": f"{layer_name}-fill",
            "source": "base",
            "source-layer": layer_name,
            "type": "fill",
            "paint": {
                "fill-color": colors.get('fill', "rgb(50, 205, 50)"),
                "fill-opacity": 0.3
            },
            "layout": {
                "visibility": "visible"
            },
            "minzoom": min_zoom,
            "maxzoom": max_zoom
        })

        # ラインレイヤー
        style['layers'].append({
            "id": f"{layer_name}-line",
            "source": "base",
            "source-layer": layer_name,
            "type": "line",
            "paint": {
                "line-color": colors.get('line', "rgb(0, 100, 0)"),
                "line-opacity": 0.5,
                "line-width": 1
            },
            "layout": {
                "visibility": "visible"
            },
            "minzoom": min_zoom,
            "maxzoom": max_zoom
        })

        # ラベルレイヤー
        style['layers'].append({
            "id": f"{layer_name}-label",
            "source": "base",
            "source-layer": layer_name,
            "type": "symbol",
            "layout": {
                "visibility": "visible",
                "text-field": ["coalesce", ["get", label_field], ""],
                "text-size": 15,
                "text-anchor": "center",
                "text-font": ["Noto Sans CJK JP Regular"]
            },
            "paint": {
                "text-color": colors.get('text', "rgb(0, 100, 0)"),
                "text-halo-color": "rgba(255, 255, 255, 0.3)",
                "text-halo-width": 2
            },
            "minzoom": min_zoom,
            "maxzoom": max_zoom
        })

    # style.jsonの保存
    output_path = os.path.join(output_dir, 'style.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(style, f, ensure_ascii=False, indent=2)

    return output_path
