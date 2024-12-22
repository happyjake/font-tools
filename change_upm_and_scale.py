import os
import sys
from fontTools.ttLib import TTFont

def change_upm_and_scale(font_path, output_path):
    font = TTFont(font_path)
    old_upm = font['head'].unitsPerEm
    print(f"原 UPM 值: {old_upm}")
    print(f"需要几秒时间，请耐心等待 请不要乱按(^O^) ")
    # 计算缩放因子
    scale_factor = 1000 / old_upm

    # 修改 UPM 值为 1000
    font['head'].unitsPerEm = 1000

    # 调整字符轮廓和度量信息
    # 处理 hmtx 表
    hmtx_table = font['hmtx']
    for name in hmtx_table.metrics.keys():
        hmtx_table.metrics[name] = (int(hmtx_table.metrics[name][0] * scale_factor), hmtx_table.metrics[name][1])

    # 处理 glyf 表
    glyf_table = font['glyf']
    for name in glyf_table.keys():
        glyph = glyf_table[name]
        if glyph.isComposite():
            # 对于组合字形，调整每个组件的变换
            for component in glyph.components:
                # 组合字形的变换处理
                if hasattr(component, 'transform'):
                    component.transform = (
                        component.transform[0] * scale_factor,
                        component.transform[1] * scale_factor,
                        component.transform[2],
                        component.transform[3],
                        component.transform[4] * scale_factor,
                        component.transform[5] * scale_factor,
                    )
        else:
            # 对于普通字形，调整轮廓
            coordinates = glyph.getCoordinates(font['glyf'])[0]
            for i in range(len(coordinates)):
                coordinates[i] = (int(coordinates[i][0] * scale_factor), int(coordinates[i][1] * scale_factor))
            glyph.coordinates = coordinates  # 更新坐标

    # 保存修改后的字体
    font.save(output_path)
    print(f"修改后的字体已保存至 {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供要修改的字体文件路径。")
        sys.exit(1)

    font_path = sys.argv[1]
    # 生成输出文件名
    output_path = f"UPM1000_{os.path.basename(font_path)}"    
    change_upm_and_scale(font_path, output_path)
