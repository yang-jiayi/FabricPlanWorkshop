#!/usr/bin/env python3
"""Build the Japanese participant overview deck, without network or Fabric access."""
import argparse
import hashlib
import io
import re
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('docs/workshop-overview-ja.pptx')
FONT = 'Yu Gothic UI'
REPO = 'https://github.com/yang-jiayi/FabricPlanWorkshop'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
ICONS = {
    'Fabric': 'fabric_48_color.svg',
    'Plan': 'planning_48_item.svg',
    'SQL database': 'sql_database_48_item.svg',
    'Semantic model': 'semantic_model_48_item.svg',
    'Warehouse': 'data_warehouse_48_item.svg',
    'Data Agent': 'data_agent_48_item.svg',
    'Lakehouse': 'lakehouse_48_item.svg',
    'Notebook': 'notebook_48_item.svg',
    'Power BI': 'power_bi_48_color.svg',
    'OneLake': 'one_lake_48_color.svg',
    'Graph intelligence': 'graph_intelligence_48_color.svg',
    'Workspace': 'group_workspace_48_non-item.svg',
    'Copilot': 'copilot_48_color.svg',
    'Report': 'report_48_item.svg',
}
LABS = [
    '00-prerequisites.md', '01-environment-and-first-sheet.md',
    '02-allocation-and-collaboration.md', '03-optimizer.md',
    '04-forecast-and-writeback.md', '05-pl-models-and-scenarios.md',
    '06-intelligence-canvas.md', '07-powertable.md',
    '08-sizing-and-governance.md', '09-variance-analyst.md',
]
INK, MUTED, GREEN, BLUE, PURPLE = '172B3A', '465E70', '007F6D', '005FB8', '6941C6'
PALE, LINE, WHITE = 'F3F7FB', 'DCE5ED', 'FFFFFF'
JAPANESE = r'\u3041-\u3096\u30a1-\u30fa\u3400-\u4dbf\u4e00-\u9fff々〆'
TERMS = {
    'セマンティックモデル': 'Semantic model',
    'SQLデータベース': 'SQL database',
    '計画シート': 'Planning sheet',
    'ワークスペース': 'Workspace',
}


def japanese_spacing(text):
    """Separate prose boundaries, preserving URLs, code, names and punctuation."""
    text = re.sub(fr'([{JAPANESE}])[ \t]*([A-Za-z0-9$])', r'\1 \2', text)
    return re.sub(fr'([A-Za-z0-9%])[ \t]*([{JAPANESE}])', r'\1 \2', text)


def learner_text(text):
    for original, english in TERMS.items():
        text = text.replace(original, english)
    return japanese_spacing(text)


def spacing_errors(payload):
    errors = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for name in archive.namelist():
            if not name.startswith('ppt/') or not name.endswith('.xml'):
                continue
            for paragraph in ET.fromstring(archive.read(name)).findall('.//a:p', NS):
                text = ''.join(node.text or '' for node in paragraph.findall('.//a:t', NS))
                if text and japanese_spacing(text) != text:
                    errors.append(f'{name}: Japanese/Latin spacing: {text!r}')
    return errors


def participant_source(path):
    text = path.read_text(encoding='utf-8')
    text = re.sub(
        r'<!-- presentation-exclude-start: ([A-Z0-9-]+) -->.*?'
        r'<!-- presentation-exclude-end: \1 -->', '', text, flags=re.S,
    )
    if 'presentation-exclude-' in text:
        raise ValueError(f'Unbalanced exclusion markers: {path}')
    return re.sub(r'<details>\s*<summary>解答</summary>.*?</details>', '', text, flags=re.S)


def validate_sources(root):
    """Keep provenance limited to learner sources, never facilitator material."""
    sources = [Path('README.md')] + [Path('labs') / name for name in LABS]
    return {path.as_posix(): hashlib.sha256(
        participant_source(root / path).replace('\r\n', '\n').encode('utf-8')
    ).hexdigest() for path in sources}


def font_errors(payload):
    """Audit the complete OPC package, including notes, masters and layouts."""
    errors = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for name in archive.namelist():
            if not name.startswith('ppt/') or not name.endswith('.xml'):
                continue
            root = ET.fromstring(archive.read(name))
            for element in root.iter():
                if 'typeface' in element.attrib and element.get('typeface') != FONT:
                    errors.append(f'{name}: unexpected typeface {element.get("typeface")!r}')
            for run in root.findall('.//a:r', NS) + root.findall('.//a:fld', NS):
                props = run.find('a:rPr', NS)
                for script in ('latin', 'ea', 'cs'):
                    entry = props.find(f'a:{script}', NS) if props is not None else None
                    if entry is None or entry.get('typeface') != FONT:
                        errors.append(f'{name}: run missing explicit {script} font')
            if name.startswith('ppt/theme/'):
                for kind in ('majorFont', 'minorFont'):
                    for script in ('latin', 'ea', 'cs'):
                        entries = root.findall(f'.//a:{kind}/a:{script}', NS)
                        if not entries or any(e.get('typeface') != FONT for e in entries):
                            errors.append(f'{name}: missing {kind}/{script}')
    return errors


