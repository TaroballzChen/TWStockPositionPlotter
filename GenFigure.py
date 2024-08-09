import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys


class PositionFigure:
    def __init__(self, positions_table: pd.DataFrame):
        self.positions = positions_table
        if sys.platform.startswith('darwin'):
            font_name = 'Arial Unicode Ms'
        elif sys.platform.startswith('win'):
            font_name = 'Microsoft YaHei'
        else:
            font_name = 'WenQuanYi Zen Hei'
        plt.rcParams['font.sans-serif'] = [font_name]
        plt.rcParams['axes.unicode_minus'] = False
        self.plt = plt
        sns.set_theme(style="whitegrid")
        sns.set(font=font_name)
        self.color_palette = sns.color_palette("husl", 8)

    def position_pie(self, ax):
        position_type = self.positions.groupby('股票類型').agg({'部位價值': 'sum', '部位占比': 'sum', '數量': 'sum'})
        position_type_index = [i + f'\n({position_type["數量"][i]:,})' for i in position_type.index]
        colors = self.color_palette[:len(position_type)]
        wedges, texts, autotexts = ax.pie(position_type['部位占比'],
                                          labels=position_type_index,
                                          explode=[0.02 for _ in range(len(position_type))],
                                          autopct='%.2f%%',
                                          colors=colors,
                                          startangle=90,
                                          wedgeprops=dict(width=0.6))
        ax.set_title('各類型股票持倉分佈', fontsize=14, fontweight='bold', pad=20)
        plt.setp(autotexts, size=9, weight="bold")

    def loss_bar_with_type(self, ax):
        position_type = self.positions.groupby('股票類型').agg({'損益': 'sum'}).sort_values('損益')
        colors = [self.color_palette[0] if x >= 0 else self.color_palette[2] for x in position_type['損益']]
        bars = ax.barh(position_type.index, position_type['損益'], color=colors, alpha=0.8)

        ax.set_yticks([])
        ax.set_yticklabels([])

        # 為每個柱子添加數值標籤
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f'{width:,.0f}',
                    ha='left' if width >= 0 else 'right', va='center',
                    color='black', fontsize=9, fontweight='bold',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(0, i, f' {position_type.index[i]} ',
                    ha='center', va='center',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        # ax.set_xlabel('損益', fontsize=12, fontweight='bold')
        ax.tick_params(axis='both', which='major', labelsize=10)

        # 添加零線
        ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)

        ax.set_title('各類型股票損益', fontsize=14, fontweight='bold', pad=20)
        sns.despine(left=True, bottom=True, ax=ax)

    def value_bar_chart(self, ax):
        position_type = self.positions.groupby('股票類型').agg({'部位價值': 'sum'}).sort_values('部位價值',
                                                                                                ascending=False)
        colors = sns.color_palette("Blues_d", len(position_type))
        bars = ax.bar(position_type.index, position_type['部位價值'], color=colors)

        # 為每個柱子添加數值標籤
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height,
                    f'{height:,.0f}',
                    ha='center', va='bottom', rotation=0, fontweight='bold', fontsize=9)

        ax.set_ylabel('部位價值', fontsize=12, fontweight='bold')
        # ax.set_xlabel('股票類型', fontsize=12, fontweight='bold')
        ax.set_title('各股票類型部位價值', fontsize=14, fontweight='bold', pad=20)
        ax.tick_params(axis='x', labelsize=9)
        ax.tick_params(axis='y', labelsize=10)

        # 添加輔助線
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        sns.despine(ax=ax)

    def max_holdings_text(self, ax):
        max_holdings = self.positions.loc[self.positions.groupby('股票類型')['部位價值'].idxmax()]

        ax.set_facecolor('white')  # 設置白色背景

        # 標題
        ax.text(0.5, 0.95, "各類型股票最大持倉",
                ha='center', va='top', fontsize=14, fontweight='bold',
                transform=ax.transAxes)

        colors = plt.cm.tab10(np.linspace(0, 1, len(max_holdings)))  # 為每種股票類型生成不同的顏色

        num_rows = len(max_holdings)
        row_height = 0.7 / num_rows  # 調整行高

        for i, (_, row) in enumerate(max_holdings.iterrows()):
            y_pos = 0.85 - (i + 0.5) * row_height  # 調整垂直位置，使文字居中

            # 股票類型
            ax.text(0.05, y_pos, f"{row['股票類型']}:",
                    fontsize=12, fontweight='bold', color=colors[i],
                    transform=ax.transAxes, va='center')

            # 商品代碼
            ax.text(0.5, y_pos, f"{row['商品代碼']}",
                    fontsize=12, transform=ax.transAxes, ha='center', va='center')

            # 佔比
            ax.text(0.95, y_pos, f"({row['部位占比']:,.2f}%)",
                    fontsize=12, color='#555555', transform=ax.transAxes, ha='right', va='center')

            # 添加分隔線
            if i < num_rows - 1:  # 不在最後一行下方添加分隔線
                ax.axhline(y=0.85 - (i + 1) * row_height, xmin=0.05, xmax=0.95,
                           color='lightgray', linestyle='--', linewidth=0.8)

        # # 添加外框
        # ax.add_patch(plt.Rectangle((0.02, 0.1), 0.96, 0.82, fill=False,
        #                            edgecolor='gray', linewidth=1, transform=ax.transAxes))

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        # ax.set_title('各類型最大持倉', fontsize=12, fontweight='bold')

    def daily_position_changes(self, ax):
        """
        顯示今日增加或減少的部位信息，使用更美觀的排版
        """
        # 計算數量變化
        self.positions['數量變化'] = self.positions['數量'] - self.positions['昨日庫存數量']

        # 篩選出有變化的部位
        changed_positions = self.positions[self.positions['數量變化'] != 0].copy()
        changed_positions['變化類型'] = changed_positions['數量變化'].apply(lambda x: '增加' if x > 0 else '減少')

        # 按變化絕對值排序
        changed_positions = changed_positions.sort_values(by='數量變化', key=abs, ascending=False)

        ax.set_facecolor('white')  # 設置白色背景

        # 標題
        ax.text(0.5, 0.95, "今日部位變化",
                ha='center', va='top', fontsize=14, fontweight='bold',
                transform=ax.transAxes)

        colors = plt.cm.RdYlGn(np.linspace(0, 1, len(changed_positions)))  # 為每個變化生成顏色

        num_rows = min(len(changed_positions), 10)  # 限制顯示的行數
        row_height = 0.7 / num_rows  # 調整行高

        for i, (_, row) in enumerate(changed_positions.iterrows()):
            if i >= num_rows:
                break

            y_pos = 0.85 - (i + 0.5) * row_height  # 調整垂直位置，使文字居中

            # 商品代碼和名稱
            ax.text(0.05, y_pos, f"{row['商品代碼']}:",
                    fontsize=11, fontweight='bold', color=colors[i],
                    transform=ax.transAxes, va='center')

            # 變化類型
            change_type = '增加' if row['數量變化'] > 0 else '減少'
            ax.text(0.6, y_pos, change_type,
                    fontsize=11, transform=ax.transAxes, ha='center', va='center',
                    color='green' if change_type == '增加' else 'red')

            # 變化數量
            ax.text(0.95, y_pos, f"{abs(row['數量變化']):,.0f} 股",
                    fontsize=11, color='#555555', transform=ax.transAxes, ha='right', va='center')

            # 添加分隔線
            if i < num_rows - 1:  # 不在最後一行下方添加分隔線
                ax.axhline(y=0.85 - (i + 1) * row_height, xmin=0.05, xmax=0.95,
                           color='lightgray', linestyle='--', linewidth=0.8)

        if changed_positions.empty:
            ax.text(0.5, 0.5, "今日無部位變化",
                    ha='center', va='center', fontsize=12,
                    transform=ax.transAxes)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def custom_combined_charts(self, chart_configs, save_path=None, dpi=300, format='jpg'):
        """
        自定義組合圖表並保存到指定路徑

        :param chart_configs: 列表的列表，每個子列表包含：
                             [方法名稱, 子圖位置, 子圖大小]
        :param save_path: 圖片保存路徑，如果為 None 則顯示圖片而不保存
        :param dpi: 圖片的 DPI (dots per inch)
        :param format: 圖片格式，例如 'png', 'pdf', 'svg' 等
        """
        total_rows = max(config[1][0] for config in chart_configs) + 1
        total_cols = max(config[1][1] for config in chart_configs) + 1

        fig = plt.figure(figsize=(6 * total_cols, 5 * total_rows))

        for method_name, position, size in chart_configs:
            ax = plt.subplot2grid((total_rows, total_cols), position, colspan=size[1], rowspan=size[0])
            method = getattr(self, method_name)
            method(ax)

        plt.tight_layout()
        # plt.suptitle('股票投資組合分析', fontsize=16, fontweight='bold', y=1.02)
        # plt.show()
        if save_path:
            # 確保保存路徑的目錄存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            # 保存圖片
            plt.savefig(save_path, dpi=dpi, format=format, bbox_inches='tight')
            plt.close(fig)  # 關閉圖形以釋放內存
            print(f"圖片已保存至: {save_path}")
        else:
            plt.show()

    def combined_holdings_and_changes(self, ax):
        """
        合併顯示最大持倉和每日變化信息
        """
        ax.set_facecolor('white')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # 繪製最大持倉部分
        self.draw_max_holdings(ax, top=1.0, bottom=0.55)

        # 繪製每日變化部分
        self.draw_daily_changes(ax, top=0.45, bottom=0.0)

        # 添加分隔線
        ax.axhline(y=0.5, xmin=0.02, xmax=0.98, color='gray', linestyle='-', linewidth=0.5)

    def draw_max_holdings(self, ax, top, bottom):
        max_holdings = self.positions.loc[self.positions.groupby('股票類型')['部位價值'].idxmax()]

        ax.text(0.5, top - 0.05, "各類型股票最大持倉",
                ha='center', va='top', fontsize=12, fontweight='bold',
                transform=ax.transAxes)

        colors = plt.cm.tab10(np.linspace(0, 1, len(max_holdings)))
        num_rows = len(max_holdings)
        row_height = (top - bottom - 0.1) / num_rows

        for i, (_, row) in enumerate(max_holdings.iterrows()):
            y_pos = top - 0.1 - (i + 0.5) * row_height

            ax.text(0.05, y_pos, f"{row['股票類型']}:",
                    fontsize=10, fontweight='bold', color=colors[i],
                    transform=ax.transAxes, va='center')

            ax.text(0.5, y_pos, f"{row['商品代碼']}",
                    fontsize=10, transform=ax.transAxes, ha='center', va='center')

            ax.text(0.95, y_pos, f"({row['部位占比']:,.2f}%)",
                    fontsize=10, color='#555555', transform=ax.transAxes, ha='right', va='center')

            if i < num_rows - 1:
                ax.axhline(y=top - 0.1 - (i + 1) * row_height, xmin=0.05, xmax=0.95,
                           color='lightgray', linestyle='--', linewidth=0.8)

    def draw_daily_changes(self, ax, top, bottom):
        self.positions['數量變化'] = self.positions['數量'] - self.positions['昨日庫存數量']
        changed_positions = self.positions[self.positions['數量變化'] != 0].copy()
        changed_positions['變化類型'] = changed_positions['數量變化'].apply(lambda x: '增加' if x > 0 else '減少')
        changed_positions = changed_positions.sort_values(by='數量變化', key=abs, ascending=False)

        ax.text(0.5, top - 0.05, "今日部位變化",
                ha='center', va='top', fontsize=12, fontweight='bold',
                transform=ax.transAxes)

        colors = plt.cm.RdYlGn(np.linspace(0, 1, len(changed_positions)))
        num_rows = min(len(changed_positions), 5)  # 限制顯示的行數
        if num_rows == 0:
            num_rows = 1
        row_height = (top - bottom - 0.1) / num_rows

        for i, (_, row) in enumerate(changed_positions.iterrows()):
            if i >= num_rows:
                break

            y_pos = top - 0.1 - (i + 0.5) * row_height

            ax.text(0.05, y_pos, f"{row['商品代碼']}:",
                    fontsize=9, fontweight='bold', color=colors[i],
                    transform=ax.transAxes, va='center')

            change_type = '增加' if row['數量變化'] > 0 else '減少'
            ax.text(0.6, y_pos, change_type,
                    fontsize=9, transform=ax.transAxes, ha='center', va='center',
                    color='green' if change_type == '增加' else 'red')

            ax.text(0.95, y_pos, f"{abs(row['數量變化']):,.0f} 股",
                    fontsize=9, color='#555555', transform=ax.transAxes, ha='right', va='center')

            if i < num_rows - 1:
                ax.axhline(y=top - 0.1 - (i + 1) * row_height, xmin=0.05, xmax=0.95,
                           color='lightgray', linestyle='--', linewidth=0.8)

        if changed_positions.empty:
            ax.text(0.5, (top + bottom) / 2, "今日無部位變化",
                    ha='center', va='center', fontsize=10,
                    transform=ax.transAxes)

    def save_individual_charts(self, chart_configs, save_dir, dpi=300, format='jpg'):
        """
        根據 chart_configs 生成多個單獨的圖表並保存到指定目錄

        :param chart_configs: 列表的列表，每個子列表包含：
                             [方法名稱, 子圖位置, 子圖大小]
        :param save_dir: 保存圖片的目錄路徑
        :param dpi: 圖片的 DPI (dots per inch)
        :param format: 圖片格式，例如 'png', 'pdf', 'svg' 等
        """
        # 確保保存目錄存在
        os.makedirs(save_dir, exist_ok=True)

        for i, (method_name, _, _) in enumerate(chart_configs):
            # 創建新的圖表
            fig, ax = plt.subplots(figsize=(8, 6))

            # 調用對應的方法繪製圖表
            method = getattr(self, method_name)
            method(ax)

            # 設置標題
            # plt.title(method_name.replace('_', ' ').title(), fontsize=16, fontweight='bold')

            # 調整布局
            plt.tight_layout()

            # 生成文件名
            file_name = f"{method_name}.{format}"
            file_path = os.path.join(save_dir, file_name)

            # 保存圖片
            plt.savefig(file_path, dpi=dpi, format=format, bbox_inches='tight')
            plt.close(fig)  # 關閉圖形以釋放內存

            print(f"圖片已保存至: {file_path}")