def normalize_package(payload):
    from lxml import etree

    def fonts(props):
        for script in ('latin', 'ea', 'cs'):
            node = props.find(f'{{{NS["a"]}}}{script}')
            if node is None:
                node = etree.SubElement(props, f'{{{NS["a"]}}}{script}')
            node.set('typeface', FONT)

    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(payload)) as original:
        with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as result:
            for name in sorted(original.namelist()):
                data = original.read(name)
                if name.startswith('ppt/') and name.endswith('.xml'):
                    root = etree.fromstring(data)
                    for element in root.iter():
                        if 'typeface' in element.attrib:
                            element.set('typeface', FONT)
                    for text in root.findall('.//a:t', NS):
                        if text.text:
                            text.text = learner_text(text.text)
                    for tag in ('rPr', 'defRPr', 'endParaRPr'):
                        for props in root.findall(f'.//a:{tag}', NS):
                            fonts(props)
                    for run in root.findall('.//a:r', NS) + root.findall('.//a:fld', NS):
                        props = run.find('a:rPr', NS)
                        if props is None:
                            props = etree.Element(f'{{{NS["a"]}}}rPr')
                            run.insert(0, props)
                        fonts(props)
                    data = etree.tostring(root, xml_declaration=True, encoding='UTF-8',
                                          standalone=True)
                info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                result.writestr(info, data)
    return output.getvalue()


class Deck:
    def __init__(self, root, scratch):
        from pptx import Presentation
        from pptx.util import Inches

        self.root, self.scratch = Path(root), Path(scratch)
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333333), Inches(7.5)
        props = self.prs.core_properties
        props.title = 'Microsoft Fabric Plan Workshop'
        props.subject = learner_text('参加者向けワークショップ概要 / Lab00–09')
        props.author = 'Jiayi Yang, Swarm Data SE'
        props.keywords = 'Microsoft Fabric, Plan, 日本語, Yu Gothic UI'
        props.created = props.modified = datetime(2026, 11, 3)
        props.last_modified_by = 'Jiayi Yang'
        props.revision = 1
        self.sources = validate_sources(self.root)
        self.icon_paths = {}
        self._backgrounds()
        self.slide = None

    def _backgrounds(self):
        from PIL import Image

        stops = [(9, 29, 66), (0, 88, 125), (0, 146, 124), (87, 52, 177)]
        image = Image.new('RGB', (1600, 900))
        pixels = image.load()
        for x in range(image.width):
            position = x / (image.width - 1) * (len(stops) - 1)
            index = min(int(position), len(stops) - 2)
            fraction = position - index
            color = tuple(round(stops[index][c] * (1 - fraction)
                                + stops[index + 1][c] * fraction) for c in range(3))
            for y in range(image.height):
                shade = 0.72 + 0.28 * (1 - y / image.height)
                pixels[x, y] = tuple(round(c * shade) for c in color)
        self.gradient = self.scratch / 'gradient.png'
        image.save(self.gradient, optimize=True)

    def rect(self, x, y, w, h, fill, border=None, radius=False):
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.dml.color import RGBColor
        from pptx.util import Inches

        shape = self.slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(y), Inches(w), Inches(h),
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill)
        if border:
            shape.line.color.rgb = RGBColor.from_string(border)
        else:
            shape.line.fill.background()
        if radius:
            shape.adjustments[0] = 0.12
        return shape

    def text(self, value, x, y, w, h, size=22, color=INK, bold=False, align=None,
             link=None):
        from pptx.util import Inches, Pt
        from pptx.enum.text import MSO_AUTO_SIZE
        from pptx.dml.color import RGBColor

        shape = self.slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        frame = shape.text_frame
        frame.clear()
        frame.word_wrap = True
        frame.auto_size = MSO_AUTO_SIZE.NONE
        frame.margin_left = frame.margin_right = 0
        frame.margin_top = frame.margin_bottom = 0
        for index, line in enumerate(learner_text(value).split('\n')):
            para = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            para.space_after, para.space_before = Pt(2), Pt(0)
            para.line_spacing = 1.17
            if align is not None:
                para.alignment = align
            run = para.add_run()
            run.text = line
            run.font.name, run.font.size, run.font.bold = FONT, Pt(size), bold
            run.font.color.rgb = RGBColor.from_string(color)
            props = para._p.get_or_add_pPr()
            props.set('eaLnBrk', '1')
        if link:
            # Shape hyperlinks preserve explicit text color on dark backgrounds.
            shape.click_action.hyperlink.address = link
        return shape

    def icon(self, name, x, y, size=0.55):
        from pptx.util import Inches
        import resvg_py

        if name not in self.icon_paths:
            source = self.root / 'assets' / 'brand' / ICONS[name]
            destination = self.scratch / (source.stem + '.png')
            destination.write_bytes(resvg_py.svg_to_bytes(
                svg_string=source.read_text(encoding='utf-8'), width=240, height=240,
            ))
            self.icon_paths[name] = destination
        shape = self.slide.shapes.add_picture(
            str(self.icon_paths[name]), Inches(x), Inches(y), Inches(size), Inches(size),
        )
        shape._element.nvPicPr.cNvPr.set('descr', f'Microsoft Fabric公式アイコン / {name}')
        return shape

    def picture(self, relative, x, y, w, h, description):
        from PIL import Image
        from pptx.util import Inches

        path = self.root / relative
        with Image.open(path) as image:
            iw, ih = image.size
        scale = min(w / iw, h / ih)
        pw, ph = iw * scale, ih * scale
        picture = self.slide.shapes.add_picture(
            str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2),
            Inches(pw), Inches(ph),
        )
        picture._element.nvPicPr.cNvPr.set('descr', description)
        return picture

    def new(self, section, title, source='README.md', dark=False):
        from pptx.util import Inches
        from pptx.enum.text import PP_ALIGN

        self.slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.slide.background.fill.solid()
        from pptx.dml.color import RGBColor
        self.slide.background.fill.fore_color.rgb = RGBColor.from_string(WHITE)
        if dark:
            self.slide.shapes.add_picture(str(self.gradient), 0, 0,
                                         self.prs.slide_width, self.prs.slide_height)
        else:
            self.slide.shapes.add_picture(str(self.gradient), 0, 0,
                                         self.prs.slide_width, Inches(0.13))
        fg = WHITE if dark else MUTED
        self.icon('Fabric', 0.48, 0.32, 0.38)
        self.text('Microsoft Fabric', 0.98, 0.35, 2.4, 0.28, 12, fg, True)
        self.text(f'Learn / Plan Workshop / {section}', 3.25, 0.35, 8.6, 0.3,
                  12, fg)
        self.text(title, 0.55, 1.02, 12.2, 0.73, 31, WHITE if dark else INK, True)
        self.rect(0.55, 1.92, 0.85, 0.065, '58E0BD' if dark else GREEN)
        self.text('Jiayi Yang, Swarm Data SE', 0.55, 7.12, 3.1, 0.22, 10, fg)
        source_url = f'{REPO}/blob/main/{source}'
        self.text(f'出典: {source}', 3.5, 7.12, 8.35, 0.22, 10, fg, link=source_url)
        self.text(f'{len(self.prs.slides):02d}', 12.1, 7.08, 0.65, 0.28, 12,
                  fg, align=PP_ALIGN.RIGHT)
        notes = [
            f'{title}\n参加者向けの概要資料。詳細な操作は正本Markdownを参照。',
            f'出典: {source_url}',
            '原典: Diego Diaz / Fabric Planning Lab。日本語版制作: Jiayi Yang, Swarm Data SE。',
            f'参加者向け出典SHA256: {self.sources[source]}',
            'presentation-exclude範囲 / 解答 / 講師用資料は採用しない。',
        ]
        self.slide.notes_slide.notes_text_frame.text = '\n'.join(notes)
        return self.slide

    def card(self, x, y, w, h, label, body, icon=None, accent=GREEN, size=21):
        self.rect(x, y, w, h, PALE, LINE, True)
        self.rect(x, y + 0.14, 0.055, h - 0.28, accent)
        offset = 0.25
        if icon:
            self.icon(icon, x + 0.25, y + 0.23, 0.53)
            offset = 0.96
        self.text(label, x + offset, y + 0.25, w - offset - 0.2, 0.64,
                  23, INK, True)
        self.text(body, x + 0.25, y + 1.02, w - 0.5, h - 1.15, size)

    def callout(self, label, body, y=5.75, kind='note'):
        bg, accent = {
            'note': ('EAF3FF', BLUE), 'tip': ('E5F8F1', GREEN),
            'important': ('F1EAFE', PURPLE), 'warning': ('FFF2D6', '855600'),
        }[kind]
        self.rect(0.55, y, 12.23, 0.98, bg, radius=True)
        self.rect(0.55, y + 0.12, 0.055, 0.74, accent)
        self.text(label, 0.8, y + 0.14, 1.45, 0.32, 17, accent, True)
        self.text(body, 2.28, y + 0.16, 10.1, 0.72, 18)

    def steps(self, rows, x=0.65, y=2.3, w=5.2, gap=1.03):
        for index, (title, body) in enumerate(rows):
            self.rect(x, y + index * gap, 0.4, 0.4, GREEN, radius=True)
            self.text(str(index + 1), x + 0.07, y + index * gap + 0.02,
                      0.28, 0.3, 17, WHITE, True)
            self.text(title, x + 0.58, y + index * gap - 0.03,
                      w - 0.58, 0.38, 21, INK, True)
            self.text(body, x + 0.58, y + index * gap + 0.42,
                      w - 0.58, 0.68, 18, MUTED)

    def flow_node(self, x, y, w, title, body, icon, accent=GREEN):
        self.rect(x, y, w, 1.72, PALE, LINE, True)
        offset = 0.18
        if icon:
            self.icon(icon, x + 0.18, y + 0.18, 0.48)
            offset = 0.8
        self.text(title, x + offset, y + 0.21, w - offset - 0.17, 0.4, 20, accent, True)
        self.text(body, x + 0.18, y + 0.8, w - 0.36, 0.82, 18)

    def arrow(self, x, y, w=0.42, direction='right'):
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.util import Inches
        from pptx.dml.color import RGBColor

        arrow_type = {'right': MSO_SHAPE.RIGHT_ARROW, 'down': MSO_SHAPE.DOWN_ARROW,
                      'up': MSO_SHAPE.UP_ARROW}[direction]
        shape = self.slide.shapes.add_shape(arrow_type, Inches(x), Inches(y),
                                            Inches(w), Inches(0.22))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(GREEN)
        shape.line.fill.background()

    def screenshot_slide(self, section, title, lab, image, alt, rows, caution,
                         caution_kind='important'):
        self.new(section, title, f'labs/{LABS[lab]}')
        self.steps(rows, w=4.0, gap=1.04)
        self.rect(4.95, 2.24, 7.83, 3.05, PALE, LINE, True)
        self.picture(f'assets/screenshots/{image}', 5.04, 2.32, 7.65, 2.83, alt)
        self.text('教材の操作画面例 / 詳細はLabの画像を拡大して確認', 5.08, 5.37,
                  7.4, 0.26, 11, MUTED)
        self.callout('重要' if caution_kind == 'important' else '補足', caution,
                     kind=caution_kind)

    def populate(self):
        self.new('概要', 'Microsoft Fabric\nPlan Workshop', dark=True)
        # Cover uses a larger two-line title, without a tagline.
        title = self.slide.shapes[4]
        from pptx.util import Inches, Pt
        title.top, title.height, title.width = Inches(1.7), Inches(2.0), Inches(6.6)
        for para in title.text_frame.paragraphs:
            for run in para.runs:
                run.font.size = Pt(42)
        self.slide.shapes[5].top = Inches(4.03)
        credit = self.slide.shapes[6]
        credit.top, credit.height, credit.width = Inches(6.65), Inches(0.35), Inches(6.6)
        for run in credit.text_frame.paragraphs[0].runs:
            run.font.size = Pt(16)
        self.text('参加者向け概要', 0.6, 4.3, 5.9, 0.55, 25, WHITE, True)
        self.text('Lab00–09  /  日本語版', 0.6, 5.12, 5.9, 0.4, 21, WHITE)
        self.text('独立した非公式のコミュニティ教材', 0.6, 6.05, 6.1, 0.4, 16, WHITE)
        for index, name in enumerate(['Fabric', 'Plan', 'Power BI', 'OneLake',
                                      'SQL database', 'Semantic model']):
            x, y = 7.15 + (index % 2) * 2.7, 1.65 + (index // 2) * 1.62
            self.rect(x, y, 2.48, 1.4, WHITE, radius=True)
            self.icon(name, x + 0.92, y + 0.17, 0.63)
            self.text(name, x + 0.15, y + 0.94, 2.18, 0.3, 16, INK, True)

        self.new('目的', 'このワークショップで身につけること')
        self.card(0.55, 2.3, 5.98, 1.82, '計画を組み立てる',
                  '全社目標の配賦 / 入力 / レビュー / 承認', 'Plan', size=20)
        self.card(6.8, 2.3, 5.98, 1.82, '前提を比較する',
                  'Optimizer / 統計予測 / シナリオ', 'Plan', BLUE, 20)
        self.card(0.55, 4.4, 5.98, 1.82, '保存結果を確かめる',
                  '書き戻しログとSQLの実データを照合', 'SQL database', BLUE, 20)
        self.card(6.8, 4.4, 5.98, 1.82, '自社の検証条件を決める',
                  '容量 / 課金 / 権限 / PoCの成功条件', 'Workspace', PURPLE, 20)

        self.new('シナリオ', 'Harborlight Provisions の計画業務',
                 f'labs/{LABS[0]}')
        self.card(0.55, 2.32, 3.9, 2.9, '現在の業務',
                  '40枚のExcelシート\n地域が入力 / 本社が集計\n数式と版の整合性が課題', 'Plan', size=20)
        self.card(4.72, 2.32, 3.9, 2.9, '経営陣の目標',
                  'FY25売上: 約$25.9M\nFY26売上目標: $30M\n売上総利益目標: $12.5M', 'Report', BLUE, 22)
        self.card(8.89, 2.32, 3.9, 2.9, '演習で取り組むこと',
                  '目標を明細へ配賦\n現場の前提を調整\n見通しと実績を区別', 'Semantic model', PURPLE, 22)
        self.callout('補足', '架空企業のサンプルです。USD / FYの設定を保ち, 自社データとは区別します。')

        self.new('アーキテクチャ', '実績を参照し, 計画を別の保存先へつなぐ')
        self.flow_node(0.55, 2.25, 3.5, 'Power BI', 'PBIXをインポート\n既存レポートも作成', 'Power BI')
        self.arrow(4.13, 2.93)
        self.flow_node(4.72, 2.25, 3.5, 'Semantic model', '実績 / 業務指標の参照元\n接続先は1つ', 'Semantic model', BLUE)
        self.arrow(8.3, 2.93)
        self.flow_node(8.88, 2.25, 3.9, '主Plan', 'Lab01–06 / 08\nPlanning sheet / Intelligence', 'Plan')
        self.arrow(10.72, 4.0, 0.22, 'down')
        self.text('Writeback', 11.12, 3.99, 1.58, 0.27, 15, GREEN, True)
        self.flow_node(8.88, 4.27, 3.9, 'SQL database',
                       'Lab04のForecastを保存\nPlanのメタデータとは別', 'SQL database', BLUE)
        self.text('後続分析との接続を明示する', 0.65, 4.4, 7.7, 0.45, 24, GREEN, True)
        self.text('SQLテーブルを後続モデルで使う場合は\n接続 / テーブル追加 / 更新を構成',
                  0.65, 5.06, 7.7, 0.85, 21)
        self.callout('重要', '標準のSQL書き戻しだけで, 元モデルや既存レポートが自動更新されるわけではありません。',
                     y=6.08, kind='important')

        self.new('データの意味', '「参照」と「編集可能なコピー」を分ける',
                 f'labs/{LABS[3]}')
        self.card(0.55, 2.35, 5.98, 2.93, 'From Sheets = 参照',
                  '同じPlan内のシートを参照\n参照元の変更を受け取る\n例: Plan Intro → Intelligence', 'Plan', size=23)
        self.card(6.8, 2.35, 5.98, 2.93, 'Copy = 独立した入力',
                  'コピー後は編集可能な系列\n元シートとは自動同期しない\n例: Optimizer用のSales Plan', 'Plan', BLUE, 23)
        self.callout('重要', '実績 / 計画 / Forecastは, 表示名に加え参照元・期間・粒度も確認します。',
                     kind='important')

        self.new('学習経路', 'Lab00–09 の進め方')
        entries = [
            ('00', '事前準備', '15分', 'Fabric'), ('01', '最初のシート', '20分', 'Semantic model'),
            ('02', '配賦と共同作業', '25分', 'Plan'), ('03', 'Optimizer', '15分', 'Plan'),
            ('04', '見通しと書き戻し', '25分', 'SQL database'),
            ('05', '損益とシナリオ', '25分', 'Semantic model'),
            ('06', 'Intelligence', '25分', 'Report'), ('08', '容量とガバナンス', '15分', 'Workspace'),
        ]
        for index, (number, title, minutes, icon) in enumerate(entries):
            x, y = 0.55 + index % 4 * 3.12, 2.25 + index // 4 * 1.42
            self.rect(x, y, 2.88, 1.19, PALE, LINE, True)
            self.icon(icon, x + 0.16, y + 0.16, 0.4)
            self.text(f'Lab{number} / {minutes}', x + 0.7, y + 0.16, 2.04, 0.3, 15, GREEN, True)
            self.text(title, x + 0.16, y + 0.72, 2.58, 0.34, 18, INK, True)
        self.text('任意: Lab07 PowerTable / 30分     発展: Lab09 / 45〜60分 + データ準備',
                  0.65, 5.34, 12.0, 0.5, 22, PURPLE, True)
        self.callout('補足', '基本ルートは165分が目安。集合開催180分は一部を別回へ分け, デモと入力を組み合わせます。',
                     y=6.02)

        self.new('受講準備', '開始前に用意するもの')
        self.card(0.55, 2.3, 5.98, 2.82, '環境とデータ',
                  'Fabric F2以上または試用容量\nEdge / Chrome\n公式 Northwind_FMCG.pbix', 'Fabric', size=23)
        self.card(6.8, 2.3, 5.98, 2.82, '知識と役割',
                  'Excelピボット / 損益の基本\nPower BI の Semantic model\n作成・接続・入力・閲覧の担当を区別', 'Power BI', BLUE, 23)
        self.callout('重要', 'F2は製品上の前提であり, 10〜20名の推奨容量ではありません。Lab09には追加条件があります。',
                     kind='important')

        self.new('費用と安全', 'Planを開く前に, 課金の条件を確認',
                 f'labs/{LABS[0]}', dark=True)
        self.text('セッションは途中で終了できません', 0.65, 2.35, 12.0, 0.62,
                  32, WHITE, True)
        self.text('Planの作成 / 編集 / 閲覧など, 操作に応じて開始・昇格します。\n'
                  '公式例: Plannerの30日間の1セッションは847 CU時間。\n'
                  'Fabric SQL / OneLake / XMLAの消費は別に考慮します。',
                  0.65, 3.35, 11.9, 1.95, 25, WHITE)
        self.slide.notes_slide.notes_text_frame.text += (
            '\n課金単位: 操作で開始するPlannerセッション全体の消費量。'
            '\n公式資料は30日間（730時間）と表記し試算に730時間を使用。暦の30日間は720時間。'
            '\n実際の期限と請求は対象環境の課金情報で確認する。'
        )
        self.callout('注意', '容量の停止やPlanの削除でセッション課金はなくなりません。操作前に管理者と確認します。',
                     kind='warning')

        self.new('Lab00 / 15分', '演習対象と権限を確認する', f'labs/{LABS[0]}')
        self.steps([
            ('演習用Workspace / フォルダー', '本番環境ではないことを確認'),
            ('容量 / Tenant settings / XMLA', '管理者と設定・適用範囲・余力を確認'),
            ('操作別の権限', '接続担当者にはモデルのRead / Build'),
        ], w=6.2)
        self.card(7.25, 2.3, 5.53, 3.16, '最小権限で準備',
                  '作成担当: Member / Admin\n入力・閲覧者には必要な権限のみ\n環境固有の設定を確認', 'Workspace', BLUE, 20)
        self.callout('注意', 'アカウント / Tenant ID / 資格情報 / 顧客データを, 教材・画像・公開ログへ含めません。',
                     kind='warning')

        self.screenshot_slide('Lab01 / 20分', '最初の計画シートを作成する', 1,
            'lab01/28-reloaded-plan-intro.png',
            'Plan Introを保存して再読込したReadingモードの画面例',
            [('PBIXをインポート', 'レポートとモデルを作成'),
             ('Planをモデルへ接続', 'New Planning Sheet'),
             ('フィールドを配置', 'Rows / Columns / Values')],
            '接続済みのモデル名は変更しません。接続先も後から付け替えません。')

        self.screenshot_slide('Lab02 / 25分', '目標の配賦から共同作業へ', 2,
            'lab02/82-comments-status-reloaded.png',
            '販売計画のコメント列とステータスを保存後に確認した画面例',
            [('トップダウンで配賦', '目標額を明細へ展開'),
             ('確定した期間をロック', '残る期間で差額を調整'),
             ('入力 / コメント / 承認', '申請と承認段階を区別')],
            '「2026」の系列名を付けても日付キーは変わりません。この演習では2025年の時間軸を使います。')

        self.screenshot_slide('Lab03 / 15分', 'Optimizerで目標から入力を逆算する', 3,
            'lab03/18-four-series-stable.png',
            '参照元2系列とOptimizer用の編集可能なコピー2系列が並ぶ画面例',
            [('変更可能な入力を用意', 'Sales Plan / COGSをコピー'),
             ('利益の式と目標を指定', 'Gross Profit: $12.5M'),
             ('結果と制約を確認', '目標達成と業務妥当性は別')],
            '売上総利益の達成は, 売上$30Mとの同時達成を意味しません。必要な制約を別に設計します。')

        self.screenshot_slide('Lab04 / 25分', '統計予測からローリング見通しへ', 4,
            'lab04/20-forecast-created-result.png',
            '2024 / 2025の履歴と作成直後のForecastを表示した画面例。予測生成前',
            [('過去24か月を準備', '年度限定なしのGross Revenue'),
             ('Predictで統計予測', '前提・期間・生成結果を確認'),
             ('確定期間を更新', 'Close Period till / 期間延長')],
            '画像は予測生成前です。予測値や行数はデータ・期間・設定に依存する出力例です。',
            'note')

        self.new('Lab04 / 保存', 'ログとSQLの保存値を照合',
                 f'labs/{LABS[4]}')
        self.flow_node(0.55, 2.5, 3.65, 'Forecast', '保存する系列 / 期間\nScenarioを確認', 'Plan')
        self.arrow(4.3, 3.19)
        self.flow_node(4.84, 2.5, 3.65, 'Writeback Logs', '宛先 / 対象操作\n成功・失敗を確認', 'SQL database', BLUE)
        self.arrow(8.59, 3.19)
        self.flow_node(9.12, 2.5, 3.65, 'SQL database', '保存値を同じキーで照合\n件数 / 金額 / 精度', 'SQL database')
        self.text('画面上の値 → 書き戻し設定 → ログ → 保存先の実データ',
                  0.65, 4.65, 12.0, 0.6, 26, GREEN, True)
        self.callout('重要', '元モデルへの自動反映ではありません。履歴の形式と, 現在値を示す条件を確認します。',
                     kind='important')

        self.new('Lab05 / 25分', '損益モデルとシナリオを比較する', f'labs/{LABS[5]}')
        self.card(0.55, 2.32, 5.98, 2.96, '数量加重単価で組み立てる',
                  'Invoice ID / Monthの末端値を照合\n数量の重みで単価を集計\n同じ範囲の元売上と再計算値を比較', 'Semantic model', size=22)
        self.card(6.8, 2.32, 5.98, 2.96, 'Baseとシナリオを比較する',
                  '数量 / 単価 / 費用の前提を変更\n同じ期間・地域・粒度で比較\n保存・再読込後も入力と結果を確認', 'Plan', PURPLE, 22)
        self.callout('注意', '単価の単純平均や月次単価の合計を年次単価にしません。P&L Measuresと別テーブルを混ぜません。',
                     kind='warning')

        self.screenshot_slide('Lab06 / 25分', 'Intelligenceで計画と実績を可視化', 6,
            'lab06/lab06-22-expanded-variance-focus-mode.png',
            '地域と製品カテゴリへ展開した差異グラフのFocus表示の画面例',
            [('Plan Introを埋め込む', '同じPlanのIntelligence内'),
             ('参照元を分けて指定', 'From Sheets / モデル実績'),
             ('差異 / KPIを確認', '同じ地域・製品・期間で比較')],
            '入力を変えて連動するのは, その入力系列を参照するビジュアルです。モデル実績は変わりません。')

        self.new('Lab07 / 任意30分', 'PowerTableは独立した資産台帳の演習',
                 f'labs/{LABS[7]}')
        self.flow_node(0.55, 2.45, 3.65, '公式サンプルXLSX', 'Locations → Employees\n→ Assetsの順で取込み', None)
        self.arrow(4.3, 3.14)
        self.flow_node(4.84, 2.45, 3.65, '別Plan',
                       'PowerTable / 型 / 参照\nフォーム / 承認 / 権限', 'Plan', PURPLE)
        self.arrow(8.59, 3.14)
        self.flow_node(9.12, 2.45, 3.65, '専用SQL database', '主Planの保存先と分離\n既存DBを流用しない', 'SQL database')
        self.text('計画機能だけを体験する場合は, Lab08へ進めます。',
                  0.65, 4.68, 12.0, 0.6, 26, PURPLE, True)
        self.callout('注意', '容量上限に達した場合は管理者へ相談します。既存PlanやDBを削除して空きを作りません。',
                     kind='warning')

        self.new('Lab08 / 15分', '利用人数と実操作 / 負荷を踏まえて考える',
                 f'labs/{LABS[8]}')
        self.card(0.55, 2.3, 3.9, 2.95, '課金と容量',
                  'Planner / Stakeholder / Viewer\n操作とセッションの重なり\n他ワークロードの消費', 'Fabric', size=20)
        self.card(4.72, 2.3, 3.9, 2.95, '性能の検証',
                  '同時利用 / 繁忙時の負荷\nCapacity Metricsを確認\n予算と応答性能を分離', 'OneLake', BLUE, 21)
        self.card(8.89, 2.3, 3.9, 2.95, '権限の検証',
                  'RLSロールを明示割当\n別ユーザーで閲覧範囲を確認\n未割当の動作を仮定しない', 'Workspace', PURPLE, 20)
        self.callout('重要', '容量の計算に収まることと, 同時利用時に必要な性能が出ることは別です。',
                     kind='important')

        self.new('Lab09 / 発展45〜60分', '合成Snapshotで差異分析とData Agentを試す',
                 f'labs/{LABS[9]}')
        self.flow_node(0.55, 2.35, 3.45, 'Lakehouse Files', '同梱の合成CSV / 18行\nProduct × 月', 'Lakehouse')
        self.arrow(4.1, 3.03)
        self.flow_node(4.65, 2.35, 3.7, 'Warehouse', 'COPY INTOで取込み\nDecimalで金額を独立検算', 'Warehouse', BLUE)
        self.arrow(8.45, 3.03)
        self.flow_node(9.0, 2.35, 3.78, '数値を独立照合',
                       'WarehouseのDecimal値\nData Agentの回答と比較', None, BLUE)
        self.arrow(2.1, 4.12, 0.22, 'down')
        self.flow_node(0.55, 4.35, 3.45, 'Lakehouse Delta', 'Spark SQLでテーブル作成\nNotebook / managed Delta', 'Notebook')
        self.arrow(4.1, 5.03)
        self.flow_node(4.65, 4.35, 3.7, 'Ontology Preview', 'Deltaへバインド\nGraph intelligence', 'Graph intelligence', PURPLE)
        self.arrow(8.45, 5.03)
        self.flow_node(9.0, 4.35, 3.78, 'Data Agent', 'Ontology経由で読取専用\n回答をWarehouseで照合', 'Data Agent')
        self.arrow(10.77, 4.12, 0.22, 'up')
        self.text('Filesから2経路: WarehouseへCOPY / Spark SQLでDelta作成',
                  0.65, 6.3, 12.0, 0.45, 20, GREEN, True)

        self.new('Lab09 / 条件と範囲', '発展編は追加条件と確認範囲を守る',
                 f'labs/{LABS[9]}')
        self.card(0.55, 2.3, 5.98, 2.88, '追加の前提条件',
                  '有料F2以上 / Fabric有効化済みP1以上\nTenant AI / クロスジオ / 地域を管理者と確認\nOntology Preview / ソースの読取権限', 'Copilot', size=21)
        self.card(6.8, 2.3, 5.98, 2.88, '確認済みの範囲を区別',
                  '合成CSVによるPart 3–5を実機確認\nData Agentの一部の質問を照合\nQ4 / Q4aはエラーを記録', 'Data Agent', PURPLE, 21)
        self.callout('重要', 'Planや元モデルへの自動書き戻しではありません。成功・失敗を一般化せず, 毎回数値を検算します。',
                     kind='important')

        self.new('自社のPoC', '試す業務と成功条件を具体化する')
        self.card(0.55, 2.3, 5.98, 1.83, '対象業務 / データ',
                  'どの予算・見通しを, どの粒度と頻度で扱うか', 'Semantic model', size=20)
        self.card(6.8, 2.3, 5.98, 1.83, '関係者 / 責任分担',
                  '誰が入力・承認し, 誰がモデルを管理するか', 'Workspace', BLUE, 20)
        self.card(0.55, 4.4, 5.98, 1.83, '照合 / 品質',
                  '保存値・元データ・参照先をどう照合するか', 'SQL database', BLUE, 20)
        self.card(6.8, 4.4, 5.98, 1.83, '費用 / 性能 / 権限',
                  'どの条件を測り, 何をもって合格とするか', 'Fabric', PURPLE, 20)

        self.new('参加方法', '受講するときに使う資料')
        self.steps([
            ('Lab00から順に進める', '指定の演習環境 / 公式サンプルを確認'),
            ('各LabのMarkdownで操作する', '画面・英語のUI名・値を照合'),
            ('HTML操作ガイドを手元で開く', '参加者版 workshop-presentation.htmlを使用'),
        ], w=7.0, gap=1.05)
        self.card(8.25, 2.3, 4.53, 3.2, 'このPowerPointの役割',
                  '目的と流れをつかむ概要資料\n操作の正本はREADME / 各Lab\n環境差があれば推測せず確認', 'Report', BLUE, 20)
        self.callout('ヒント', 'HTMLはダウンロードしてEdge / Chromeで開けます。Fabric操作や外部資料の取得には通信が必要です。',
                     kind='tip')
        self.text('教材を開く', 0.68, 6.86, 2.0, 0.25, 12, BLUE, True, link=REPO)

        self.new('出典 / ライセンス', '教材とアイコンの出典', dark=True)
        self.text('原典 / Lab00–08', 0.65, 2.3, 5.8, 0.45, 23, WHITE, True)
        self.text('Diego Diaz / Fabric Planning Lab\nHarborlight Provisions Co. / MIT License',
                  0.65, 2.95, 6.3, 0.95, 21, WHITE,
                  link='https://github.com/Diaz506/fabric-planning-lab')
        self.text('日本語版 / 追加と修正', 0.65, 4.28, 6.3, 0.45, 23, WHITE, True)
        self.text('Jiayi Yang, Swarm Data SE\nLab09は日本語版独自の発展編',
                  0.65, 4.93, 6.3, 0.95, 21, WHITE)
        self.rect(7.5, 2.25, 5.28, 3.88, WHITE, radius=True)
        self.icon('Fabric', 7.85, 2.6, 0.72)
        self.text('Microsoft Fabric', 8.8, 2.77, 3.6, 0.4, 23, INK, True)
        self.text('公式Fabricアイコン v6.1.0\n教材・スライド用途の利用条件に従い使用\nアイコンの権利はMicrosoftに帰属\n企業ロゴ / Azureアイコンは不使用',
                  7.85, 3.75, 4.55, 1.85, 19, INK,
                  link='https://learn.microsoft.com/en-us/fabric/fundamentals/icons')
        self.text('Microsoft Fabric is a trademark of Microsoft Corporation.',
                  0.65, 6.38, 12.0, 0.32, 13, WHITE)
        self.text('Microsoftによる承認・提携・公式認定を示す資料ではありません。',
                  0.65, 6.78, 12.0, 0.3, 13, WHITE)
        self.slide.notes_slide.notes_text_frame.text += (
            '\nアイコン出典と条件: ' + REPO + '/blob/main/assets/brand/README.md'
            '\n翻訳方針: ' + REPO + '/blob/main/LOCALIZATION.md'
            '\n原典基準コミット: 486be63004b30554ab44a0e3ae654e3e762188ad'
        )

    def save(self):
        payload = io.BytesIO()
        self.prs.save(payload)
        normalized = normalize_package(payload.getvalue())
        errors = font_errors(normalized) + spacing_errors(normalized)
        if errors:
            raise ValueError('\n'.join(errors))
        return normalized


def build(root=ROOT):
    with tempfile.TemporaryDirectory(prefix='fabric-powerpoint-') as scratch:
        deck = Deck(root, scratch)
        deck.populate()
        return deck.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare reproducible output')
    parser.add_argument('--audit-fonts', action='store_true',
                        help='Audit the committed deck with the standard library only')
    args = parser.parse_args()
    destination = ROOT / OUTPUT
    if args.audit_fonts:
        errors = font_errors(destination.read_bytes())
        if errors:
            raise SystemExit('\n'.join(errors))
        print(f'PASS: {destination.name}: Yu Gothic UI across the complete package')
        return
    payload = build()
    if args.check:
        if not destination.is_file() or payload != destination.read_bytes():
            raise SystemExit(f'Stale PowerPoint: run python tools/{Path(__file__).name}')
        print(f'PASS: {destination.name} is current')
    else:
        destination.write_bytes(payload)
        print(f'Wrote {destination}: {len(payload):,} bytes')


if __name__ == '__main__':
    main()
